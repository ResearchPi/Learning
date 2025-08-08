import json
import logging
from typing import List, Dict, Any
from datetime import datetime
    
from PaperCollector import PaperCollector
from KeywordExtractor import KeywordExtractor
from LLMProcessor import LLMProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchProcessor:
    """
    Simple processor that combines KeyBERT keyword extraction and DeepSeek field classification
    """
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """
        Initialize the research processor
        
        Args:
            api_key: API key for DeepSeek (via OpenRouter or direct)
            api_base: API base URL (optional, defaults to OpenRouter)
        """
        self.api_key = api_key
        self.api_base = api_base
        
        self.keyword_extractor = KeywordExtractor()
        self.llm_processor = LLMProcessor(api_key=api_key, api_base=api_base)
        
        logger.info("Research processor initialized with KeyBERT + DeepSeek")
    
    def process_researcher(self, name: str, school: str = None) -> Dict:
        """
        Complete processing pipeline for a researcher
        
        Args:
            name: Researcher name
            school: Institution/school name (optional)
            
        Returns:
            Complete research analysis
        """
        logger.info(f"Processing researcher: {name} from {school or 'Unknown institution'}")
        
        # Get papers from all sources
        logger.info("Step 1: Fetching papers from academic databases...")
        collector = PaperCollector(name, affiliation=school)
        papers = collector.get_papers()
        
        if not papers:
            logger.warning(f"No papers found for {name}")
            return self._create_empty_result(name, school)
        
        logger.info(f"Found {len(papers)} papers")
        
        # Extract keywords using KeyBERT
        logger.info("Step 2: Extracting keywords using KeyBERT...")
        papers_with_keywords = self._extract_keywords_from_papers(papers)
        
        # Collect all unique affiliations for the researcher
        all_affiliations = self._collect_researcher_affiliations(papers_with_keywords, name)
        
        # Classify research fields using DeepSeek from keywords
        logger.info("Step 3: Classifying research fields using DeepSeek...")
        classification_result = self.llm_processor.classify_research_fields(papers_with_keywords, all_affiliations, name)
        
        # Extract the field classification from the result
        field_classification = classification_result.get("fields", {})
        summary = classification_result.get("summary", "")
        
        # Create output
        logger.info("Step 4: Creating final output...")
        final_output = self.llm_processor.create_final_output(papers_with_keywords, field_classification, all_affiliations)
        
        # Add the summary to the final output
        if 'summary' not in final_output:
            final_output['summary'] = summary
        
        # Add researcher info
        final_output['researcher'] = {
            'name': name,
            'institution': school,
            'affiliations': all_affiliations,
            'analysis_date': datetime.now().isoformat()
        }
        
        logger.info("Processing complete!")
        return final_output
    
    def _extract_keywords_from_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Extract keywords from all papers using KeyBERT
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Papers with extracted keywords added
        """
        papers_with_keywords = []
        
        for i, paper in enumerate(papers):
            logger.info(f"Extracting keywords from paper {i+1}/{len(papers)}: {paper.get('title', 'No title')[:50]}...")
            
            try:
                # Extract keywords using KeyBERT
                keyword_result = self.keyword_extractor.extract_paper_keywords(paper)
                
                # Add keywords to paper
                paper_with_keywords = paper.copy()
                paper_with_keywords.update(keyword_result)
                paper_with_keywords['sources'] = keyword_result.get('categories', [])

                papers_with_keywords.append(paper_with_keywords)
                
            except Exception as e:
                logger.error(f"Error extracting keywords from paper {i+1}: {e}")
                # Add paper without keywords
                paper_with_keywords = paper.copy()
                paper_with_keywords.update({
                    'keywords': [],
                    'categories': paper.get('categories', []),
                    'sources': paper.get('categories', [])
                })
                papers_with_keywords.append(paper_with_keywords)
        
        return papers_with_keywords
    
    def _collect_researcher_affiliations(self, papers: List[Dict], researcher_name: str) -> List[str]:
        """
        Collect all unique affiliations for a researcher from their papers
        
        Args:
            papers: List of papers with author information
            researcher_name: Name of the researcher
            
        Returns:
            List of unique affiliations
        """
        affiliations = set()
        
        for paper in papers:

            if 'authors' in paper:
                for author in paper['authors']:

                    if author.get('name', '').lower() == researcher_name.lower():
                        affiliation = author.get('affiliation', '').strip()

                        if affiliation and affiliation not in affiliations:
                            clean_affiliation = self._clean_affiliation_text(affiliation)

                            if clean_affiliation:
                                affiliations.add(clean_affiliation) 
        
        return sorted(list(affiliations))
    
    def _clean_affiliation_text(self, affiliation: str) -> str:
        """
        Clean and standardize affiliation text
        
        Args:
            affiliation: Raw affiliation text
            
        Returns:
            Cleaned affiliation text
        """
        if not affiliation:
            return ""
        
        # Remove email addresses
        import re
        affiliation = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', affiliation)
        
        # Remove extra whitespace and punctuation
        affiliation = re.sub(r'\s+', ' ', affiliation.strip())
        affiliation = re.sub(r'[.,;]+$', '', affiliation)
        
        # Remove asterisks and other common formatting
        affiliation = re.sub(r'^\*+\s*', '', affiliation)
        
        return affiliation.strip()
    
    def _create_empty_result(self, name: str, school: str = None) -> Dict:
        """Create empty result when no papers are found"""
        return {
            'researcher': {
                'name': name,
                'institution': school,
                'affiliations': [],
                'analysis_date': datetime.now().isoformat()
            },
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'total_papers': 0,
                'sources': ["arXiv", "PubMed", "DOAJ", "Zenodo", "Crossref"],
                'nlp_model_used': "KeyBERT",
                'llm_provider': "DeepSeek R1 (Free)"
            },
            'field_classification': {
                'primary_fields': [],
                'secondary_fields': [],
                'interdisciplinary_areas': []
            },
            'papers': [],
            'summary': f"No papers found for {name} from {school or 'unknown institution'}"
        }
    
    def save_results(self, results: Dict, output_file: str = None) -> str:
        """
        Save results to JSON file
        
        Args:
            results: Analysis results
            output_file: Output file path (optional)
            
        Returns:
            Path to saved file
        """
        if not output_file:
            researcher_name = results['researcher']['name'].replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"research_analysis_{researcher_name}_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise
    
    def print_summary(self, results: Dict):
        """Print a summary of the analysis results"""
        researcher = results['researcher']
        metadata = results['metadata']
        field_classification = results['field_classification']
        
        print("\n" + "="*80)
        print("RESEARCH ANALYSIS SUMMARY")
        print("="*80)
        print(f"Researcher: {researcher['name']}")
        
        # Display affiliations if available
        if 'affiliations' in researcher and researcher['affiliations']:
            print(f"Affiliations:")
            for i, affiliation in enumerate(researcher['affiliations'], 1):
                print(f"  {i}. {affiliation}")
        else:
            print(f"Institution: {researcher['institution'] or 'Unknown'}")
        
        print(f"Total Papers: {metadata['total_papers']}")
        print(f"Analysis Date: {researcher['analysis_date']}")
        print(f"NLP Model: {metadata['nlp_model_used']}")
        print(f"LLM Provider: {metadata['llm_provider']}")
        
        print("\nPRIMARY RESEARCH FIELDS:")
        for field in field_classification.get('primary_fields', []):
            print(f"  • {field['name']} (Confidence: {field['confidence']:.2f})")
            print(f"    Description: {field['description']}")
            print(f"    Key Terms: {', '.join(field['key_terms'][:5])}")
            print(f"    Paper Count: {field['paper_count']}")
            print()
        
        if field_classification.get('secondary_fields'):
            print("SECONDARY RESEARCH FIELDS:")
            for field in field_classification['secondary_fields']:
                print(f"  • {field['name']} (Confidence: {field['confidence']:.2f})")
        
        if field_classification.get('interdisciplinary_areas'):
            print("\nINTERDISCIPLINARY AREAS:")
            for area in field_classification['interdisciplinary_areas']:
                print(f"  • {area['name']} (Confidence: {area['confidence']:.2f})")
        
        print("\n" + "="*80)

def main():
    """Example usage of the ResearchProcessor"""
    
    # Load environment variables from .env file
    import os
    from dotenv import load_dotenv
    
    # Load .env file if it exists
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
    api_base = "https://openrouter.ai/api/v1"  # Default to OpenRouter
    
    # Debug: Print what we found
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    else:
        print("No API key found in environment variables")
        print("Available env vars:", [k for k in os.environ.keys() if 'API' in k or 'KEY' in k])
    
    # Initialize processor
    processor = ResearchProcessor(api_key=api_key, api_base=api_base)
    
    # Example researcher
    researcher_name = "Pingkun Yan"
    institution = "Rensselaer Polytechnic Institute"
    
    try:
        # Process researcher
        results = processor.process_researcher(researcher_name, institution)
        
        # Print summary
        processor.print_summary(results)
        
        # Save results
        output_file = processor.save_results(results)
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing researcher: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 