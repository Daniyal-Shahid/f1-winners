import feedparser
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from functools import lru_cache
import time
import requests

class F1SentimentAnalyzer:
    # Class-level cache
    _articles_cache = {}
    _cache_timestamp = None
    _cache_duration = timedelta(minutes=60)  # Cache for 1 hour

    def __init__(self):
        # Extended list of reliable F1 RSS feeds
        self.rss_feeds = {
            'formula1': 'https://www.formula1.com/content/fom-website/en/latest/all.xml',
            'autosport': 'https://www.autosport.com/rss/f1/news/',
            'motorsport': 'https://www.motorsport.com/rss/f1/news/',
            'BBC': 'https://www.bbc.co.uk/sport/formula1/rss.xml',
            'TheGuardian': 'https://www.theguardian.com/sport/formulaone/rss',
            'racefans': 'https://www.racefans.net/feed/',
            'crash': 'https://www.crash.net/rss/f1',
            'gpblog': 'https://www.gpblog.com/en/rss',
            'racingnews365': 'https://racingnews365.com/feed/news.xml',
            'f1i': 'https://f1i.com/feed',
            'thecheckeredflag': 'https://www.thecheckeredflag.co.uk/feed/',
            'wtf1': 'https://wtf1.com/feed',
            'GPToday': 'https://feeds.feedburner.com/totalf1-recent',
            'NewsonF1': 'https://www.newsonf1.com/feed',
            'Grandprix.com': 'https://www.grandprix.com/rss.xml',
        }
        
        self._refresh_cache_if_needed()

    def _refresh_cache_if_needed(self):
        """Check if cache needs refreshing and update if necessary"""
        current_time = datetime.now()
        if (self._cache_timestamp is None or 
            current_time - self._cache_timestamp > self._cache_duration):
            self._articles_cache = {}
            for source, feed_url in self.rss_feeds.items():
                self._articles_cache[source] = self._fetch_feed(feed_url)
            self._cache_timestamp = current_time

    @lru_cache(maxsize=100)
    def _fetch_feed(self, feed_url: str) -> List[Dict]:
        """Fetch and parse RSS feed with caching"""
        try:
            # Add User-Agent header to avoid being blocked
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Use requests to get the feed content first
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the feed content
            feed = feedparser.parse(response.content)
            
            # Log feed status
            if hasattr(feed, 'status'):
                logging.info(f"Feed {feed_url} status: {feed.status}")
            
            if not feed.entries:
                logging.warning(f"No entries found in feed: {feed_url}")
                return []
            
            articles = []
            for entry in feed.entries:
                # Extract content from either description or content field
                content = ''
                if 'content' in entry:
                    content = entry.content[0].value
                elif 'description' in entry:
                    content = entry.description
                elif 'summary' in entry:
                    content = entry.summary
                
                articles.append({
                    'title': entry.get('title', ''),
                    'description': content,
                    'published': entry.get('published', entry.get('updated', '')),
                    'source': feed_url
                })
            
            logging.info(f"Successfully fetched {len(articles)} articles from {feed_url}")
            return articles
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error fetching feed {feed_url}: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error fetching feed {feed_url}: {str(e)}")
            return []

    def _analyze_sentiment(self, texts: List[str], articles: List[Dict] = None) -> Dict:
        """Analyze sentiment of given texts"""
        sentiments = []
        article_sentiments = []  # Track sentiment for each article
        
        for i, text in enumerate(texts):
            try:
                analysis = TextBlob(text)
                sentiment = {
                    'polarity': analysis.sentiment.polarity,
                    'subjectivity': analysis.sentiment.subjectivity
                }
                sentiments.append(sentiment)
                
                # If articles are provided, attach sentiment to each article
                if articles:
                    article_sentiments.append({
                        **articles[i],
                        'sentiment': sentiment['polarity']
                    })
                
            except Exception as e:
                logging.error(f"Error analyzing text: {str(e)}")
                continue
            
        if not sentiments:
            return None
            
        df = pd.DataFrame(sentiments)
        
        # Use consistent thresholds for sentiment categorization
        positive_threshold = 0.05
        negative_threshold = -0.05
        
        positive_count = len([s for s in df['polarity'] if s > positive_threshold])
        negative_count = len([s for s in df['polarity'] if s < negative_threshold])
        neutral_count = len([s for s in df['polarity'] if negative_threshold <= s <= positive_threshold])
        total_count = len(df['polarity'])
        
        result = {
            'average_sentiment': float(df['polarity'].mean()),
            'sentiment_std': float(df['polarity'].std()),
            'average_subjectivity': float(df['subjectivity'].mean()),
            'sample_size': len(texts),
            'sentiment_distribution': {
                'positive': positive_count / total_count,
                'neutral': neutral_count / total_count,
                'negative': negative_count / total_count
            }
        }
        
        # Add categorized articles if available
        if article_sentiments:
            result.update({
                'positive_articles': [a for a in article_sentiments if a['sentiment'] > positive_threshold],
                'neutral_articles': [a for a in article_sentiments if negative_threshold <= a['sentiment'] <= positive_threshold],
                'negative_articles': [a for a in article_sentiments if a['sentiment'] < negative_threshold]
            })
        
        return result

    def get_driver_sentiment(self, driver_name: str, days: int = 7) -> Dict:
        """Get sentiment analysis for a specific driver from news sources"""
        self._refresh_cache_if_needed()
        
        all_articles = []
        driver_articles = []
        article_texts = []
        since_date = datetime.now() - timedelta(days=days)
        
        driver_last_name = driver_name.split()[-1]
        
        # Use cached articles instead of fetching
        for source, articles in self._articles_cache.items():
            all_articles.extend(articles)
        
        # Filter articles mentioning either full name or last name
        for article in all_articles:
            content = f"{article['title']} {article['description']}"
            if (driver_name.lower() in content.lower() or 
                driver_last_name.lower() in content.lower()):
                driver_articles.append({
                    'title': article['title'],
                    'source': article.get('source', 'Unknown'),
                    'published': article.get('published', '')
                })
                article_texts.append(content)
        
        if not driver_articles:
            return None
        
        sentiment_results = self._analyze_sentiment(article_texts, driver_articles)
        if sentiment_results:
            sentiment_results['articles_analyzed'] = len(driver_articles)
            sentiment_results['time_period'] = f"Last {days} days"
            
        return sentiment_results

    def get_team_sentiment(self, team_name: str, days: int = 7) -> Dict:
        """Get sentiment analysis for a specific team from news sources"""
        return self.get_driver_sentiment(team_name, days)  # Reuse the same logic

    def get_latest_headlines(self, query: str = None, limit: int = 5) -> List[Dict]:
        """Get latest F1 headlines, optionally filtered by query"""
        self._refresh_cache_if_needed()
        
        all_headlines = []
        seen_titles = set()  # Track unique titles
        
        # Use cached articles instead of fetching
        for source, articles in self._articles_cache.items():
            for article in articles:
                title = article['title'].lower()  # Convert to lowercase for comparison
                if query is None or query.lower() in title:
                    # Only add if we haven't seen this title before
                    if title not in seen_titles:
                        seen_titles.add(title)
                        all_headlines.append({
                            'title': article['title'],  # Keep original case for display
                            'source': source,
                            'published': article['published']
                        })
        
        # Sort by published date and limit results
        return sorted(
            all_headlines,
            key=lambda x: x['published'],
            reverse=True
        )[:limit]

    def get_driver_sentiment_details(self, driver_name: str, days: int = 7) -> Dict:
        """Get detailed sentiment analysis for a specific driver including all articles"""
        self._refresh_cache_if_needed()
        
        all_articles = []
        driver_articles = []
        article_texts = []
        
        driver_last_name = driver_name.split()[-1]
        
        # Use cached articles instead of fetching
        for source, articles in self._articles_cache.items():
            for article in articles:
                content = f"{article['title']} {article['description']}"
                if (driver_name.lower() in content.lower() or 
                    driver_last_name.lower() in content.lower()):
                    # Create a clean article object
                    clean_article = {
                        'title': article['title'],
                        'description': article['description'],
                        'source': source,
                        'published': article['published']
                    }
                    driver_articles.append(clean_article)
                    article_texts.append(content)
        
        if not driver_articles:
            return {
                'driver': driver_name,
                'articles_analyzed': 0,
                'message': 'No articles found for analysis'
            }
        
        sentiment_results = self._analyze_sentiment(article_texts, driver_articles)
        if sentiment_results:
            sentiment_results['driver'] = driver_name
            sentiment_results['articles_analyzed'] = len(driver_articles)
            sentiment_results['time_period'] = f"Last {days} days"
            
            # Sort articles by absolute sentiment value
            for category in ['positive_articles', 'neutral_articles', 'negative_articles']:
                if category in sentiment_results:
                    sentiment_results[category] = sorted(
                        sentiment_results[category],
                        key=lambda x: abs(x['sentiment']),
                        reverse=True
                    )[:10]  # Limit to top 10 articles per category
            
            # Don't recalculate distribution here - use the one from _analyze_sentiment
            
        return sentiment_results

