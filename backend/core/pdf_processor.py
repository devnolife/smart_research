import fitz  # PyMuPDF
import re
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Enhanced PDF processing for abstract extraction"""
    
    def __init__(self):
        self.abstract_patterns = [
            r'abstract\s*:?\s*(.*?)(?=\n\s*(?:keywords?|introduction|1\.|background|method|conclusion))',
            r'summary\s*:?\s*(.*?)(?=\n\s*(?:keywords?|introduction|1\.|background|method|conclusion))',
            r'overview\s*:?\s*(.*?)(?=\n\s*(?:keywords?|introduction|1\.|background|method|conclusion))',
        ]
    
    def _clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'[^\w\s\.,;:!?()-]', ' ', text)
        
        # Remove repeated spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_abstract_by_patterns(self, text):
        """Extract abstract using regex patterns"""
        text_lower = text.lower()
        
        for pattern in self.abstract_patterns:
            matches = re.finditer(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                abstract = match.group(1)
                if abstract and len(abstract.strip()) > 50:  # Minimum length check
                    return self._clean_text(abstract)
        
        return None
    
    def _extract_abstract_by_structure(self, doc):
        """Extract abstract by analyzing document structure"""
        try:
            abstract_text = ""
            found_abstract = False
            
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc.load_page(page_num)
                text = page.get_text()
                
                lines = text.split('\n')
                
                for i, line in enumerate(lines):
                    line_lower = line.lower().strip()
                    
                    # Look for abstract section
                    if any(keyword in line_lower for keyword in ['abstract', 'summary', 'overview']):
                        if len(line_lower) < 20:  # Likely a header
                            found_abstract = True
                            continue
                    
                    # If we found abstract header, collect following text
                    if found_abstract:
                        # Stop at next section
                        if any(keyword in line_lower for keyword in 
                               ['introduction', 'background', 'method', 'keyword', '1.', 'i.']):
                            break
                        
                        if line.strip():
                            abstract_text += line + " "
                        
                        # Stop if we have enough text
                        if len(abstract_text) > 500:
                            break
                
                if abstract_text and len(abstract_text.strip()) > 100:
                    return self._clean_text(abstract_text)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting abstract by structure: {e}")
            return None
    
    def _extract_first_paragraph(self, doc):
        """Extract first substantial paragraph as potential abstract"""
        try:
            for page_num in range(min(2, len(doc))):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                paragraphs = text.split('\n\n')
                
                for paragraph in paragraphs:
                    cleaned = self._clean_text(paragraph)
                    # Look for substantial paragraphs that might be abstracts
                    if (len(cleaned) > 100 and 
                        len(cleaned) < 2000 and
                        not any(keyword in cleaned.lower() for keyword in 
                               ['figure', 'table', 'reference', 'citation', 'doi:', 'isbn'])):
                        return cleaned
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting first paragraph: {e}")
            return None
    
    def extract_abstract(self, pdf_path):
        """
        Extract abstract from PDF file
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted abstract or None
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                logger.error("PDF contains no pages")
                return None
            
            # Get full text from first few pages
            full_text = ""
            for page_num in range(min(3, len(doc))):
                page = doc.load_page(page_num)
                full_text += page.get_text() + "\n"
            
            doc.close()
            
            # Try different extraction methods
            
            # Method 1: Pattern matching
            abstract = self._extract_abstract_by_patterns(full_text)
            if abstract and len(abstract) > 50:
                logger.info("Abstract extracted using pattern matching")
                return abstract
            
            # Method 2: Structure analysis
            doc = fitz.open(pdf_path)
            abstract = self._extract_abstract_by_structure(doc)
            doc.close()
            
            if abstract and len(abstract) > 50:
                logger.info("Abstract extracted using structure analysis")
                return abstract
            
            # Method 3: First substantial paragraph
            doc = fitz.open(pdf_path)
            abstract = self._extract_first_paragraph(doc)
            doc.close()
            
            if abstract and len(abstract) > 50:
                logger.info("Abstract extracted as first paragraph")
                return abstract
            
            logger.warning("No abstract could be extracted")
            return "Unable to extract abstract from this PDF. The document may not contain a clear abstract section or may be in an unsupported format."
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return f"Error processing PDF: {str(e)}"
    
    def extract_metadata(self, pdf_path):
        """
        Extract metadata from PDF
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            dict: PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            
            # Add file info
            file_info = {
                'filename': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path),
                'page_count': len(doc),
                'processed_at': datetime.now().isoformat()
            }
            
            doc.close()
            
            return {**metadata, **file_info}
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")
            return {'error': str(e)}
    
    def extract_full_text(self, pdf_path, max_pages=None):
        """
        Extract full text from PDF
        
        Args:
            pdf_path (str): Path to PDF file
            max_pages (int): Maximum number of pages to process
            
        Returns:
            str: Full text content
        """
        try:
            doc = fitz.open(pdf_path)
            
            if max_pages:
                max_pages = min(max_pages, len(doc))
            else:
                max_pages = len(doc)
            
            full_text = ""
            for page_num in range(max_pages):
                page = doc.load_page(page_num)
                full_text += page.get_text() + "\n\n"
            
            doc.close()
            
            return self._clean_text(full_text)
            
        except Exception as e:
            logger.error(f"Error extracting full text from {pdf_path}: {e}")
            return None
