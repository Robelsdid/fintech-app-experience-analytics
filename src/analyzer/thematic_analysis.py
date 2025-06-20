import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os

# Load spaCy English model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Theme keyword mapping
theme_keywords = {
    'Account Access Issues': ['login', 'password', 'access', 'authentication', 'error'],
    'Transaction Performance': ['transfer', 'transaction', 'delay', 'slow', 'fast', 'processing'],
    'User Interface & Experience': ['ui', 'design', 'navigation', 'easy', 'difficult', 'layout'],
    'Customer Support': ['support', 'help', 'service', 'response', 'contact'],
    'Feature Requests': ['feature', 'add', 'request', 'missing', 'new', 'update']
}

# Preprocessing function
def preprocess(text):
    doc = nlp(str(text).lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return ' '.join(tokens)

# Load sentiment-enriched reviews
input_path = 'data/processed/reviews_with_sentiment.csv'
df = pd.read_csv(input_path)

# Preprocess review text
df['processed_review'] = df['review'].apply(preprocess)

# Extract keywords using TF-IDF
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=1000)
X = vectorizer.fit_transform(df['processed_review'])
feature_names = vectorizer.get_feature_names_out()

# Get top keywords for each review
def get_top_keywords(row_idx, top_n=3):
    row = X[row_idx].toarray().flatten()
    top_indices = row.argsort()[-top_n:][::-1]
    return [feature_names[i] for i in top_indices if row[i] > 0]

df['keywords'] = [get_top_keywords(i) for i in range(len(df))]

# Assign themes based on keywords
def assign_themes(keywords):
    themes = set()
    for theme, kw_list in theme_keywords.items():
        for kw in kw_list:
            if any(re.search(rf'\b{re.escape(kw)}\b', k) for k in keywords):
                themes.add(theme)
    return ', '.join(themes) if themes else 'Other'

df['identified_theme(s)'] = df['keywords'].apply(assign_themes)

# Save results
output_path = 'data/processed/reviews_with_themes.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Thematic analysis complete. Results saved to {output_path}") 