#take the games from https://www.indiedb.com/games by scraping only the first 4 pages and store them in the database
from bs4 import BeautifulSoup as bs
import sqlite3
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def get_game_links():
    links = []
    for i in range(1, 5):
        url = f'https://www.indiedb.com/games/page/{i}'
        response = requests.get(url)
        soup = bs(response.content, 'html.parser')
        for game in soup.find_all('div', class_='row'):
            link = game.find('a')['href']
            links.append(link)
    return links

ps = PorterStemmer()

def fetch_game_details():
    game_details = []
    try:
        for l in get_game_links():
            response = requests.get(l)
            soup = bs(response.content, 'html.parser')
            title = soup.find('h2').text.strip()
            description = ' '.join([p.text.strip() for p in soup.find(id='profiledescription').find_all('p')])
            tags = [div.text.strip() for div in soup.find(id='tagsform').find_all('div', class_='row')]

            tokens = word_tokenize(description)
            #stemming
            tokens = [ps.stem(token) for token in tokens]

            game_details.append({
                'title': title,
                'description': description,
                'tags': tags,
                'tokenized_description': " ".join(tokens),
                'url': l
            })
        return game_details
    
    except Exception as e:
        print(f"Failed to fetch {e}")
        return None