if __name__ == "__main__":
    # Initialize the analyzer
    analyzer = F1SentimentAnalyzer()
    
    # Test drivers to analyze
    test_drivers = ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc"]
    
    print("\n=== Testing F1 Sentiment Analyzer ===\n")
    
    # Test RSS feeds
    print("1. Testing RSS Feeds:")
    print("-----------------------")
    for source, feed_url in analyzer.rss_feeds.items():
        articles = analyzer._fetch_feed(feed_url)
        print(f"{source}: Found {len(articles)} articles")
        if articles:
            print(f"Sample headline: {articles[0]['title']}\n")
    
    # Test driver sentiment analysis
    print("\n2. Testing Driver Sentiment Analysis:")
    print("----------------------------------")
    for driver in test_drivers:
        print(f"\nAnalyzing {driver}:")
        sentiment = analyzer.get_driver_sentiment(driver, days=7)
        
        if sentiment:
            print(f"✓ Articles analyzed: {sentiment['articles_analyzed']}")
            print(f"✓ Average sentiment: {sentiment['average_sentiment']:.2f}")
            print(f"✓ Sentiment distribution:")
            print(f"  - Positive: {sentiment['sentiment_distribution']['positive']*100:.1f}%")
            print(f"  - Neutral: {sentiment['sentiment_distribution']['neutral']*100:.1f}%")
            print(f"  - Negative: {sentiment['sentiment_distribution']['negative']*100:.1f}%")
        else:
            print("✗ No articles found for analysis")
    
    # Test headlines retrieval
    print("\n3. Testing Headlines Retrieval:")
    print("-----------------------------")
    headlines = analyzer.get_latest_headlines(limit=3)
    if headlines:
        print("Latest F1 Headlines:")
        for idx, headline in enumerate(headlines, 1):
            print(f"{idx}. {headline['title']} (from {headline['source']})")
    else:
        print("No headlines found")
