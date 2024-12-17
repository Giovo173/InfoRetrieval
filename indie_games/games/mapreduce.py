import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor

def process_database(db_path, query_vector, vectorizer, table_name):
    """Process a single database to calculate similarity scores."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch game details, including stemmed descriptions
    cursor.execute(f"SELECT id, title, tags, stemmed_description FROM {table_name}")
    games = cursor.fetchall()

    # Combine text fields (use stemmed_description instead of description)
    corpus = [f"{title} {tags} {stemmed_description}" for _, title, tags, stemmed_description in games]
    tfidf_matrix = vectorizer.transform(corpus)  # Use transform, not fit_transform

    # Calculate cosine similarity
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Return results with full game details
    results = [
        {
            "db_path": db_path,
            "game_id": game[0],
            "title": game[1],
            "description": game[2],
            "tags": game[3],  # Corrected index for tags
            "score": score
        }
        for game, score in zip(games, scores)
    ]
    conn.close()
    
    return results

def query_databases(query, db_paths, vectorizer):
    """Use multithreading to query multiple databases simultaneously."""
    # Transform query text using the fitted vectorizer
    query_vector = vectorizer.transform([query])

    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_database, db_path, query_vector, vectorizer, table_name) for db_path, table_name in db_paths]

        # Collect results from all threads
        results_list = [future.result() for future in futures]

    return results_list

def shuffle_and_sort(results_list):
    """Combine and sort results from all databases."""
    combined_results = []
    for results in results_list:
        combined_results.extend(results)

    # Sort by score (descending)
    combined_results.sort(key=lambda x: x["score"], reverse=True)
    return combined_results

def reduce_phase(combined_results):
    """Keep all results without deduplication."""
    # Simply return the combined results
    return combined_results

def search_games(query, db_paths):
    # Fit a global vectorizer
    global_corpus = []
    for db_path, table_name in db_paths:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT title, tags, stemmed_description FROM {table_name}")
        global_corpus.extend([f"{title} {tags} {stemmed_description}" for title, tags, stemmed_description in cursor.fetchall()])
        conn.close()

    vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer.fit(global_corpus)

    # Map Phase: Query databases in parallel
    results_list = query_databases(query, db_paths, vectorizer)

    # Shuffle and Sort Phase: Combine and sort results
    combined_results = shuffle_and_sort(results_list)

    # Reduce Phase: Deduplicate and finalize results
    final_results = reduce_phase(combined_results)

    return final_results

# Example usage
results = search_games("indie platformer", [('./steam.db', 'steam'), ('./itchio.db', 'itchio')])
print(results)
