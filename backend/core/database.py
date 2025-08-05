import sqlite3
import json
import os
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """SQLite database for caching and storing research data"""
    
    def __init__(self, db_path="../data/research_assistant.db"):
        self.db_path = db_path
        self.ensure_db_directory()
    
    def ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Search cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS search_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_hash TEXT UNIQUE NOT NULL,
                        query TEXT NOT NULL,
                        max_results INTEGER NOT NULL,
                        results TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                ''')
                
                # Papers table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS papers (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        authors TEXT,
                        year INTEGER,
                        snippet TEXT,
                        url TEXT,
                        pdf_url TEXT,
                        citations INTEGER DEFAULT 0,
                        abstract TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Topics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generated_topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paper_ids TEXT NOT NULL,
                        topics TEXT NOT NULL,
                        method TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # PDF files table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pdf_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        filepath TEXT NOT NULL,
                        abstract TEXT,
                        metadata TEXT,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Application stats table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS app_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stat_name TEXT UNIQUE NOT NULL,
                        stat_value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_cache_query ON search_cache(query_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _generate_query_hash(self, query, max_results):
        """Generate hash for query caching"""
        query_string = f"{query.lower().strip()}_{max_results}"
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def get_cached_search(self, query, max_results, cache_hours=24):
        """
        Get cached search results
        
        Args:
            query (str): Search query
            max_results (int): Maximum results
            cache_hours (int): Cache validity in hours
            
        Returns:
            list: Cached results or None
        """
        try:
            query_hash = self._generate_query_hash(query, max_results)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT results FROM search_cache 
                    WHERE query_hash = ? 
                    AND datetime(created_at, '+{} hours') > datetime('now')
                '''.format(cache_hours), (query_hash,))
                
                result = cursor.fetchone()
                if result:
                    logger.info(f"Cache hit for query: {query}")
                    return json.loads(result[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached search: {e}")
            return None
    
    def cache_search_results(self, query, max_results, results):
        """Cache search results"""
        try:
            query_hash = self._generate_query_hash(query, max_results)
            results_json = json.dumps(results)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO search_cache 
                    (query_hash, query, max_results, results)
                    VALUES (?, ?, ?, ?)
                ''', (query_hash, query, max_results, results_json))
                
                conn.commit()
                logger.info(f"Cached search results for: {query}")
                
        except Exception as e:
            logger.error(f"Error caching search results: {e}")
    
    def save_paper(self, paper_data):
        """Save paper to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO papers 
                    (id, title, authors, year, snippet, url, pdf_url, citations, abstract, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paper_data.get('id'),
                    paper_data.get('title'),
                    paper_data.get('authors'),
                    paper_data.get('year'),
                    paper_data.get('snippet'),
                    paper_data.get('url'),
                    paper_data.get('pdf_url'),
                    paper_data.get('citations', 0),
                    paper_data.get('abstract'),
                    json.dumps(paper_data.get('metadata', {}))
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving paper: {e}")
    
    def save_generated_topics(self, papers, topics):
        """Save generated topics"""
        try:
            paper_ids = [paper.get('id', '') for paper in papers]
            paper_ids_str = ','.join(paper_ids)
            topics_json = json.dumps(topics)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO generated_topics (paper_ids, topics, method)
                    VALUES (?, ?, ?)
                ''', (paper_ids_str, topics_json, 'ml_clustering'))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving generated topics: {e}")
    
    def save_pdf_processing(self, filename, filepath, abstract, metadata):
        """Save PDF processing results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO pdf_files (filename, filepath, abstract, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (filename, filepath, abstract, json.dumps(metadata)))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving PDF processing results: {e}")
    
    def get_application_stats(self):
        """Get application statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total searches
                cursor.execute('SELECT COUNT(*) FROM search_cache')
                stats['total_searches'] = cursor.fetchone()[0]
                
                # Total papers
                cursor.execute('SELECT COUNT(*) FROM papers')
                stats['total_papers'] = cursor.fetchone()[0]
                
                # Total topics generated
                cursor.execute('SELECT COUNT(*) FROM generated_topics')
                stats['total_topics_generated'] = cursor.fetchone()[0]
                
                # Total PDFs processed
                cursor.execute('SELECT COUNT(*) FROM pdf_files')
                stats['total_pdfs_processed'] = cursor.fetchone()[0]
                
                # Recent activity (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) FROM search_cache 
                    WHERE created_at > datetime('now', '-7 days')
                ''')
                stats['recent_searches'] = cursor.fetchone()[0]
                
                # Most searched terms
                cursor.execute('''
                    SELECT query, COUNT(*) as count 
                    FROM search_cache 
                    GROUP BY query 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                stats['top_queries'] = [{'query': row[0], 'count': row[1]} 
                                       for row in cursor.fetchall()]
                
                # Recent papers by year
                cursor.execute('''
                    SELECT year, COUNT(*) as count 
                    FROM papers 
                    WHERE year IS NOT NULL 
                    GROUP BY year 
                    ORDER BY year DESC 
                    LIMIT 10
                ''')
                stats['papers_by_year'] = [{'year': row[0], 'count': row[1]} 
                                          for row in cursor.fetchall()]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting application stats: {e}")
            return {'error': str(e)}
    
    def cleanup_old_cache(self, days=7):
        """Clean up old cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM search_cache 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
