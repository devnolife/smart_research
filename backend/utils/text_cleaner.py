import re
import string
from typing import List, Optional

def clean_text(text: str) -> str:
    """
    Enhanced text cleaning function
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^a-zA-Z0-9.,!?\-\s]", "", text)
    
    # Convert to lowercase
    text = text.lower().strip()
    
    return text

def clean_academic_text(text: str) -> str:
    """
    Specialized cleaning for academic text
    
    Args:
        text (str): Academic text to clean
        
    Returns:
        str: Cleaned academic text
    """
    if not text:
        return ""
    
    # Remove common academic artifacts
    text = re.sub(r'\b(abstract|introduction|conclusion|references?)\b:?', '', text, flags=re.IGNORECASE)
    
    # Remove citation patterns like [1], (Author, 2020), etc.
    text = re.sub(r'\[[\d,\s\-]+\]', '', text)
    text = re.sub(r'\([^)]*\d{4}[^)]*\)', '', text)
    
    # Remove URLs and DOIs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'doi:\s*[\w\./\-]+', '', text, flags=re.IGNORECASE)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Clean and normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def extract_keywords(text: str, min_length: int = 3, max_length: int = 20) -> List[str]:
    """
    Extract potential keywords from text
    
    Args:
        text (str): Input text
        min_length (int): Minimum keyword length
        max_length (int): Maximum keyword length
        
    Returns:
        List[str]: List of potential keywords
    """
    if not text:
        return []
    
    # Clean the text
    cleaned = clean_academic_text(text)
    
    # Split into words and filter
    words = [
        word.strip(string.punctuation) 
        for word in cleaned.split() 
        if min_length <= len(word.strip(string.punctuation)) <= max_length
        and word.strip(string.punctuation).isalpha()
    ]
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
        'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'shall', 'must', 'ought', 'need', 'dare', 'used', 'able'
    }
    
    keywords = [word for word in words if word.lower() not in stop_words]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword.lower() not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword.lower())
    
    return unique_keywords

def normalize_academic_title(title: str) -> str:
    """
    Normalize academic paper titles
    
    Args:
        title (str): Paper title
        
    Returns:
        str: Normalized title
    """
    if not title:
        return ""
    
    # Remove common prefixes/suffixes
    title = re.sub(r'^(a\s+|an\s+|the\s+)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*:\s*a\s+(review|survey|study|analysis)$', '', title, flags=re.IGNORECASE)
    
    # Normalize capitalization (title case)
    title = title.title()
    
    # Fix common academic terms
    academic_terms = {
        'Ai': 'AI',
        'Ml': 'ML',
        'Nlp': 'NLP',
        'Iot': 'IoT',
        'Api': 'API',
        'Ui': 'UI',
        'Ux': 'UX',
        'Cnn': 'CNN',
        'Rnn': 'RNN',
        'Lstm': 'LSTM',
        'Gpt': 'GPT',
        'Bert': 'BERT'
    }
    
    for wrong, correct in academic_terms.items():
        title = re.sub(r'\b' + wrong + r'\b', correct, title)
    
    return title.strip()

def clean_author_names(authors: str) -> List[str]:
    """
    Clean and parse author names
    
    Args:
        authors (str): Raw author string
        
    Returns:
        List[str]: List of cleaned author names
    """
    if not authors:
        return []
    
    # Remove common separators and prefixes
    authors = re.sub(r'\b(by|authors?:?)\s*', '', authors, flags=re.IGNORECASE)
    
    # Split by common separators
    separators = [',', ';', ' and ', ' & ', '\n']
    author_list = [authors]
    
    for sep in separators:
        new_list = []
        for author in author_list:
            new_list.extend([a.strip() for a in author.split(sep) if a.strip()])
        author_list = new_list
    
    # Clean individual names
    cleaned_authors = []
    for author in author_list[:10]:  # Limit to 10 authors
        # Remove titles and suffixes
        author = re.sub(r'\b(dr\.?|prof\.?|phd\.?|md\.?|jr\.?|sr\.?)\b', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\s+', ' ', author).strip()
        
        if author and len(author) > 2:
            cleaned_authors.append(author)
    
    return cleaned_authors

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "untitled"
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit length and clean up
    filename = filename[:100].strip()
    
    # Ensure it's not empty
    if not filename:
        filename = "untitled"
    
    return filename
