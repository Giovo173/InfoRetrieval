import sqlite3

def store_in_database(games_data, site):
    conn = sqlite3.connect(f'{site}.db')
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {site} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            stemmed_description TEXT,
            tags TEXT,
            url TEXT,
            rating TEXT,
            price TEXT,
            image_path TEXT
        )
    ''')

    if games_data is not None:
        for game in games_data:
            if game:
                c.execute(f'''
                    INSERT INTO {site} (title, description, stemmed_description, tags, url,rating, price, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game['title'], game['description'], game['stemmed_description'], str(game['tags']), game['url'], game['rating'], game['price'], game['image_path']))
        conn.commit()
    conn.close()
