import pandas as pd
from transformers import pipeline

# Load cleaned reviews
input_path = 'data/processed/cleaned_reviews.csv'
df = pd.read_csv(input_path)

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Run sentiment analysis
results = sentiment_pipeline(df['review'].astype(str).tolist(), truncation=True)

# Add results to DataFrame
sentiment_labels = [r['label'] for r in results]
sentiment_scores = [r['score'] for r in results]
df['sentiment_label'] = sentiment_labels
df['sentiment_score'] = sentiment_scores

# Save enriched data
output_path = 'data/processed/reviews_with_sentiment.csv'
df.to_csv(output_path, index=False)

print(f"Sentiment analysis complete. Results saved to {output_path}") 