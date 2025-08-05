from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TopicGenerator:
    """Advanced topic generation using multiple ML techniques"""
    
    def __init__(self):
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'study', 'research', 'paper', 'article', 'analysis', 'using', 'based'
        ])
    
    def _preprocess_text(self, text):
        """Preprocess text for topic modeling"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_keywords(self, texts, n_keywords=20):
        """Extract keywords using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top keywords
            top_indices = mean_scores.argsort()[-n_keywords:][::-1]
            keywords = [feature_names[i] for i in top_indices]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _cluster_based_topics(self, texts, n_topics=5):
        """Generate topics using K-means clustering"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            if tfidf_matrix.shape[0] < n_topics:
                n_topics = max(1, tfidf_matrix.shape[0])
            
            kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for i in range(n_topics):
                # Get cluster center
                center = kmeans.cluster_centers_[i]
                
                # Get top terms for this cluster
                top_indices = center.argsort()[-10:][::-1]
                top_terms = [feature_names[idx] for idx in top_indices]
                
                # Create topic description
                topic = {
                    'id': i,
                    'terms': top_terms[:5],
                    'description': f"Research focusing on {', '.join(top_terms[:3])}"
                }
                topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error in cluster-based topic generation: {e}")
            return []
    
    def _lda_based_topics(self, texts, n_topics=5):
        """Generate topics using Latent Dirichlet Allocation"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            if tfidf_matrix.shape[0] < n_topics:
                n_topics = max(1, tfidf_matrix.shape[0])
            
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10
            )
            
            lda.fit(tfidf_matrix)
            feature_names = vectorizer.get_feature_names_out()
            
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-10:][::-1]
                top_terms = [feature_names[i] for i in top_indices]
                
                topic_desc = {
                    'id': topic_idx,
                    'terms': top_terms[:5],
                    'description': f"Investigation of {', '.join(top_terms[:3])}"
                }
                topics.append(topic_desc)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error in LDA-based topic generation: {e}")
            return []
    
    def _generate_research_questions(self, keywords, topics):
        """Generate potential research questions"""
        questions = []
        
        # Question templates
        templates = [
            "How does {} impact {} in the context of {}?",
            "What are the effects of {} on {} performance?",
            "Can {} be used to improve {} systems?",
            "What is the relationship between {} and {} in {}?",
            "How can {} techniques enhance {} applications?",
            "What are the challenges of implementing {} in {}?",
            "How do {} methods compare to traditional {} approaches?",
            "What factors influence {} adoption in {} environments?"
        ]
        
        # Generate questions using top keywords
        for template in templates[:4]:  # Limit to avoid too many questions
            if len(keywords) >= 3:
                try:
                    question = template.format(
                        keywords[0], 
                        keywords[1] if len(keywords) > 1 else 'system',
                        keywords[2] if len(keywords) > 2 else 'modern applications'
                    )
                    questions.append(question)
                except:
                    continue
        
        return questions[:5]  # Return top 5 questions
    
    def generate_topics(self, papers, n_topics=5):
        """
        Generate comprehensive research topics from papers
        
        Args:
            papers (list): List of paper dictionaries with 'title' and 'snippet'
            n_topics (int): Number of topics to generate
            
        Returns:
            dict: Dictionary containing various topic suggestions
        """
        logger.info(f"Generating topics from {len(papers)} papers")
        
        if not papers:
            return {'error': 'No papers provided'}
        
        try:
            # Combine text from papers
            texts = []
            for paper in papers:
                combined_text = f"{paper.get('title', '')} {paper.get('snippet', '')}"
                processed_text = self._preprocess_text(combined_text)
                if processed_text.strip():
                    texts.append(processed_text)
            
            if not texts:
                return {'error': 'No valid text found in papers'}
            
            # Extract keywords
            keywords = self._extract_keywords(texts)
            
            # Generate topics using different methods
            cluster_topics = self._cluster_based_topics(texts, n_topics)
            lda_topics = self._lda_based_topics(texts, n_topics)
            
            # Generate research questions
            research_questions = self._generate_research_questions(keywords, cluster_topics)
            
            # Create comprehensive output
            result = {
                'keywords': keywords[:15],
                'cluster_based_topics': cluster_topics,
                'lda_based_topics': lda_topics,
                'research_questions': research_questions,
                'summary': {
                    'total_papers': len(papers),
                    'text_sources': len(texts),
                    'top_keywords': keywords[:5],
                    'main_themes': [topic['terms'][:3] for topic in cluster_topics[:3]]
                }
            }
            
            logger.info("Successfully generated topics")
            return result
            
        except Exception as e:
            logger.error(f"Error generating topics: {e}")
            return {'error': str(e)}
