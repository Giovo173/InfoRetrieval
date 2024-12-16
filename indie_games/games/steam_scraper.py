from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup as bs
import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import time
from store import store_in_database

ps = PorterStemmer()

def get_game_links():
    links = []
    options = Options()
    options.headless = False  # Set to False for debugging
    driver = webdriver.Chrome(options=options)
    
    url = 'https://store.steampowered.com/tags/en/Indie/'
    driver.get(url)
    
    try:
        # Accept cookies popup if present
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'acceptAllButton')))
            driver.find_element(By.ID, 'acceptAllButton').click()
            time.sleep(2)
        except Exception as e:
            print("No cookies popup to accept.")
        
        # Scroll and collect game links
        prev_game_count = 0
        max_attempts = 20
        attempts = 0

        while attempts < max_attempts:
            # Scroll down the page
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)  # Allow time for new content to load
            
            # Click "Show More" button if visible
            try:
                show_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, '_2tkiJ4VfEdI9kq1agjZyNz'))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                show_more_button.click()
                time.sleep(2)
            except Exception as e:
                print(f"'Show More' button not found or not clickable: {e}")
                break  # Exit if no button is found

            # Check if new games are loaded
            soup = bs(driver.page_source, 'html.parser')
            games_div = soup.find_all('div', class_='_3rrH9dPdtHVRMzAEw82AId')
            if len(games_div) == prev_game_count:
                print("No new games loaded; stopping.")
                break
            prev_game_count = len(games_div)
            attempts += 1

        # Extract links to individual game pages
        soup = bs(driver.page_source, 'html.parser')
        games_div = soup.find_all('div', class_='_3rrH9dPdtHVRMzAEw82AId')
        for game_div in games_div:
            game_link = game_div.find('a')['href']
            print(game_link)
            links.append(game_link)
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    
    print(f"Total links fetched: {len(links)}")
    return links


def fetch_game_details():
    game_details = []
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    try:
        for l in get_game_links():
            try:
                driver.get(l)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'apphub_AppName')))
                title = retry_find_element(driver, By.ID, 'appHubAppName').text.strip()
                
                try:
                    description = retry_find_element(driver, By.CLASS_NAME, 'game_description_snippet').text.strip()
                except Exception:
                    description = "No description available"
                
                try:
                    tags_section = retry_find_element(driver, By.CLASS_NAME, 'glance_tags')
                    tags_elements = tags_section.find_elements(By.CLASS_NAME, 'app_tag')
                    tags = [tag.text.strip() for tag in tags_elements if tag.get_attribute('style') != 'display: none;']
                except Exception:
                    tags = []

                try:
                    image_url = retry_find_element(driver, By.CLASS_NAME, 'game_header_image_full').get_attribute('src')
                except Exception:
                    image_url = "No image available"

                try:
                    price = retry_find_element(driver, By.CLASS_NAME, 'discount_original_price').text.strip()
                except Exception:
                    try:
                        price = retry_find_element(driver, By.CLASS_NAME, 'game_purchase_price price').text.strip()
                    except Exception:
                        price = "No price available"

                print(f"Title: {title} Description: {description} Price: {price} Tags: {tags} Image URL: {image_url} URL: {l} \n")

                tokens = word_tokenize(description)
                # stemming
                tokens = [ps.stem(token) for token in tokens]

                game_details.append({
                    'title': title,
                    'description': description,
                    'price': price,
                    'tags': tags,
                    'tokenized_description': " ".join(tokens),
                    'image_url': image_url,
                    'url': l
                })
                time.sleep(2)  # To avoid being blocked by the server
            except Exception as e:
                print(f"Failed to fetch details for {l}: {e}, skipping")
                continue
        return game_details
    
    except Exception as e:
        print(f"Failed to fetch game links: {e}")
        return None
    
    finally:
        driver.quit()

def retry_find_element(driver, by, value, retries=3):
    for i in range(retries):
        try:
            element = driver.find_element(by, value)
            return element
        except StaleElementReferenceException:
            if i < retries - 1:
                time.sleep(2)
            else:
                raise
        except Exception as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                raise e


store_in_database(fetch_game_details(), 'steam')
