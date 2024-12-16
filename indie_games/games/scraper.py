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
from nltk.stem import PorterStemmer

# Download NLTK data (run once)
# nltk.download('punkt')
nltk.download('punkt_tab')

def fetch_game_details(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse game details
        title_element = soup.find('h1', class_='game_title')
        if title_element:
            title = title_element.text.strip()
        else:
            title = url.split('/')[-1]  # Take the last part of the URL as the title
            #replace the - with a space
            title = title.replace('-', ' ')
        description = soup.find('div', class_='formatted_description')
        if description:
            description = description.text
        else:
            description = "No description available"
            
        tags = []
        game_info_panel = soup.find('div', class_='game_info_panel_widget base_widget')
        # Find the 'Tags' row
        tags_row = soup.find("td", text="Tags")

        # Extract all the tags (anchor elements) in the next <td>
        if tags_row:
            tags_td = tags_row.find_next_sibling("td")
            tags = [a.text.strip() for a in tags_td.find_all("a")]

            print("Extracted Tags:", tags)
        else:
            print("Tags row not found.")
        
        #take the title of the div "aggragate rating to have the rating"
        rating = soup.find('div', class_='aggragate_rating')
        if rating:
            rating = rating.find('title').text
        else:
            rating = "No rating available"
        
        
        price = soup.find('span', class_='dollars original_price')
        if price:
            price = price.text
        else:
            price = "Free"
            
        ps = PorterStemmer()
        # Tokenize the description
        tokens = word_tokenize(description)
        for i in range(len(tokens)):
            tokens[i] = ps.stem(tokens[i])
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'stemmed_description': " ".join(tokens),  # Store tokens as a space-separated string
            'url': url,
            'rating': rating,
            'price': price,
        }
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
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
        data = fetch_game_details(link)
        if data:
            print(data['title'], data['tags'], data['stemmed_description'][:10])
            games_data.append(data)

    # Step 3: Store data in SQLite
    print("Storing data in the database...")
    store_in_database(games_data, 'itchio')
    print("Done!")

if __name__ == "__main__":
    main()
