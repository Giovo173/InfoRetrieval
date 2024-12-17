import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download NLTK stopwords if not already downloaded
nltk.download('stopwords')
nltk.download('punkt')
custom_stop_words = ['of', 'to', 'game']
def clean_tags(tags):
    if not tags:
        return []
    # Load default stop words and customize by adding specific terms
    stop_words = set(stopwords.words('english'))
    
    stop_words.update(custom_stop_words)

    # Split tags by common delimiters
    tag_list = re.split(r'[,\s]', tags)
    # Remove empty strings, irrelevant entries, and standardize case
    clean_list = [
        tag.strip().lower()
        for tag in tag_list
        if tag.strip() and tag.strip().lower() not in stop_words and len(tag.strip()) > 1
    ]
    # Remove non-alphanumeric tags
    clean_list = [tag for tag in clean_list if re.match(r'^[a-z0-9\-]+$', tag)]
    return clean_list

# Function to clean and tokenize text descriptions
def clean_and_tokenize(text):
    # Load default stop words and customize by adding specific terms
    stop_words = set(stopwords.words('english'))
    # Add specific words to exclude

    stop_words.update(custom_stop_words)
    
    # Tokenize text
    tokens = word_tokenize(text.lower())
    # Remove stopwords and non-alphanumeric words
    return [word for word in tokens if word.isalnum() and word not in stop_words]

# Function to generate meaningful cluster labels
def get_cluster_labels(df, cluster_column, tags_column, descriptions_column, top_n=3, min_tag_freq=5):
    labels = {}
    for cluster in df[cluster_column].unique():
        cluster_data = df[df[cluster_column] == cluster]

        # Extract and count tags
        all_tags = []
        for tags in cluster_data[tags_column].dropna():
            all_tags.extend(clean_tags(tags))
        most_common_tags = [
            tag for tag, freq in Counter(all_tags).most_common(top_n)
            if freq >= min_tag_freq
        ]

        # Extract and count terms from descriptions
        all_terms = []
        for desc in cluster_data[descriptions_column].dropna():
            all_terms.extend(clean_and_tokenize(desc))
        most_common_terms = [term for term, _ in Counter(all_terms).most_common(top_n)]

        # Combine tags and terms for cluster label
        labels[cluster] = ", ".join(most_common_tags + most_common_terms)
    return labels

# Specify the paths to your .db files
db_table_map = {
    './steam.db': 'steam', 
    './itchio.db': 'itchio',  
    './gog.db': 'gog'  
}

dataframes = []

for path, table_name in db_table_map.items():
    conn = sqlite3.connect(path)
    query = f"SELECT id, title, description, tags, price, image_path FROM {table_name}"
    dataframes.append(pd.read_sql_query(query, conn))
    conn.close()

# Combine data
combined_df = pd.concat(dataframes, ignore_index=True)

# Combine descriptions and tags for better features
combined_df['combined_text'] = (
    combined_df['description'].fillna("") + " " +
    combined_df['tags'].fillna("")
)

# Vectorize combined text
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(combined_df['combined_text'])

# Perform clustering
num_clusters = 10
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
combined_df['cluster'] = kmeans.fit_predict(X)

# Assign cluster labels using tags and description terms
cluster_labels = get_cluster_labels(combined_df, 'cluster', 'tags', 'description')

# Add labels to the DataFrame
combined_df['cluster_label'] = combined_df['cluster'].map(cluster_labels)

# Save to a new SQLite database
conn = sqlite3.connect('clustered_games.sqlite')
combined_df.to_sql('games_with_clusters', conn, if_exists='replace', index=False)
conn.close()


