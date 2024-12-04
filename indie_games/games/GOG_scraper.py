#take the games from https://www.gog.com/en/games?tags=indie&page=1 by scraping only the first 4 pages and store them in the database
import requests
from bs4 import BeautifulSoup
import sqlite3

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Download NLTK data (run once)
# nltk.download('punkt')
nltk.download('punkt_tab')

def scrape(num):
    url = "https://www.gog.com/en/games?tags=indie&page="
    links = []  # Initialize the list to store game links
    for i in range(1, num + 1):
        # Get the page
        url_complete = url + str(i)
        print(f"Scraping: {url_complete}")
        
        response = requests.get(url_complete)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {i}: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the games links
        games = soup.find_all('a', class_="product-tile product-tile--grid")
        print(f"Found {len(links)} games")
        for game in games:
            links.append(game['href'])
            
    ps = PorterStemmer()
    
    for link in links:
        
        try:
            #get the game page
            soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            
            title = soup.find('h1', class_='productcard-basics__title').text
            
            description = soup.find('div', class_="description").text
            
            tokenized_description = word_tokenize(description)
            #stemming
            for i in range(len(tokenized_description)):
                tokenized_description[i] = ps.stem(tokenized_description[i])
            
            
            rating = soup.find('div', class_="rating productcard-rating__score")
            if rating:
                rating = rating.text
            else:
                rating = "No rating"
            print(title)
            print(rating)
            tags = soup.find_all('a', class_="details__link details__link--tag")
            price_div = soup.find('div', class_="product-actions-price")
            price = price_div.find('span', class_="product-actions-price__final-amount _price").text
            print(price, '\n')
            data = {
                'title': title,
                'description': description,
                'stemmed_description': " ".join(tokenized_description),
                'tags': tags,
                'price': price,
                'url': link,
                'rating': rating,
            }
            store_in_database(data)
        except Exception as e:
            print("Error while scraping  ", link, e)
    print("added to database", len(links))
        
    
def store_in_database(games_data):
    conn = sqlite3.connect('GOG.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            tokenized_description TEXT,
            tags TEXT,
            url TEXT
            rating TEXT
            price TEXT
        )
    ''')

scrape(4)