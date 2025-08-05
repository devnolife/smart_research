from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import requests
import os
import hashlib
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedScholarScraper:
    """Enhanced Google Scholar scraper with stealth mode and advanced features"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://scholar.google.com"
        self.cache_dir = "../data/cache"
        self.papers_dir = "../data/papers"
        self.max_retries = 3
        self.delay_range = (2, 5)
        
        # Ensure directories exist
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.papers_dir, exist_ok=True)
    
    def _setup_driver(self):
        """Setup Chrome driver with stealth options"""
        options = Options()
        
        # Stealth options
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--window-size=1920,1080")
        
        # Random user agent
        user_agent = self.ua.random
        options.add_argument(f"--user-agent={user_agent}")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Apply stealth
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        return driver
    
    def _random_delay(self):
        """Add random delay to avoid detection"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _detect_captcha(self, driver):
        """Detect if CAPTCHA is present"""
        try:
            captcha_elements = [
                "//div[contains(@class, 'g-recaptcha')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//*[contains(text(), 'unusual traffic')]"
            ]
            
            for element in captcha_elements:
                if driver.find_elements(By.XPATH, element):
                    return True
            return False
        except:
            return False
    
    def _extract_paper_data(self, result_element):
        """Extract data from a single search result"""
        try:
            paper_data = {}
            
            # Title
            title_elem = result_element.find_element(By.CSS_SELECTOR, ".gs_rt a")
            paper_data['title'] = title_elem.text.strip()
            paper_data['url'] = title_elem.get_attribute('href')
            
            # Authors and publication info
            authors_elem = result_element.find_element(By.CSS_SELECTOR, ".gs_a")
            authors_text = authors_elem.text
            paper_data['authors'] = authors_text.split(' - ')[0] if ' - ' in authors_text else authors_text
            
            # Extract year from authors text
            year_match = None
            for part in authors_text.split(' - '):
                if any(char.isdigit() for char in part):
                    year_match = ''.join(filter(str.isdigit, part))
                    if len(year_match) == 4 and year_match.startswith('20'):
                        break
            paper_data['year'] = int(year_match) if year_match else None
            
            # Abstract/snippet
            snippet_elem = result_element.find_element(By.CSS_SELECTOR, ".gs_rs")
            paper_data['snippet'] = snippet_elem.text.strip() if snippet_elem else ""
            
            # Citations
            try:
                citation_elem = result_element.find_element(By.XPATH, ".//a[contains(text(), 'Cited by')]")
                citations_text = citation_elem.text
                paper_data['citations'] = int(''.join(filter(str.isdigit, citations_text)))
            except NoSuchElementException:
                paper_data['citations'] = 0
            
            # PDF link
            try:
                pdf_elem = result_element.find_element(By.CSS_SELECTOR, ".gs_or_ggsm a")
                paper_data['pdf_url'] = pdf_elem.get_attribute('href')
            except NoSuchElementException:
                paper_data['pdf_url'] = None
            
            # Additional metadata
            paper_data['scraped_at'] = datetime.now().isoformat()
            paper_data['id'] = hashlib.md5(paper_data['title'].encode()).hexdigest()
            
            return paper_data
            
        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None
    
    def scrape_papers(self, query, max_results=50, year_range=None):
        """
        Scrape papers from Google Scholar with pagination
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to scrape
            year_range (tuple): (start_year, end_year) or None
        
        Returns:
            list: List of paper dictionaries
        """
        logger.info(f"Starting scrape for query: {query}, max_results: {max_results}")
        
        papers = []
        driver = None
        
        try:
            driver = self._setup_driver()
            
            # Navigate to Google Scholar
            driver.get(self.base_url)
            self._random_delay()
            
            # Check for CAPTCHA
            if self._detect_captcha(driver):
                logger.warning("CAPTCHA detected, waiting longer...")
                time.sleep(30)
            
            # Perform search
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(query)
            
            # Add year filter if specified
            if year_range:
                year_filter = f" after:{year_range[0]} before:{year_range[1]}"
                search_box.send_keys(year_filter)
            
            search_box.submit()
            self._random_delay()
            
            # Scrape multiple pages
            page_num = 0
            results_per_page = 10
            
            while len(papers) < max_results:
                # Wait for results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_ri"))
                )
                
                # Check for CAPTCHA after each page
                if self._detect_captcha(driver):
                    logger.warning("CAPTCHA detected during scraping")
                    break
                
                # Extract papers from current page
                result_elements = driver.find_elements(By.CSS_SELECTOR, ".gs_ri")
                
                if not result_elements:
                    logger.info("No more results found")
                    break
                
                for result_elem in result_elements:
                    if len(papers) >= max_results:
                        break
                        
                    paper_data = self._extract_paper_data(result_elem)
                    if paper_data:
                        papers.append(paper_data)
                
                logger.info(f"Scraped {len(papers)} papers so far...")
                
                # Try to go to next page
                try:
                    next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
                    if 'disabled' in next_button.get_attribute('class'):
                        break
                    
                    driver.execute_script("arguments[0].click();", next_button)
                    self._random_delay()
                    page_num += 1
                    
                except NoSuchElementException:
                    logger.info("No next page button found")
                    break
            
            logger.info(f"Successfully scraped {len(papers)} papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
            
        finally:
            if driver:
                driver.quit()
    
    def extract_abstract_from_link(self, paper_url):
        """
        Follow paper link to extract full abstract
        
        Args:
            paper_url (str): URL of the paper
            
        Returns:
            str: Extracted abstract or None
        """
        try:
            driver = self._setup_driver()
            driver.get(paper_url)
            self._random_delay()
            
            # Common abstract selectors for different publishers
            abstract_selectors = [
                ".abstract",
                "#abstract",
                ".section-title:contains('Abstract') + *",
                "[data-testid='abstract']",
                ".c-article-section__content",
                ".abstract-content"
            ]
            
            for selector in abstract_selectors:
                try:
                    abstract_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    if abstract_elem and abstract_elem.text.strip():
                        return abstract_elem.text.strip()
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting abstract from {paper_url}: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()
    
    def download_pdf_if_available(self, pdf_url, paper_id):
        """
        Download PDF if available
        
        Args:
            pdf_url (str): URL of the PDF
            paper_id (str): Unique identifier for the paper
            
        Returns:
            str: Path to downloaded file or None
        """
        if not pdf_url:
            return None
            
        try:
            # Set headers to mimic browser
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/pdf,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"Response is not a PDF: {content_type}")
                return None
            
            # Save PDF
            filename = f"{paper_id}.pdf"
            filepath = os.path.join(self.papers_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded PDF: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return None
