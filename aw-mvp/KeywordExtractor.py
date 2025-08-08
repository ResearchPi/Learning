import re
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordExtractor:
    """
    KeywordExtractor is a class that uses KeyBERT to extract keywords from a text.
    """
    
    def __init__(self):
        try:
            from keybert import KeyBERT
            self.model = KeyBERT()
            logger.info("KeyBERT model initialized successfully")

        except ImportError as e:
            logger.error(f"Failed to import KeyBERT: {e}")
            raise
    
    def extract_keywords(self, text: str, max_keywords: int = 15) -> List[str]:
        if not text or len(text.strip()) < 50:
            return []
        
        try:
            cleaned_text = self._preprocess_text(text)
            
            keywords = self.model.extract_keywords(
                cleaned_text,
                keyphrase_ngram_range=(1, 3),  # Extract 1-3 word phrases
                stop_words='english',
                use_maxsum=True,
                nr_candidates=20,
                top_n=max_keywords
            )
            
            return [keyword for keyword, _ in keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords with KeyBERT: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        text = re.sub(r'[^\w\s\-]', ' ', text) # Remove characters that are not words, spaces, or hyphens
        text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
        text = text.strip().lower() # Remove leading and trailing whitespace and convert to lowercase
        return text
    
    def extract_paper_keywords(self, paper: Dict) -> Dict:
        text_parts = []
        if paper.get('title'):
            text_parts.append(paper['title'])
        if paper.get('abstract'):
            text_parts.append(paper['abstract'])
        
        if not text_parts:
            return {'keywords': [], 'sources': []}
        
        combined_text = ' '.join(text_parts)
        
        keywords = self.extract_keywords(combined_text)
        
        original_categories = []
        if paper.get('categories'):
            original_categories.extend(paper['categories'])
        
        return {
            'keywords': keywords,
            'original_categories': original_categories,
            'text_used': combined_text[:200] + '...' if len(combined_text) > 200 else combined_text
        } 