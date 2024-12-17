#take the games from https://www.gog.com/en/games?tags=indie&page=1 by scraping only the first 4 pages and store them in the database
import requests
from bs4 import BeautifulSoup
import sqlite3
from store import store_in_database
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import os
import requests
import time
# Download NLTK data (run once)
# nltk.download('punkt')
nltk.download('punkt_tab')

import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}


def scrape(num):
    url = "https://www.gog.com/en/games?tags=indie&page="
    links = []  # Initialize the list to store game links and image URLs
    for i in range(1, num + 1):
        # Get the page
        url_complete = url + str(i)
        print(f"Scraping: {url_complete}")
        
        response = requests.get(url_complete)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {i}: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the games links and images
        games = soup.find_all('a', class_="product-tile product-tile--grid")
        print(f"Found {len(games)} games on page {i}")
        
        for game in games:
            link = game['href']
            
            # Find the <picture> tag
            picture_tag = game.find('picture')
            if picture_tag:
                # Find the first <source> tag with a 'srcset' attribute
                source_tag = picture_tag.find('source', {'srcset': True})
                if source_tag and 'srcset' in source_tag.attrs:
                    # Extract the first image URL from the 'srcset' attribute
                    srcset = source_tag['srcset']
                    image_url = srcset.split(',')[0].strip().split(' ')[0]
                else:
                    image_url = None  # Fallback if no image is found
            else:
                image_url = None  # Fallback if no picture tag is found
            
            if image_url:
                links.append((link, image_url))
    
    ps = PorterStemmer()
    data_all = []
    for link, image_url in links:
        
        try:
            try:
                req = requests.get(link)
                
                if req.status_code != 200:
                    print(f"Failed to fetch game")
                    continue
                
                # Get the game page
                soup = BeautifulSoup(req.content, 'html.parser')
            except Exception as e:
                print("Error while fetching ", link, e)
                continue
            
            try:
                # Create the directory to save images if it doesn't exist
                image_save_dir = "gog_images"
                if not os.path.exists(image_save_dir):
                    os.makedirs(image_save_dir)

                # Download the image
                image_filename = os.path.join(image_save_dir, os.path.basename(image_url))
                response = requests.get(image_url, headers=HEADERS, timeout=10)
                with open(image_filename, 'wb') as img_file:
                    img_file.write(response.content)
                title = soup.find('h1', class_='productcard-basics__title').text
            except Exception as e:
                print("Error while fetching image ", image_url, e)
                continue
            try:    
                description = soup.find('div', class_="description").text
                
                tokenized_description = word_tokenize(description)
                # Stemming
                for i in range(len(tokenized_description)):
                    tokenized_description[i] = ps.stem(tokenized_description[i])
                    
            except Exception as e:
                print("Error while fetching description ", link, e)
                continue
            
            try:
                rating = soup.find('div', class_="rating productcard-rating__score")
                if rating:
                    rating = rating.text
                else:
                    rating = "No rating"
            except Exception as e:
                print("Error while fetching rating ", link, e)
                continue    
            print(title)
            print(rating)
            try:
                tags = [tag.text for tag in soup.find_all('a', class_="details__link details__link--tag")]
                price_div = soup.find('div', class_="product-actions-price")
                price = price_div.find('span', class_="product-actions-price__final-amount _price").text
            except Exception as e:
                print("Error while fetching tags ", link, e)
                continue    
            print(price, '\n')
            data = {
                'title': title,
                'description': description,
                'stemmed_description': " ".join(tokenized_description),
                'tags': tags,
                'price': price,
                'rating': rating,
                'url': link,
                'image_path': image_filename,
            }
            data_all.append(data)
        except Exception as e:
            print("Error while scraping ", link, e)
        time.sleep(1)

    store_in_database(data_all, 'gog')
    print("Added to database", len(data_all))




scrape(20)