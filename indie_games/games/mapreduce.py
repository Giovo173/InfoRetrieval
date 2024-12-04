import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample function to process one database
def map_phase(db_path, query_vector, vectorizer):
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

def shuffle_and_sort(results_list):
    combined_results = []
    for results in results_list:
        combined_results.extend(results)

    # Sort by score (descending)
    combined_results.sort(key=lambda x: x[1], reverse=True)
    return combined_results

def perform_query(query, db_paths):
    from nltk.corpus import stopwords
    from sklearn.feature_extraction.text import TfidfVectorizer

    stop_words = set(stopwords.words('english'))
    vectorizer = TfidfVectorizer(stop_words=stop_words)

    # Preprocess the query
    query_vector = vectorizer.fit_transform([query])

    # Map Phase
    results_list = []
    for db_path in db_paths:
        results_list.append(map_phase(db_path, query_vector, vectorizer))

    # Shuffle and Sort Phase
    combined_results = shuffle_and_sort(results_list)

    # Reduce Phase
    final_results = []
    seen_ids = set()
    for game_id, score in combined_results:
        if game_id not in seen_ids:
            final_results.append((game_id, score))
            seen_ids.add(game_id)

    return final_results
