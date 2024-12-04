import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor

def process_database(db_path, query_vector, vectorizer):
    """Process a single database to calculate similarity scores."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch titles, tags, and descriptions
    cursor.execute("SELECT id, title, tags, description FROM games")
    games = cursor.fetchall()

    # Combine text fields and compute TF-IDF
    corpus = [f"{title} {tags} {description}" for _, title, tags, description in games]
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Emit results as a list of tuples (game_id, score)
    results = [(game[0], score) for game, score in zip(games, scores)]
    conn.close()
    return results

def query_databases(query, db_paths):
    """Use multithreading to query multiple databases simultaneously."""
    # Preprocess the query
    vectorizer = TfidfVectorizer(stop_words='english')
    query_vector = vectorizer.fit_transform([query])

    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_database, db_path, query_vector, vectorizer) for db_path in db_paths]

        # Collect results from all threads
        results_list = [future.result() for future in futures]

    return results_list


def shuffle_and_sort(results_list):
    """Combine and sort results from all databases."""
    combined_results = []
    for results in results_list:
        combined_results.extend(results)

    # Sort by score (descending)
    combined_results.sort(key=lambda x: x[1], reverse=True)
    return combined_results


def reduce_phase(combined_results):
    """Deduplicate results and finalize the ranked list."""
    final_results = []
    seen_ids = set()

    for game_id, score in combined_results:
        if game_id not in seen_ids:
            final_results.append((game_id, score))
            seen_ids.add(game_id)

    return final_results



def search_games(query, db_paths):
    # Map Phase: Query databases in parallel
    results_list = query_databases(query, db_paths)

    # Shuffle and Sort Phase: Combine and sort results
    combined_results = shuffle_and_sort(results_list)

    # Reduce Phase: Deduplicate and finalize results
    final_results = reduce_phase(combined_results)

    return final_results
