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

ps = PorterStemmer()

def get_game_links():
    links = []
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    url = 'https://store.steampowered.com/tags/en/Indie/'
    driver.get(url)
    try:
        # Accept cookies if the popup appears
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'acceptAllButton')))
            accept_cookies_button = driver.find_element(By.ID, 'acceptAllButton')
            accept_cookies_button.click()
            time.sleep(2)  # Wait for the popup to disappear
        except Exception as e:
            print("No cookies popup to accept.")

        for _ in range(5):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, '_2tkiJ4VfEdI9kq1agjZyNz')))
            show_more_button = driver.find_element(By.CLASS_NAME, '_2tkiJ4VfEdI9kq1agjZyNz')
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            driver.execute_script("window.scrollBy(0, -150);")  # Adjust the scroll position if necessary
            show_more_button.click()
            time.sleep(2)  # To avoid being blocked by the server

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, '_3rrH9dPdtHVRMzAEw82AId')))
        soup = bs(driver.page_source, 'html.parser')
        games_div = soup.find_all('div', class_='_3rrH9dPdtHVRMzAEw82AId')
        for game_div in games_div:
            game_link = game_div.find('a')['href']
            print(game_link)
            links.append(game_link)
        time.sleep(2)  # To avoid being blocked by the server
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

            print(f"Title: {title} Description: {description} Tags: {tags} URL: {l} \n")

            tokens = word_tokenize(description)
            # stemming
            tokens = [ps.stem(token) for token in tokens]

            game_details.append({
                'title': title,
                'description': description,
                'tags': tags,
                'tokenized_description': " ".join(tokens),
                'url': l
            })
            time.sleep(2)  # To avoid being blocked by the server
        return game_details
    
    except Exception as e:
        print(f"Failed to fetch {e}")
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

def store_in_database(games_data):
    conn = sqlite3.connect('Steam.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            tokenized_description TEXT,
            tags TEXT,
            url TEXT
        )
    ''')

    if games_data is not None:
        for game in games_data:
            if game:
                c.execute('''
                    INSERT INTO games (title, description, tokenized_description, tags, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (game['title'], game['description'], game['tokenized_description'], str(game['tags']), game['url']))
        conn.commit()
    conn.close()

store_in_database(fetch_game_details())
