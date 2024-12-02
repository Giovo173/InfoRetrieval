from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
import time
import random
import sqlite3

# Proxy list (replace with actual proxies)
PROXIES = [
    'http://proxy1:port',
    'http://proxy2:port',
    'http://proxy3:port'
]

# User-Agent headers
HEADERS = {
    'User-Agent': 'YourProjectName/1.0 (contact@example.com)'
}

def get_game_links():
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    driver.get("https://itch.io/games")
    game_links = set()

    try:
        for _ in range(20):  # Adjust for the number of scrolls you need
            # Find all div elements with the class 'title game_link'
            games = driver.find_elements(By.CSS_SELECTOR, '.title.game_link')
            for game in games:
                link = game.get_attribute('href')  # Extract the href attribute
                print(link)
                if link:  # Ensure the link is not None
                    game_links.add(link)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load
    finally:
        driver.quit()

    return list(game_links)

import nltk
from nltk.tokenize import word_tokenize

# Download NLTK data (run once)
# nltk.download('punkt')
nltk.download('punkt_tab')

def fetch_game_details(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse game details
        title = soup.find('h1').text.strip()
        description_tag = soup.find('div', class_='formatted_description')
        if description_tag:
            description = description_tag.text.strip()
        else:
            description = "No description available"
        # Extract tags from the fifth row of the table
        table = soup.find('div', class_='game_info_panel_widget').find('table')
        rows = table.find_all('tr')
        if len(rows) >= 5:
            tags = [tag.text.strip() for tag in rows[4].find_all('a')]
            print(tags)
        else:
            tags = []

        # Tokenize the description
        tokens = word_tokenize(description)

        return {
            'title': title,
            'description': description,
            'tags': tags,
            'tokenized_description': " ".join(tokens),  # Store tokens as a space-separated string
            'url': url
            #TODO add rating price and source site
        }
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


# Function to store data in SQLite
def store_in_database(games_data):
    with sqlite3.connect('games.db') as conn:
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

        for game in games_data:
            if game:  # Ensure valid data
                c.execute('''
                INSERT INTO games (title, description, tokenized_description, tags, url)
                VALUES (?, ?, ?, ?, ?)''', 
                (game['title'], game['description'], game['tokenized_description'], ','.join(game['tags']), game['url']))

        conn.commit()
# Main function
def main():
    # Step 1: Collect game links
    print("Collecting game links...")
    links = get_game_links()

    # Step 2: Fetch game details using multithreading
    print("Fetching game details...")
    games_data = []
    for link in links:
        data = fetch_game_details(link)
        if data:
            print(data['title'], data['tags'], data['tokenized_description'][:10])
            games_data.append(data)

    # Step 3: Store data in SQLite
    print("Storing data in the database...")
    store_in_database(games_data)
    print("Done!")

if __name__ == "__main__":
    main()
