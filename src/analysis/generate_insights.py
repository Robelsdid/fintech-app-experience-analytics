# will generate insights
import pandas as pd
import numpy as np
from collections import Counter
import json

# Load the data
df = pd.read_csv('data/processed/reviews_with_themes.csv')

# Bank name mapping
bank_names = {
    'CBE': 'Commercial Bank of Ethiopia',
    'BOA': 'Bank of Abyssinia', 
    'Dashen': 'Dashen Bank'
}
df['bank_name'] = df['bank'].map(bank_names)

print("=" * 60)
print("FINANCIAL APP EXPERIENCE ANALYTICS - INSIGHTS REPORT")
print("=" * 60)

# 1. OVERALL PERFORMANCE SUMMARY
print("\n OVERALL PERFORMANCE SUMMARY")
print("-" * 40)

total_reviews = len(df)
print(f"Total Reviews Analyzed: {total_reviews:,}")

# Average ratings by bank
avg_ratings = df.groupby('bank_name')['rating'].agg(['mean', 'count']).round(2)
print("\nAverage Ratings by Bank:")
for bank, stats in avg_ratings.iterrows():
    print(f"  {bank}: {stats['mean']} stars ({stats['count']} reviews)")

# Sentiment distribution
sentiment_dist = df['sentiment_label'].value_counts()
print(f"\nOverall Sentiment Distribution:")
for sentiment, count in sentiment_dist.items():
    percentage = (count / total_reviews) * 100
    print(f"  {sentiment}: {count} reviews ({percentage:.1f}%)")

# 2. DRIVERS AND PAIN POINTS ANALYSIS
print("\n DRIVERS AND PAIN POINTS ANALYSIS")
print("-" * 40)

def analyze_bank_performance(bank_code, bank_name):
    """Analyze performance for a specific bank"""
    bank_data = df[df['bank'] == bank_code]
    
    print(f"\n{bank_name} ({bank_code}):")
    print(f"  Total Reviews: {len(bank_data)}")
    print(f"  Average Rating: {bank_data['rating'].mean():.2f} stars")
    print(f"  Average Sentiment Score: {bank_data['sentiment_score'].mean():.3f}")
    
    # Sentiment breakdown
    sentiment_breakdown = bank_data['sentiment_label'].value_counts()
    positive_pct = (sentiment_breakdown.get('POSITIVE', 0) / len(bank_data)) * 100
    print(f"  Positive Reviews: {positive_pct:.1f}%")
    
    # Top themes
    themes = bank_data['identified_theme(s)'].value_counts().head(3)
    print(f"  Top Themes: {', '.join(themes.index.tolist())}")
    
    # Extract keywords for analysis
    all_keywords = []
    for keywords_str in bank_data['keywords'].dropna():
        if isinstance(keywords_str, str):
            try:
                keywords = eval(keywords_str) if keywords_str.startswith('[') else keywords_str.split(', ')
                all_keywords.extend(keywords)
            except:
                continue
    
    # Analyze positive vs negative keywords
    positive_reviews = bank_data[bank_data['sentiment_label'] == 'POSITIVE']
    negative_reviews = bank_data[bank_data['sentiment_label'] == 'NEGATIVE']
    
    positive_keywords = []
    negative_keywords = []
    
    for keywords_str in positive_reviews['keywords'].dropna():
        if isinstance(keywords_str, str):
            try:
                keywords = eval(keywords_str) if keywords_str.startswith('[') else keywords_str.split(', ')
                positive_keywords.extend(keywords)
            except:
                continue
    
    for keywords_str in negative_reviews['keywords'].dropna():
        if isinstance(keywords_str, str):
            try:
                keywords = eval(keywords_str) if keywords_str.startswith('[') else keywords_str.split(', ')
                negative_keywords.extend(keywords)
            except:
                continue
    
    # Top drivers (positive keywords)
    positive_counter = Counter(positive_keywords)
    top_drivers = positive_counter.most_common(3)
    
    # Top pain points (negative keywords)
    negative_counter = Counter(negative_keywords)
    top_pain_points = negative_counter.most_common(3)
    
    print(f"  Top Drivers: {', '.join([kw for kw, _ in top_drivers])}")
    print(f"  Top Pain Points: {', '.join([kw for kw, _ in top_pain_points])}")
    
    return {
        'rating': bank_data['rating'].mean(),
        'sentiment_score': bank_data['sentiment_score'].mean(),
        'positive_pct': positive_pct,
        'top_drivers': top_drivers,
        'top_pain_points': top_pain_points,
        'top_themes': themes.index.tolist()
    }

