# Smart Research Assistant v2

## 🚀 Modern Research Paper Inspiration System

A sophisticated web-based research assistant that scrapes academic papers from Google Scholar, extracts abstracts, and provides AI-powered research topic suggestions. This is an enhanced version with modern web UI and advanced features.

## ✨ Features

### 🔍 Enhanced Academic Search
- **Advanced Google Scholar Scraper** with stealth mode to avoid detection
- **Pagination Support** - scrape up to 100+ papers per search
- **Year Range Filtering** - search papers from specific time periods
- **Rate Limiting & Proxy Rotation** for reliable scraping
- **CAPTCHA Detection** with retry logic
- **Caching System** to avoid repeated requests

### 🧠 AI-Powered Topic Generation
- **Multiple ML Techniques** - K-means clustering and LDA topic modeling
- **Smart Keyword Extraction** using TF-IDF vectorization
- **Research Question Generation** - potential questions for your research
- **Thematic Analysis** - discover hidden patterns in paper collections

### 📑 PDF Processing
- **Drag & Drop Upload** - easy PDF file handling
- **Abstract Extraction** - automatic detection and extraction
- **Metadata Analysis** - file information and statistics
- **Multiple PDF Support** - batch processing capabilities

### 📊 Analytics & Statistics
- **Search History** - track your research queries
- **Usage Statistics** - monitor your research activity
- **Popular Terms** - see trending research topics
- **Publication Trends** - papers by year analysis

### 🎨 Modern Web Interface
- **Responsive Design** - works on desktop, tablet, and mobile
- **Real-time Updates** - live search progress and notifications
- **Interactive UI** - modern components and smooth animations
- **Dark/Light Theme Ready** - easy customization

## 🛠️ Technical Architecture

### Backend (Flask API)
```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── core/
│   ├── scholar_scraper.py # Enhanced Google Scholar scraper
│   ├── topic_generator.py # AI-powered topic generation
│   ├── pdf_processor.py   # PDF abstract extraction
│   └── database.py        # SQLite data storage
└── utils/
    └── api_helpers.py     # API utilities and helpers
```

### Frontend (Modern Web App)
```
frontend/
├── index.html            # Main application interface
├── css/
│   └── style.css        # Modern responsive styling
└── js/
    ├── main.js          # Application logic
    └── components.js    # Reusable UI components
```

### Data Storage
```
data/
├── papers/              # Downloaded PDF files
├── cache/              # Cached search results
└── research_assistant.db # SQLite database
```

## 🚀 Quick Start

### 1. Install Dependencies

Navigate to the backend directory and install Python packages:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize the Application

Run the Flask development server:

```bash
python app.py
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## 📋 Usage Guide

### 🔍 Searching for Papers

1. **Enter Search Query**: Type your research topic (e.g., "Artificial Intelligence in Education")
2. **Set Parameters**: Choose max results (20-100) and optional year range
3. **Review Results**: Browse through found papers with abstracts and metadata
4. **Select Papers**: Check papers of interest for topic generation

### 💡 Generating Research Topics

1. **Select Papers**: Choose relevant papers from search results
2. **Generate Topics**: Click "Generate Topics" to run AI analysis
3. **Review Suggestions**: Explore different topic categories:
   - Key research terms
   - Research focus areas
   - Thematic categories
   - Potential research questions

### 📤 Processing PDFs

1. **Upload Files**: Drag & drop PDF files or use file browser
2. **Automatic Processing**: Abstracts are extracted automatically
3. **Review Results**: View extracted content and metadata

### 📊 Analytics

1. **View Statistics**: Check your research activity and trends
2. **Popular Terms**: See most searched topics
3. **Publication Trends**: Analyze papers by publication year

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///data/research_assistant.db

# API Settings
API_RATE_LIMIT=60
CACHE_TTL=3600

# Scraper Settings
MAX_PAPERS_PER_SEARCH=100
SCRAPER_DELAY_MIN=2
SCRAPER_DELAY_MAX=5

# File Upload
MAX_FILE_SIZE=50MB
UPLOAD_FOLDER=../data/papers
```

## 🔧 Advanced Features

### Enhanced Scholar Scraper

The scraper includes advanced features:

- **Stealth Mode**: Avoids detection with random user agents and delays
- **Error Handling**: Robust retry logic for failed requests
- **Metadata Extraction**: Citations, authors, publication year, PDF links
- **Content Processing**: Clean text extraction and formatting

### AI Topic Generation

Multiple ML techniques for comprehensive analysis:

- **TF-IDF Vectorization**: Extract important terms and phrases
- **K-means Clustering**: Group similar papers by themes
- **LDA Topic Modeling**: Discover latent topics in paper collections
- **Research Questions**: Generate potential research directions

## 📈 Performance Optimizations

- **Database Caching**: Store search results to reduce API calls
- **Lazy Loading**: Load content progressively for better UX
- **Compression**: Minimize payload sizes for faster transfers
- **Background Processing**: Handle long-running tasks asynchronously

---

**Happy Researching! 🔬✨**
