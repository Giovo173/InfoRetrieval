
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import re

# Function to clean and standardize tags
def clean_tags(tags):
    if not tags:
        return []
    # Split tags by common delimiters (e.g., comma, space)
    tag_list = re.split(r'[,\s]', tags)
    # Remove empty strings and standardize case
    return [tag.strip().lower() for tag in tag_list if tag.strip()]

# Function to generate meaningful cluster labels
def get_cluster_labels(df, cluster_column, tags_column, top_n=2):
    labels = {}
    for cluster in df[cluster_column].unique():
        # Get all tags for the cluster
        cluster_tags = df[df[cluster_column] == cluster][tags_column]
        all_tags = []
        for tags in cluster_tags:
            all_tags.extend(clean_tags(tags))
        # Count occurrences of tags, excluding irrelevant ones
        filtered_tags = [tag for tag in all_tags if tag not in ['indie', '+'] and len(tag) > 1]
        most_common = Counter(filtered_tags).most_common(top_n)
        labels[cluster] = ", ".join([tag for tag, _ in most_common])
    return labels

# Specify the paths to your .db files
db_table_map = {
    './steam.db': 'steam',  # Replace with the correct table name for steam.db
    './itchio.db': 'itchio',  # Replace with the correct table name for itchio.db
}

dataframes = []

for path, table_name in db_table_map.items():
    conn = sqlite3.connect(path)
    query = f"SELECT id, title, description, tags, price, image_path FROM {table_name}"
    dataframes.append(pd.read_sql_query(query, conn))
    conn.close()
    

# Combine data
combined_df = pd.concat(dataframes, ignore_index=True)

# Vectorize descriptions
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(combined_df['description'].fillna(""))

# Perform clustering
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
combined_df['cluster'] = kmeans.fit_predict(X)

# Assign cluster labels
cluster_labels = get_cluster_labels(combined_df, 'cluster', 'tags')

# Add labels to the DataFrame
combined_df['cluster_label'] = combined_df['cluster'].map(cluster_labels)

# Save to a new SQLite database
conn = sqlite3.connect('clustered_games.sqlite')
combined_df.to_sql('games_with_clusters', conn, if_exists='replace', index=False)
conn.close()

# Display preview
print(combined_df[['id', 'title', 'cluster', 'cluster_label']].head())


