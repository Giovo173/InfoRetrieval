from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
import time
import random
import sqlite3
from store import store_in_database

# User-Agent headers
HEADERS = {
    'User-Agent': 'YourProjectName/1.0 (contact@example.com)'
}

def get_game_links():
    driver = webdriver.Chrome()
    driver.get("https://itch.io/games/")
    
    game_links = set()  # To store unique game links and images
    game_info = []  # To store the final results (links and image URLs)

    try:
        for _ in range(20):  # Adjust for the number of scrolls you need
            # Find all 'a' elements with the class 'thumb_link game_link'
            games = driver.find_elements(By.CSS_SELECTOR, '.thumb_link.game_link')
            
            for game in games:
                link = game.get_attribute('href')  # Extract the href attribute
                try:
                    img_tag = game.find_element(By.TAG_NAME, 'img')  # Find the <img> element inside the <a> tag
                    img_url = img_tag.get_attribute('src')  # Extract the image URL from the src attribute
                except Exception as e:
                    print(f"Error extracting image URL: {e}")
                    img_url = None

                if link and img_url:  # Ensure both link and image URL are not None
                    print(f"Link: {link}, Image URL: {img_url}")
                    game_info.append({'link': link, 'image_url': img_url})
                    game_links.add(link)
            
            # Scroll down to load more games
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load

    finally:
        driver.quit()

    return game_info  # Return a list of dictionaries with game links and image URLs
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Download NLTK data (run once)
# nltk.download('punkt')
nltk.download('punkt_tab')

import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

def fetch_game_details(url, image_url, image_save_dir="itch_images"):
    try:
        # Create the directory to save images if it doesn't exist
        if not os.path.exists(image_save_dir):
            os.makedirs(image_save_dir)

        # Download the image
        image_filename = os.path.join(image_save_dir, os.path.basename(image_url))
        response = requests.get(image_url, headers=HEADERS, timeout=10)
        with open(image_filename, 'wb') as img_file:
            img_file.write(response.content)

        # Fetch and parse the game's details page
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse game details
        title_element = soup.find('h1', class_='game_title')
        if title_element:
            title = title_element.text.strip()
        else:
            # Take the last part of the URL as the title
            title = url.split('/')[-1].replace('-', ' ')

        description = soup.find('div', class_='formatted_description')
        if description:
            description = description.text.strip()
        else:
            description = "No description available"

        tags = []
        tags_row = soup.find("td", string="Tags")
        if tags_row:
            tags_td = tags_row.find_next_sibling("td")
            tags = [a.text.strip() for a in tags_td.find_all("a")]

        rating_element = soup.find('div', class_='star_value')
        if rating_element and rating_element.get('content'):
            rating = rating_element['content']
        else:
            rating = "No rating"

        price_element = soup.find('span', class_='dollars original_price')
        if price_element:
            price = price_element.text.strip()
        else:
            price = "Free"

        # Stem the description
        ps = PorterStemmer()
        tokens = word_tokenize(description)
        stemmed_description = " ".join(ps.stem(token) for token in tokens)

        # Return the game's details along with the image path
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'stemmed_description': stemmed_description,
            'url': url,
            'rating': rating,
            'price': price,
            'image_path': image_filename
        }
    except Exception as e:
        print(f"Failed to fetch details for {url}: {e}")
        return None

# Main function
def main():
    # Step 1: Collect game links
    print("Collecting game links...")
    links = get_game_links()

    # Step 2: Fetch game details using multithreading
    print("Fetching game details...")
    games_data = []
    for link in links:
        data = fetch_game_details(link.get('link'), link.get('image_url'))
        if data:
            games_data.append(data)
        time.sleep(random.uniform(1, 2))

    # Step 3: Store data in SQLite
    print("Storing data in the database...")
    store_in_database(games_data, 'itchio')
    print("Done!")

if __name__ == "__main__":
    main()
