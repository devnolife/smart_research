from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from core.scholar_scraper import EnhancedScholarScraper
from core.topic_generator import TopicGenerator
from core.pdf_processor import PDFProcessor
from core.database import Database
from utils.api_helpers import validate_request, format_response

app = Flask(__name__)
CORS(app)

# Initialize components
scholar_scraper = EnhancedScholarScraper()
topic_generator = TopicGenerator()
pdf_processor = PDFProcessor()
db = Database()

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

@app.route('/api/search', methods=['POST'])
def search_papers():
    """Search for academic papers using enhanced scholar scraper"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 50)
        year_range = data.get('year_range', None)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check cache first
        cached_results = db.get_cached_search(query, max_results)
        if cached_results:
            return format_response({
                'papers': cached_results,
                'from_cache': True,
                'timestamp': datetime.now().isoformat()
            })
        
        # Perform new search
        papers = scholar_scraper.scrape_papers(
            query=query,
            max_results=max_results,
            year_range=year_range
        )
        
        # Cache results
        db.cache_search_results(query, max_results, papers)
        
        return format_response({
            'papers': papers,
            'from_cache': False,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-topics', methods=['POST'])
def generate_topics():
    """Generate research topic suggestions from selected papers"""
    try:
        data = request.get_json()
        papers = data.get('papers', [])
        n_topics = data.get('n_topics', 5)
        
        if not papers:
            return jsonify({'error': 'Papers are required'}), 400
        
        topics = topic_generator.generate_topics(papers, n_topics)
        
        # Save to database
        db.save_generated_topics(papers, topics)
        
        return format_response({
            'topics': topics,
            'paper_count': len(papers),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Process uploaded PDF and extract abstract"""
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{pdf_file.filename}"
        filepath = os.path.join('../data/papers', filename)
        pdf_file.save(filepath)
        
        # Extract abstract
        abstract = pdf_processor.extract_abstract(filepath)
        
        return format_response({
            'abstract': abstract,
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf/<paper_id>', methods=['POST'])
def download_pdf(paper_id):
    """Download PDF from paper URL"""
    try:
        data = request.get_json()
        pdf_url = data.get('pdf_url', '')
        
        if not pdf_url:
            return jsonify({'error': 'PDF URL is required'}), 400
        
        # Download and process PDF
        filepath = scholar_scraper.download_pdf_if_available(pdf_url, paper_id)
        
        if filepath:
            abstract = pdf_processor.extract_abstract(filepath)
            return format_response({
                'success': True,
                'abstract': abstract,
                'filepath': filepath
            })
        else:
            return jsonify({'error': 'Failed to download PDF'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        stats = db.get_application_stats()
        return format_response(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    db.init_database()
    
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
