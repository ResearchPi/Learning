import json
import logging
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProcessor:
    """
    LLMProcessor is a class that uses DeepSeek to classify research papers into broad research fields and generate a summary of the researcher's work.
    """
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """
        Initialize LLMProcessor
        
        Args:
            api_key: API key for OpenRouter
            api_base: API base URL (optional, defaults to OpenRouter)
        """
        self.api_key = api_key
        self.api_base = api_base or "https://openrouter.ai/api/v1"
        self.model_name = "deepseek/deepseek-r1:free"  
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the DeepSeek client"""
        try:
            from openai import OpenAI
            
            # For free version, API key not required
            if not self.api_key:
                raise ValueError("API key required for OpenRouter (even for free models)")
            
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            logger.info(f"DeepSeek client initialized with {self.api_base}")
                
        except ImportError as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            raise
    
    def classify_research_fields(self, papers_with_keywords: List[Dict], affiliations: List[str] = None) -> Dict[str, Any]:
        """
        Classify research paper's keywords into broader research fields using DeepSeek
        
        Args:
            papers_with_keywords: List of papers with extracted keywords
            affiliations: List of researcher's affiliations
            
        Returns:
            Dictionary with field classifications and summaries
        """
        if not papers_with_keywords:
            return {"fields": {}, "summary": "", "total_papers": 0}
        
        # Prepare data for LLM analysis
        analysis_data = self._prepare_analysis_data(papers_with_keywords)
        
        # Add affiliations to analysis data
        if affiliations:
            analysis_data['researcher_affiliations'] = affiliations
        
        # Get classification from DeepSeek
        field_classification = self._get_field_classification(analysis_data)
        
        # Generate summary
        summary = self._generate_overall_summary(analysis_data, field_classification)
        
        return {
            "fields": field_classification,
            "summary": summary,
            "total_papers": len(papers_with_keywords),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _prepare_analysis_data(self, papers_with_keywords: List[Dict]) -> Dict:
        """Prepare data for DeepSeek analysis"""
        
        # Collect all keywords and their frequencies
        all_keywords = []
        paper_summaries = []
        
        for paper in papers_with_keywords:
            # Add extracted keywords
            if 'keywords' in paper:
                all_keywords.extend(paper['keywords'])
            
            # Add existing categories
            if 'categories' in paper:
                all_keywords.extend(paper['categories'])
            
            # Create paper summary
            paper_summary = {
                'title': paper.get('title', 'No title'),
                'journal': paper.get('journal', 'Unknown'),
                'date': paper.get('publication_date', 'Unknown'),
                'keywords': paper.get('keywords', []),
                'categories': paper.get('categories', [])
            }
            paper_summaries.append(paper_summary)
        
        # Count keyword frequencies
        from collections import Counter
        keyword_freq = Counter(all_keywords)
        
        return {
            'keyword_frequencies': dict(keyword_freq.most_common(50)),
            'paper_summaries': paper_summaries,
            'total_papers': len(papers_with_keywords)
        }
    
    def _get_field_classification(self, analysis_data: Dict) -> Dict[str, Any]:
        """Get research field classification from DeepSeek"""
        
        # Create prompt for field classification
        prompt = self._create_field_classification_prompt(analysis_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert research analyst specializing in academic field classification. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = response.choices[0].message.content.strip()
            
            # Get response as JSON
            try:
                # First, try direct JSON parsing
                return json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                
                # Try to find JSON-like content
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass
                
                logger.warning(f"Failed to parse DeepSeek response as JSON. Response: {result[:200]}...")
                return self._fallback_field_classification(analysis_data)
                
        except Exception as e:
            logger.error(f"Error getting field classification: {e}")
            return self._fallback_field_classification(analysis_data)
    
    def _create_field_classification_prompt(self, analysis_data: Dict) -> str:
        """Create prompt for field classification"""
        
        keyword_text = ", ".join([f"{kw} ({freq})" for kw, freq in 
                                list(analysis_data['keyword_frequencies'].items())[:20]])
        
        prompt = f"""
        Analyze the following research data and classify it into broad research fields.
        
        Data Summary:
        - Total papers: {analysis_data['total_papers']}
        - Top keywords: {keyword_text}
        
        Paper details:
        """
        
        for i, paper in enumerate(analysis_data['paper_summaries'][:10]):  # Limit to first 10
            prompt += f"""
        Paper {i+1}:
        - Title: {paper['title']}
        - Journal: {paper['journal']}
        - Date: {paper['date']}
        - Keywords: {', '.join(paper['keywords'][:10])}
        - Categories: {', '.join(paper['categories'][:5])}
        """
        
        prompt += """
        
        TASK: Analyze this research data and classify it into research fields. Return ONLY a valid JSON object with this exact structure:
        
        {
            "primary_fields": [
                {
                    "name": "Field Name",
                    "description": "Brief description of the field",
                    "confidence": 0.95,
                    "key_terms": ["term1", "term2", "term3"],
                    "paper_count": 15
                }
            ],
            "secondary_fields": [
                {
                    "name": "Secondary Field Name", 
                    "description": "Brief description",
                    "confidence": 0.75,
                    "key_terms": ["term1", "term2"],
                    "paper_count": 8
                }
            ],
            "interdisciplinary_areas": [
                {
                    "name": "Interdisciplinary Area",
                    "description": "Description", 
                    "confidence": 0.8,
                    "key_terms": ["term1", "term2"],
                    "paper_count": 5
                }
            ]
        }
        
        REQUIREMENTS:
        1. Identify 2-4 primary research fields based on the most frequent keywords and paper titles
        2. Use standard academic field names: "Computer Vision", "Medical Imaging", "Machine Learning", "Deep Learning", "Image Processing", "Computer Graphics", "Robotics", "Data Science", "Artificial Intelligence"
        3. Provide confidence scores between 0.0 and 1.0
        4. List 3-5 key terms that define each field
        5. Estimate paper count based on keyword frequency
        6. Return ONLY the JSON object, no additional text or formatting
        
        IMPORTANT: Your response must be valid JSON that can be parsed by json.loads().
        """
        
        return prompt
    
    def _generate_overall_summary(self, analysis_data: Dict, field_classification: Dict) -> str:
        """Generate formatted research summary from collected data"""
        
        # Extract field information
        primary_fields = field_classification.get('primary_fields', [])
        secondary_fields = field_classification.get('secondary_fields', [])
        interdisciplinary_areas = field_classification.get('interdisciplinary_areas', [])
        
        # Get affiliations
        affiliations = analysis_data.get('researcher_affiliations', [])
        
        # Get top keywords
        top_keywords = list(analysis_data['keyword_frequencies'].keys())[:15]
        
        # Create formatted summary
        summary = f"""**Research Profile Summary**

