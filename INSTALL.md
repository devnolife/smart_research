# Installation and Setup Guide

## Prerequisites

Before installing the Smart Research Assistant v2, ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Google Chrome Browser** (latest version)
   - Required for the Selenium web scraper
   - ChromeDriver will be automatically managed

3. **Git** (optional, for cloning the repository)

## Installation Steps

### Option 1: Download and Extract

1. Download the project as a ZIP file
2. Extract to your desired location
3. Navigate to the project directory

### Option 2: Clone Repository

```bash
git clone <repository-url>
cd smart_research_assistant_v2
```

## Setup Instructions

### 1. Install Python Dependencies

Navigate to the backend directory and install required packages:

**Windows:**
```cmd
cd backend
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
cd backend
pip3 install -r requirements.txt
```

### 2. Create Environment Configuration (Optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` file with your preferred settings:
- Database path
- Cache settings
- File upload limits
- API rate limits

### 3. Initialize the Database

The database will be automatically created when you first run the application.

### 4. Run the Application

**Easy Start (Windows):**
```cmd
# From project root directory
run_dev.bat
```

**Easy Start (macOS/Linux):**
```bash
# From project root directory
chmod +x run_dev.sh
./run_dev.sh
```

**Manual Start:**
```bash
cd backend
python app.py
```

### 5. Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## First-Time Usage

### 1. Test the Search Function

1. Enter a research topic (e.g., "machine learning")
2. Set max results to 20 (for testing)
3. Click "Search"
4. Wait for results to load

### 2. Generate Topics

1. Select a few papers from the search results
2. Click "Generate Topics"
3. Switch to the "Topics" tab to view results

### 3. Upload a PDF

1. Go to the "PDF Upload" tab
2. Drag and drop a PDF file or click to browse
3. Wait for abstract extraction

### 4. View Statistics

1. Click on the "Statistics" tab
2. View your usage statistics

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

**2. Chrome/ChromeDriver issues**
- Ensure Google Chrome is installed and up to date
- The WebDriver Manager will automatically download the correct ChromeDriver

**3. Permission errors on Windows**
- Run Command Prompt as Administrator
- Or use PowerShell instead of CMD

**4. Port 5000 already in use**
```bash
# Check what's using port 5000
netstat -tulpn | grep :5000

# Kill the process or change port in app.py
```

**5. Database permission errors**
- Ensure the data/ directory is writable
- Check file permissions in the project folder

### Performance Tips

**1. Reduce Search Load**
- Start with smaller result sets (20-30 papers)
- Use year filters to narrow searches
- Enable caching for repeated searches

**2. Optimize PDF Processing**
- Upload smaller PDF files first
- Process PDFs one at a time for testing

**3. Monitor Resource Usage**
- Close unnecessary browser tabs
- Watch memory usage during large operations

## Configuration Options

### Database Settings

Default: SQLite database in `data/research_assistant.db`

To use a different database:
```env
DATABASE_URL=sqlite:///path/to/your/database.db
```

### Search Settings

```env
MAX_PAPERS_PER_SEARCH=100
SCRAPER_DELAY_MIN=2
SCRAPER_DELAY_MAX=5
```

### File Upload Settings

```env
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_FOLDER=../data/papers
```

## Security Considerations

### For Development

- Default settings are suitable for local development
- No external access is configured by default
- Database is local SQLite file

### For Production

If deploying to production:

1. Change the secret key in `.env`
2. Use a production WSGI server (Gunicorn)
3. Configure proper database (PostgreSQL)
4. Set up reverse proxy (Nginx)
5. Enable HTTPS
6. Configure firewall rules

## Getting Help

### Documentation

- Check the main README.md for feature details
- Review code comments for technical details
- See the troubleshooting section above

### Common Questions

**Q: How many papers can I search at once?**
A: Up to 100 papers per search, but start with 20-50 for better performance.

**Q: What PDF formats are supported?**
A: Standard PDF files with text content. Scanned PDFs may not work well.

**Q: Can I use this offline?**
A: The PDF processing works offline, but searching requires internet connection.

**Q: How accurate is the topic generation?**
A: Accuracy depends on the quality and quantity of selected papers. More diverse papers = better topics.

### Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the console output for error messages
3. Ensure all dependencies are properly installed
4. Try with a simple test case first

## Next Steps

Once everything is working:

1. **Explore Features**: Try all tabs and functions
2. **Customize Settings**: Adjust configuration in `.env`
3. **Build Your Database**: Search and save papers of interest
4. **Generate Research Topics**: Use the AI features for inspiration
5. **Organize Your Research**: Use the statistics to track progress

---

**Enjoy your enhanced research experience! 🚀**
