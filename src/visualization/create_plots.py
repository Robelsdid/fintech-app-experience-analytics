import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from collections import Counter
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Create output directory
output_dir = 'reports/figures'
os.makedirs(output_dir, exist_ok=True)

# Load the data
df = pd.read_csv('data/processed/reviews_with_themes.csv')

# Debug: Check data structure
print("Data shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Sentiment labels:", df['sentiment_label'].unique())
print("Bank names:", df['bank'].unique())

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Bank name mapping for better labels
bank_names = {
    'CBE': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia', 
    'Dashen': 'Dashen Bank'
}
df['bank_name'] = df['bank'].map(bank_names)

# 1. Sentiment Distribution by Bank
plt.figure(figsize=(12, 6))
# Ensure sentiment_label is properly formatted
df['sentiment_label'] = df['sentiment_label'].astype(str)
sentiment_counts = df.groupby(['bank_name', 'sentiment_label']).size().unstack(fill_value=0)
# Convert to numeric if needed
sentiment_counts = sentiment_counts.astype(float)
sentiment_counts.plot(kind='bar', stacked=True)
plt.title('Sentiment Distribution by Bank', fontsize=16, fontweight='bold')
plt.xlabel('Bank', fontsize=12)
plt.ylabel('Number of Reviews', fontsize=12)
plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/sentiment_by_bank.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Rating Distribution by Bank
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='bank_name', y='rating', palette='Set3')
plt.title('Rating Distribution by Bank', fontsize=16, fontweight='bold')
plt.xlabel('Bank', fontsize=12)
plt.ylabel('Rating (1-5 stars)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/rating_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Theme Analysis
plt.figure(figsize=(14, 8))
theme_counts = df['identified_theme(s)'].value_counts().head(10)
theme_counts.plot(kind='barh')
plt.title('Most Common Themes Across All Banks', fontsize=16, fontweight='bold')
plt.xlabel('Number of Reviews', fontsize=12)
plt.ylabel('Theme', fontsize=12)
plt.tight_layout()
plt.savefig(f'{output_dir}/theme_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Sentiment Trends Over Time
plt.figure(figsize=(14, 6))
df['month'] = df['date'].dt.to_period('M')
monthly_sentiment = df.groupby(['month', 'sentiment_label']).size().unstack(fill_value=0)
monthly_sentiment.plot(kind='line', marker='o')
plt.title('Sentiment Trends Over Time', fontsize=16, fontweight='bold')
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Reviews', fontsize=12)
plt.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{output_dir}/sentiment_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Keyword Cloud for each bank
for bank in df['bank'].unique():
    bank_data = df[df['bank'] == bank]
    
    # Extract keywords from the keywords column
    all_keywords = []
    for keywords_str in bank_data['keywords'].dropna():
        if isinstance(keywords_str, str):
            # Convert string representation of list to actual list
            keywords = eval(keywords_str) if keywords_str.startswith('[') else keywords_str.split(', ')
            all_keywords.extend(keywords)
    
    if all_keywords:
        # Create word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                            max_words=50, colormap='viridis').generate(' '.join(all_keywords))
        
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Most Common Keywords - {bank_names[bank]}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/keywords_cloud_{bank.lower()}.png', dpi=300, bbox_inches='tight')
        plt.close()

# 6. Average Sentiment Score by Bank
plt.figure(figsize=(10, 6))
avg_sentiment = df.groupby('bank_name')['sentiment_score'].mean().sort_values(ascending=True)
avg_sentiment.plot(kind='barh', color='skyblue')
plt.title('Average Sentiment Score by Bank', fontsize=16, fontweight='bold')
plt.xlabel('Average Sentiment Score', fontsize=12)
plt.ylabel('Bank', fontsize=12)
plt.tight_layout()
plt.savefig(f'{output_dir}/avg_sentiment_by_bank.png', dpi=300, bbox_inches='tight')
plt.close()

print("All visualizations created successfully!")
print(f" Plots saved in: {output_dir}")
print("\nGenerated plots:")
print("1. sentiment_by_bank.png - Sentiment distribution by bank")
print("2. rating_distribution.png - Rating distribution by bank") 
print("3. theme_analysis.png - Most common themes")
print("4. sentiment_trends.png - Sentiment trends over time")
print("5. keywords_cloud_[bank].png - Keyword clouds for each bank")
print("6. avg_sentiment_by_bank.png - Average sentiment scores") 