import re
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Emotional keywords for categorization
        self.emotion_keywords = {
            'satisfaction': [
                'satisfied', 'pleased', 'content', 'happy', 'delighted', 'thrilled',
                'enjoyed', 'loved', 'amazing', 'wonderful', 'fantastic', 'excellent',
                'perfect', 'great', 'good', 'nice', 'pleasant', 'awesome'
            ],
            'excitement': [
                'excited', 'thrilled', 'energetic', 'pumped', 'enthusiastic',
                'amazing', 'incredible', 'spectacular', 'outstanding', 'brilliant',
                'mind-blowing', 'epic', 'fantastic', 'awesome', 'wow'
            ],
            'disappointment': [
                'disappointed', 'let down', 'underwhelmed', 'expected more',
                'not worth it', 'waste', 'regret', 'poor', 'bad', 'terrible',
                'awful', 'horrible', 'disappointing', 'unsatisfied'
            ],
            'frustration': [
                'frustrated', 'annoyed', 'irritated', 'angry', 'upset',
                'disorganized', 'chaotic', 'confusing', 'poorly managed',
                'unprofessional', 'rude', 'slow', 'delayed', 'crowded'
            ],
            'appreciation': [
                'appreciate', 'grateful', 'thankful', 'thank you', 'thanks',
                'well organized', 'professional', 'helpful', 'friendly',
                'accommodating', 'thoughtful', 'considerate', 'kind'
            ],
            'concern': [
                'concerned', 'worried', 'issue', 'problem', 'trouble',
                'difficulty', 'challenge', 'unclear', 'confusing',
                'needs improvement', 'could be better', 'suggest'
            ]
        }
        
        # Sentiment triggers (words that strongly influence sentiment)
        self.positive_triggers = [
            'amazing', 'excellent', 'fantastic', 'wonderful', 'perfect',
            'outstanding', 'brilliant', 'spectacular', 'incredible', 'awesome',
            'love', 'loved', 'adore', 'enjoy', 'enjoyed', 'delighted',
            'thrilled', 'impressed', 'exceeded expectations'
        ]
        
        self.negative_triggers = [
            'terrible', 'awful', 'horrible', 'worst', 'hate', 'hated',
            'disappointed', 'disappointing', 'waste', 'regret', 'poor',
            'bad', 'unprofessional', 'rude', 'disorganized', 'chaotic'
        ]
        
        # Industry benchmarks (example values)
        self.industry_benchmarks = {
            'average_rating': 4.2,
            'positive_percentage': 75,
            'negative_percentage': 10,
            'response_rate': 35
        }
    
    def analyze_feedback(self, feedback_text, rating=None):
        """
        Comprehensive sentiment analysis of feedback text
        """
        if not feedback_text or not feedback_text.strip():
            return self._create_basic_analysis(rating)
        
        # Clean and prepare text
        cleaned_text = self._clean_text(feedback_text)
        
        # Multiple sentiment analysis approaches
        textblob_analysis = self._textblob_analysis(cleaned_text)
        vader_analysis = self._vader_analysis(cleaned_text)
        
        # Combine analyses for more accurate results
        combined_sentiment = self._combine_sentiment_scores(
            textblob_analysis, vader_analysis, rating
        )
        
        # Extract emotional categories
        emotions = self._extract_emotions(cleaned_text)
        
        # Identify sentiment triggers
        triggers = self._identify_triggers(cleaned_text)
        
        # Calculate confidence level
        confidence = self._calculate_confidence(
            textblob_analysis, vader_analysis, rating, len(cleaned_text.split())
        )
        
        return {
            'sentiment_score': combined_sentiment['score'],
            'sentiment_label': combined_sentiment['label'],
            'confidence': confidence,
            'emotions': emotions,
            'triggers': triggers,
            'textblob_score': textblob_analysis['polarity'],
            'vader_score': vader_analysis['compound'],
            'word_count': len(cleaned_text.split()),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_bulk_feedback(self, feedbacks):
        """
        Analyze multiple feedback entries and provide aggregate insights
        """
        if not feedbacks:
            return self._empty_bulk_analysis()
        
        analyses = []
        for feedback in feedbacks:
            analysis = self.analyze_feedback(
                feedback.get('comments', ''), 
                feedback.get('rating')
            )
            analysis['feedback_id'] = feedback.get('feedback_id')
            analysis['event_id'] = feedback.get('event_id')
            analysis['rating'] = feedback.get('rating')
            analysis['submitted_at'] = feedback.get('submitted_at')
            analyses.append(analysis)
        
        # Aggregate metrics
        aggregate = self._calculate_aggregate_metrics(analyses)
        
        # Trend analysis
        trends = self._analyze_trends(analyses)
        
        # Theme extraction
        themes = self._extract_themes(analyses)
        
        # Actionable insights
        insights = self._generate_insights(aggregate, trends, themes)
        
        return {
            'individual_analyses': analyses,
            'aggregate_metrics': aggregate,
            'trends': trends,
            'themes': themes,
            'insights': insights,
            'industry_comparison': self._compare_to_industry(aggregate)
        }
    
    def _clean_text(self, text):
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep punctuation for sentiment
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    def _textblob_analysis(self, text):
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity
        }
    
    def _vader_analysis(self, text):
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        return scores
    
    def _combine_sentiment_scores(self, textblob, vader, rating=None):
        """Combine multiple sentiment analysis results"""
        # Normalize scores to 0-100 scale
        textblob_score = (textblob['polarity'] + 1) * 50  # -1,1 -> 0,100
        vader_score = (vader['compound'] + 1) * 50  # -1,1 -> 0,100
        
        # Weight the scores
        weights = {'textblob': 0.3, 'vader': 0.4, 'rating': 0.3}
        
        combined_score = (
            textblob_score * weights['textblob'] +
            vader_score * weights['vader']
        )
        
        # Include rating if available
        if rating is not None:
            rating_score = (rating - 1) * 25  # 1-5 -> 0-100
            combined_score = (
                combined_score * (weights['textblob'] + weights['vader']) +
                rating_score * weights['rating']
            )
        
        # Determine sentiment label
        if combined_score >= 70:
            label = 'positive'
        elif combined_score >= 40:
            label = 'neutral'
        else:
            label = 'negative'
        
        return {
            'score': round(combined_score, 1),
            'label': label
        }
    
    def _extract_emotions(self, text):
        """Extract emotional categories from text"""
        emotions = {}
        words = text.split()
        
        for emotion, keywords in self.emotion_keywords.items():
            matches = sum(1 for word in words if any(keyword in word for keyword in keywords))
            emotions[emotion] = {
                'count': matches,
                'intensity': min(matches / len(words) * 100, 100) if words else 0
            }
        
        # Find dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1]['count'])
        
        return {
            'categories': emotions,
            'dominant': dominant[0] if dominant[1]['count'] > 0 else 'neutral'
        }
    
    def _identify_triggers(self, text):
        """Identify words/phrases that strongly influence sentiment"""
        positive_found = []
        negative_found = []
        
        for trigger in self.positive_triggers:
            if trigger in text:
                positive_found.append(trigger)
        
        for trigger in self.negative_triggers:
            if trigger in text:
                negative_found.append(trigger)
        
        return {
            'positive': positive_found,
            'negative': negative_found,
            'total_triggers': len(positive_found) + len(negative_found)
        }
    
    def _calculate_confidence(self, textblob, vader, rating, word_count):
        """Calculate confidence level of sentiment analysis"""
        base_confidence = 50
        
        # Agreement between methods increases confidence
        textblob_sentiment = 'positive' if textblob['polarity'] > 0.1 else 'negative' if textblob['polarity'] < -0.1 else 'neutral'
        vader_sentiment = 'positive' if vader['compound'] > 0.1 else 'negative' if vader['compound'] < -0.1 else 'neutral'
        
        if textblob_sentiment == vader_sentiment:
            base_confidence += 20
        
        # Rating consistency
        if rating:
            rating_sentiment = 'positive' if rating >= 4 else 'negative' if rating <= 2 else 'neutral'
            if rating_sentiment == textblob_sentiment:
                base_confidence += 15
        
        # Text length affects confidence
        if word_count >= 10:
            base_confidence += 10
        elif word_count >= 5:
            base_confidence += 5
        
        # Strong sentiment indicators
        if abs(textblob['polarity']) > 0.5 or abs(vader['compound']) > 0.5:
            base_confidence += 10
        
        return min(base_confidence, 95)
    
    def _calculate_aggregate_metrics(self, analyses):
        """Calculate aggregate sentiment metrics"""
        if not analyses:
            return {}
        
        total_count = len(analyses)
        sentiment_counts = Counter(a['sentiment_label'] for a in analyses)
        
        avg_sentiment_score = np.mean([a['sentiment_score'] for a in analyses])
        avg_confidence = np.mean([a['confidence'] for a in analyses])
        avg_rating = np.mean([a['rating'] for a in analyses if a['rating']])
        
        # Emotion aggregation
        emotion_totals = defaultdict(int)
        for analysis in analyses:
            for emotion, data in analysis['emotions']['categories'].items():
                emotion_totals[emotion] += data['count']
        
        return {
            'total_feedback': total_count,
            'sentiment_distribution': {
                'positive': sentiment_counts.get('positive', 0),
                'neutral': sentiment_counts.get('neutral', 0),
                'negative': sentiment_counts.get('negative', 0),
                'positive_percentage': round(sentiment_counts.get('positive', 0) / total_count * 100, 1),
                'negative_percentage': round(sentiment_counts.get('negative', 0) / total_count * 100, 1)
            },
            'average_sentiment_score': round(avg_sentiment_score, 1),
            'average_confidence': round(avg_confidence, 1),
            'average_rating': round(avg_rating, 1) if avg_rating else None,
            'emotion_summary': dict(emotion_totals),
            'dominant_emotion': max(emotion_totals.items(), key=lambda x: x[1])[0] if emotion_totals else 'neutral'
        }
    
    def _analyze_trends(self, analyses):
        """Analyze sentiment trends over time"""
        if not analyses:
            return {}
        
        # Sort by date
        sorted_analyses = sorted(
            [a for a in analyses if a.get('submitted_at')],
            key=lambda x: x['submitted_at']
        )
        
        if len(sorted_analyses) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend over time
        recent_half = sorted_analyses[len(sorted_analyses)//2:]
        earlier_half = sorted_analyses[:len(sorted_analyses)//2]
        
        recent_avg = np.mean([a['sentiment_score'] for a in recent_half])
        earlier_avg = np.mean([a['sentiment_score'] for a in earlier_half])
        
        trend_direction = 'improving' if recent_avg > earlier_avg else 'declining' if recent_avg < earlier_avg else 'stable'
        trend_magnitude = abs(recent_avg - earlier_avg)
        
        return {
            'trend': trend_direction,
            'magnitude': round(trend_magnitude, 1),
            'recent_average': round(recent_avg, 1),
            'earlier_average': round(earlier_avg, 1),
            'data_points': len(sorted_analyses)
        }
    
    def _extract_themes(self, analyses):
        """Extract common themes from feedback"""
        all_triggers = []
        positive_themes = []
        negative_themes = []
        
        for analysis in analyses:
            all_triggers.extend(analysis['triggers']['positive'])
            all_triggers.extend(analysis['triggers']['negative'])
            positive_themes.extend(analysis['triggers']['positive'])
            negative_themes.extend(analysis['triggers']['negative'])
        
        # Count occurrences
        positive_counter = Counter(positive_themes)
        negative_counter = Counter(negative_themes)
        
        return {
            'top_positive_themes': positive_counter.most_common(5),
            'top_negative_themes': negative_counter.most_common(5),
            'recurring_issues': [theme for theme, count in negative_counter.items() if count >= 2],
            'praise_points': [theme for theme, count in positive_counter.items() if count >= 2]
        }
    
    def _generate_insights(self, aggregate, trends, themes):
        """Generate actionable insights"""
        insights = {
            'urgent_concerns': [],
            'improvement_opportunities': [],
            'strengths': [],
            'recommendations': []
        }
        
        # Urgent concerns (high negative sentiment)
        if aggregate['sentiment_distribution']['negative_percentage'] > 20:
            insights['urgent_concerns'].append({
                'type': 'high_negative_feedback',
                'description': f"{aggregate['sentiment_distribution']['negative_percentage']}% of feedback is negative",
                'priority': 'high'
            })
        
        # Recurring issues
        if themes['recurring_issues']:
            insights['urgent_concerns'].extend([
                {
                    'type': 'recurring_issue',
                    'description': f"Multiple complaints about: {issue}",
                    'priority': 'high'
                } for issue in themes['recurring_issues'][:3]
            ])
        
        # Improvement opportunities
        if trends.get('trend') == 'declining':
            insights['improvement_opportunities'].append({
                'type': 'declining_sentiment',
                'description': f"Sentiment declining by {trends['magnitude']} points",
                'suggestion': 'Review recent changes and address customer concerns'
            })
        
        # Strengths
        if aggregate['sentiment_distribution']['positive_percentage'] > 70:
            insights['strengths'].append({
                'type': 'high_satisfaction',
                'description': f"{aggregate['sentiment_distribution']['positive_percentage']}% positive feedback"
            })
        
        for theme, count in themes['top_positive_themes'][:3]:
            insights['strengths'].append({
                'type': 'praised_aspect',
                'description': f"Customers frequently praise: {theme}"
            })
        
        # Recommendations
        if aggregate['average_sentiment_score'] < 60:
            insights['recommendations'].append(
                "Focus on addressing negative feedback themes to improve overall satisfaction"
            )
        
        if len(themes['top_negative_themes']) > 0:
            insights['recommendations'].append(
                f"Priority improvement area: {themes['top_negative_themes'][0][0]}"
            )
        
        return insights
    
    def _compare_to_industry(self, aggregate):
        """Compare metrics to industry benchmarks"""
        comparison = {}
        
        if aggregate.get('average_rating'):
            comparison['rating_vs_industry'] = {
                'your_rating': aggregate['average_rating'],
                'industry_average': self.industry_benchmarks['average_rating'],
                'performance': 'above' if aggregate['average_rating'] > self.industry_benchmarks['average_rating'] else 'below'
            }
        
        comparison['positive_sentiment_vs_industry'] = {
            'your_percentage': aggregate['sentiment_distribution']['positive_percentage'],
            'industry_average': self.industry_benchmarks['positive_percentage'],
            'performance': 'above' if aggregate['sentiment_distribution']['positive_percentage'] > self.industry_benchmarks['positive_percentage'] else 'below'
        }
        
        return comparison
    
    def _create_basic_analysis(self, rating):
        """Create basic analysis when no text is provided"""
        if rating:
            score = (rating - 1) * 25  # Convert 1-5 to 0-100
            label = 'positive' if rating >= 4 else 'negative' if rating <= 2 else 'neutral'
        else:
            score = 50
            label = 'neutral'
        
        return {
            'sentiment_score': score,
            'sentiment_label': label,
            'confidence': 30,  # Low confidence without text
            'emotions': {'categories': {}, 'dominant': 'neutral'},
            'triggers': {'positive': [], 'negative': [], 'total_triggers': 0},
            'textblob_score': 0,
            'vader_score': 0,
            'word_count': 0,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _empty_bulk_analysis(self):
        """Return empty analysis structure"""
        return {
            'individual_analyses': [],
            'aggregate_metrics': {},
            'trends': {},
            'themes': {},
            'insights': {},
            'industry_comparison': {}
        }

    def generate_word_cloud_data(self, feedbacks):
        """Generate word frequency data for word cloud visualization"""
        all_text = ""
        positive_text = ""
        negative_text = ""
        
        for feedback in feedbacks:
            if feedback.get('comments'):
                text = self._clean_text(feedback['comments'])
                all_text += " " + text
                
                if feedback.get('rating', 3) >= 4:
                    positive_text += " " + text
                elif feedback.get('rating', 3) <= 2:
                    negative_text += " " + text
        
        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        def get_word_freq(text):
            words = [word for word in text.split() if len(word) > 2 and word not in stop_words]
            return Counter(words).most_common(50)
        
        return {
            'all_words': get_word_freq(all_text),
            'positive_words': get_word_freq(positive_text),
            'negative_words': get_word_freq(negative_text)
        }