# Analyze each bank
bank_analyses = {}
for bank_code, bank_name in bank_names.items():
    bank_analyses[bank_code] = analyze_bank_performance(bank_code, bank_name)

# 3. COMPARATIVE ANALYSIS
print("\n COMPARATIVE ANALYSIS")
print("-" * 40)

# Best performing bank by rating
best_rating_bank = max(bank_analyses.items(), key=lambda x: x[1]['rating'])
print(f"Highest Rated Bank: {bank_names[best_rating_bank[0]]} ({best_rating_bank[1]['rating']:.2f} stars)")

# Best performing bank by sentiment
best_sentiment_bank = max(bank_analyses.items(), key=lambda x: x[1]['sentiment_score'])
print(f"Most Positive Sentiment: {bank_names[best_sentiment_bank[0]]} (score: {best_sentiment_bank[1]['sentiment_score']:.3f})")

# Most positive reviews
most_positive_bank = max(bank_analyses.items(), key=lambda x: x[1]['positive_pct'])
print(f"Highest % Positive Reviews: {bank_names[most_positive_bank[0]]} ({most_positive_bank[1]['positive_pct']:.1f}%)")

# 4. RECOMMENDATIONS
print("\n ACTIONABLE RECOMMENDATIONS")
print("-" * 40)

print("\nFor Commercial Bank of Ethiopia (CBE):")
cbe_analysis = bank_analyses['CBE']
if cbe_analysis['rating'] < 4.0:
    print(" Priority: Address low ratings - focus on user experience improvements")
if 'Account Access Issues' in cbe_analysis['top_themes']:
    print(" Priority: Fix login and authentication issues")
if 'Transaction Performance' in cbe_analysis['top_themes']:
    print(" Medium: Optimize transaction processing speed")

print("\nFor Bank of Abyssinia (BOA):")
boa_analysis = bank_analyses['BOA']
if boa_analysis['rating'] < 3.0:
    print(" Critical: Major UX overhaul needed - ratings are very low")
if 'User Interface & Experience' in boa_analysis['top_themes']:
    print(" Priority: Redesign user interface for better usability")
if 'Customer Support' in boa_analysis['top_themes']:
    print(" Medium: Improve customer support response times")

print("\nFor Dashen Bank:")
dashen_analysis = bank_analyses['Dashen']
if dashen_analysis['rating'] < 4.0:
    print(" Medium: Focus on specific pain points to improve ratings")
if 'Feature Requests' in dashen_analysis['top_themes']:
    print(" Opportunity: Consider adding requested features")

# 5. ETHICS CONSIDERATIONS
print("\n ETHICS CONSIDERATIONS")
print("-" * 40)
print("• Review bias: Negative reviews may be overrepresented as dissatisfied users are more likely to leave reviews")
print("• Sample bias: Reviews are from Google Play Store users only, may not represent all customer segments")
print("• Language bias: Analysis focused on English reviews, may miss feedback in local languages")
print("• Temporal bias: Reviews collected at a specific time may not reflect current app performance")

# 6. SAVE INSIGHTS TO FILE
insights_data = {
    'summary': {
        'total_reviews': total_reviews,
        'average_ratings': avg_ratings.to_dict(),
        'sentiment_distribution': sentiment_dist.to_dict()
    },
    'bank_analyses': bank_analyses,
    'recommendations': {
        'cbe': ['Address low ratings', 'Fix login issues'] if cbe_analysis['rating'] < 4.0 else ['Maintain current performance'],
        'boa': ['Major UX overhaul', 'Improve customer support'] if boa_analysis['rating'] < 3.0 else ['Focus on specific improvements'],
        'dashen': ['Address pain points', 'Consider feature requests'] if dashen_analysis['rating'] < 4.0 else ['Maintain and enhance']
    }
}

with open('reports/insights_report.json', 'w') as f:
    json.dump(insights_data, f, indent=2, default=str)

print(f"\n Insights saved to: reports/insights_report.json")
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60) 