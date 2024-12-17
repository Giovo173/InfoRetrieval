import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import re


# Enhanced function to clean and standardize tags
def clean_tags(tags):
    if not tags:
        return []
    
    # Custom stop words for exclusion
    # Extended stop words list
    stop_words = {
        'indie', 'of', 'the', 'and', 'game', '+', '-', '', 'a', 
        'at', 'is', 'on', 'to', 'in', 'it', 'with', 'for', 'by', 
        'an', 'this', 'that', 'are', 'from', 'player'
    }

    # Split tags by common delimiters
    tag_list = re.split(r'[,\s;|:]+', tags)
    
    # Clean and filter tags
    clean_list = [
        tag.strip().lower()
        for tag in tag_list
        if tag.strip() and len(tag.strip()) > 1 and tag.strip().lower() not in stop_words
    ]
    
    # Keep only alphanumeric or hyphenated tags
    clean_list = [tag for tag in clean_list if re.match(r'^[a-z0-9\-]+$', tag)]
    
    return clean_list


# Function to generate meaningful cluster labels
def get_cluster_labels(df, cluster_column, tags_column, top_n=3):
    labels = {}
    
    for cluster in df[cluster_column].unique():
        # Collect all tags in the current cluster
        cluster_tags = df[df[cluster_column] == cluster][tags_column]
        all_tags = []
        
        # Clean and aggregate tags
        for tags in cluster_tags.dropna():
            all_tags.extend(clean_tags(tags))
        
        # Exclude common irrelevant tags and get the most frequent ones
        most_common = Counter(all_tags).most_common(top_n)
        labels[cluster] = ", ".join([tag for tag, _ in most_common if len(tag) > 1])
    
    return labels


# Specify the paths to your .db files
db_table_map = {
    './steam.db': 'steam',  # Replace with the correct table name for steam.db
    './itchio.db': 'itchio',  # Replace with the correct table name for itchio.db
}

dataframes = []

for path, table_name in db_table_map.items():
    with sqlite3.connect(path) as conn:
        query = f"SELECT id, title, description, stemmed_description, tags, price, image_path FROM {table_name}"
        dataframes.append(pd.read_sql_query(query, conn))
        
# Combine data
combined_df = pd.concat(dataframes, ignore_index=True)
combined_df['combined_text'] = (
    combined_df['stemmed_description'].fillna("") + " " +
    combined_df['tags'].fillna("")
)
from sklearn.feature_extraction.text import TfidfVectorizer

# Custom stop words
custom_stop_words = {'of', 'the', 'and', 'game', 'a', 'is', 'in', 'to', 'at'}

# Vectorize descriptions with additional stop words
vectorizer = TfidfVectorizer(stop_words='english')  # Extend with custom_stop_words if needed
X = vectorizer.fit_transform(combined_df['stemmed_description'].fillna(""))

from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for descriptions
embeddings = np.vstack(combined_df['combined_text'].apply(
    lambda x: model.encode(x if x else "")
).to_numpy())

from sklearn.cluster import AgglomerativeClustering
# Perform clustering
num_clusters = 5
# Perform hierarchical clustering
clustering = AgglomerativeClustering(n_clusters=num_clusters, linkage='ward')
combined_df['cluster'] = clustering.fit_predict(embeddings)




# Assign cluster labels
cluster_labels = get_cluster_labels(combined_df, 'cluster', 'tags')

# Add labels to the DataFrame
combined_df['cluster_label'] = combined_df['cluster'].map(cluster_labels)

# Save to a new SQLite database
with sqlite3.connect('clustered_games.sqlite') as conn:
    combined_df.to_sql('games_with_clusters', conn, if_exists='replace', index=False)

# Display preview
print(combined_df[['id', 'title', 'cluster', 'cluster_label']].head())