**Researcher Information:**
- **Name:** {analysis_data.get('researcher_name', 'Unknown')}
- **Total Publications:** {analysis_data['total_papers']}
- **Primary Institution:** {affiliations[0] if affiliations else 'Unknown'}

**Research Focus Areas:**
"""
        
        # Add primary fields
        if primary_fields:
            summary += "\n**Primary Research Fields:**\n"
            for field in primary_fields:
                summary += f"- **{field.get('name', 'Unknown')}** (Confidence: {field.get('confidence', 0):.2f})\n"
                summary += f"  - Description: {field.get('description', 'No description available')}\n"
                summary += f"  - Key Terms: {', '.join(field.get('key_terms', [])[:5])}\n"
                summary += f"  - Estimated Papers: {field.get('paper_count', 0)}\n\n"
        
        # Add secondary fields
        if secondary_fields:
            summary += "**Secondary Research Fields:**\n"
            for field in secondary_fields:
                summary += f"- **{field.get('name', 'Unknown')}** (Confidence: {field.get('confidence', 0):.2f})\n"
                summary += f"  - Key Terms: {', '.join(field.get('key_terms', [])[:3])}\n\n"
        
        # Add interdisciplinary areas
        if interdisciplinary_areas:
            summary += "**Interdisciplinary Areas:**\n"
            for area in interdisciplinary_areas:
                summary += f"- **{area.get('name', 'Unknown')}** (Confidence: {area.get('confidence', 0):.2f})\n"
                summary += f"  - Description: {area.get('description', 'No description available')}\n\n"
        
        # Add key research themes
        summary += f"**Key Research Themes:**\n"
        summary += f"- {', '.join(top_keywords[:10])}\n\n"
        
        # Add affiliations section
        if affiliations:
            summary += "**Institutional Affiliations:**\n"
            for i, affiliation in enumerate(affiliations, 1):
                summary += f"- {affiliation}\n"
        
        # Add research impact summary
        summary += f"\n**Research Impact Summary:**\n"
        summary += f"This researcher has published {analysis_data['total_papers']} papers across multiple domains, "
        if primary_fields:
            summary += f"with primary focus on {', '.join([f.get('name', '') for f in primary_fields[:2]])}. "
        summary += f"Their work spans {len(affiliations) if affiliations else 0} different institutional affiliations, "
        summary += f"demonstrating broad collaborative networks and interdisciplinary research approaches."
        
        return summary
    
    def _fallback_field_classification(self, analysis_data: Dict) -> Dict[str, Any]:
        """Fallback field classification if DeepSeek fails"""
        
        # Simple keyword-based classification
        keywords = list(analysis_data['keyword_frequencies'].keys())
        
        # Define common research field keywords
        field_keywords = {
            "Computer Vision": ["vision", "image", "detection", "recognition", "segmentation"],
            "Machine Learning": ["learning", "neural", "network", "model", "algorithm"],
            "Medical Imaging": ["medical", "imaging", "radiology", "diagnosis", "scan"],
            "Natural Language Processing": ["language", "text", "nlp", "translation", "sentiment"],
            "Robotics": ["robot", "control", "automation", "mechanical"],
            "Data Science": ["data", "analysis", "statistics", "visualization"]
        }
        
        field_scores = {}
        for field, field_kw in field_keywords.items():
            score = sum(1 for kw in keywords if any(fk in kw.lower() for fk in field_kw))
            if score > 0:
                field_scores[field] = score
        
        # Sort by score and create classification
        sorted_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_fields = []
        for field, score in sorted_fields[:3]:
            primary_fields.append({
                "name": field,
                "description": f"Research in {field.lower()}",
                "confidence": min(0.9, score / 10),
                "key_terms": [kw for kw in keywords if any(fk in kw.lower() for fk in field_keywords[field])][:5],
                "paper_count": max(1, int(analysis_data['total_papers'] * score / sum(field_scores.values())))
            })
        
        return {
            "primary_fields": primary_fields,
            "secondary_fields": [],
            "interdisciplinary_areas": []
        }
    
    def _fallback_summary(self, analysis_data: Dict, field_classification: Dict) -> str:
        """Fallback summary using formatted approach"""
        return self._generate_overall_summary(analysis_data, field_classification)
    
    def create_final_output(self, papers_with_keywords: List[Dict], 
                           field_classification: Dict, affiliations: List[str] = None) -> Dict[str, Any]:
        """
        Create the final structured output combining all data
        
        Args:
            papers_with_keywords: Papers with extracted keywords
            field_classification: DeepSeek-generated field classification
            
        Returns:
            Complete structured output
        """
        
        # Sort papers by date (recent to oldest)
        sorted_papers = sorted(
            papers_with_keywords,
            key=lambda x: x.get('publication_date', ''),
            reverse=True
        )
        
        # Create final structure
        output = {
            "metadata": {
                "generation_date": datetime.now().isoformat(),
                "total_papers": len(sorted_papers),
                "sources": ["arXiv", "PubMed", "DOAJ", "Zenodo", "Crossref"],
                "nlp_model_used": "KeyBERT",
                "llm_provider": "DeepSeek R1 (Free)"
            },
            "field_classification": field_classification,
            "papers": []
        }
        
        # Add papers with their keywords
        for paper in sorted_papers:
            paper_entry = {
                "title": paper.get('title', 'No title'),
                "authors": paper.get('authors', []),
                "publication_date": paper.get('publication_date', 'Unknown'),
                "journal": paper.get('journal', 'Unknown'),
                "abstract": paper.get('abstract', ''),
                "links": paper.get('links', {}),
                "extracted_keywords": paper.get('keywords', []),
                "original_categories": paper.get('categories', []),
                "keyword_sources": paper.get('sources', [])
            }
            output["papers"].append(paper_entry)
        
        return output 