import sqlite3

def store_in_database(games_data, site):
    conn = sqlite3.connect(f'{site}.db')
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {site} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            tokenized_description TEXT,
            tags TEXT,
            url TEXT,
            image_url TEXT,
            price REAL
        )
    ''')

    if games_data is not None:
        for game in games_data:
            if game:
                c.execute(f'''
                    INSERT INTO {site} (title, description, tokenized_description, tags, url, image_url, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (game['title'], game['description'], game['tokenized_description'], str(game['tags']), game['url'], game['image_url'], game['price']))
        conn.commit()
    conn.close()