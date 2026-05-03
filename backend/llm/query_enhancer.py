"""
Query enhancer - improves search queries using LLM
"""
from typing import List, Dict
from llm.ollama_client import OllamaClient
from utils.logger import setup_logger

logger = setup_logger('query_enhancer')

class QueryEnhancer:
    """Enhances user queries for better search results"""
    
    def __init__(self):
        self.llm = OllamaClient()
        logger.info("Query enhancer initialized")
    
    def enhance_query(self, user_query: str, file_type: str = None) -> str:
        """
        Enhance user query for better search
        
        Args:
            user_query: Original user query
            file_type: Optional file type filter
            
        Returns:
            Enhanced search query
        """
        logger.info(f"Enhancing query: '{user_query}'")
        
        system_prompt = """You are a search query optimizer for a file finder system.
Your job is to convert casual user queries into better search terms.

Rules:
1. Extract key terms that would help find the file
2. Expand abbreviations (e.g., "ppt" -> "presentation powerpoint")
3. Add related terms (e.g., "budget" -> "budget financial expenses")
4. Remove filler words (the, a, my, etc.)
5. Keep it concise (3-8 key words)
6. Return ONLY the enhanced query, no explanation

Examples:
User: "that presentation about sales from last month"
Enhanced: "sales presentation report monthly"

User: "my budget spreadsheet"
Enhanced: "budget financial spreadsheet expenses"

User: "python code for processing data"
Enhanced: "python script data processing analysis"
"""

        prompt = f"""Original query: "{user_query}"
{f'File type: {file_type}' if file_type else ''}

Enhanced query:"""

        try:
            enhanced = self.llm.generate(prompt, system=system_prompt, temperature=0.5)
            
            # Clean up response
            enhanced = enhanced.strip().strip('"').strip("'")
            
            # If LLM returned too much, use original
            if len(enhanced.split()) > 15:
                logger.warning("Enhanced query too long, using original")
                enhanced = user_query
            
            logger.info(f"Enhanced query: '{enhanced}'")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing query: {e}")
            return user_query
    
    def generate_search_variations(self, query: str, count: int = 3) -> List[str]:
        """
        Generate alternative search queries
        
        Args:
            query: Original query
            count: Number of variations to generate
            
        Returns:
            List of query variations
        """
        system_prompt = """Generate alternative search queries that mean the same thing.
Use synonyms and different phrasings.
Return one query per line, no numbering or extra text."""

        prompt = f"""Original query: "{query}"

Generate {count} alternative queries:"""

        try:
            response = self.llm.generate(prompt, system=system_prompt, temperature=0.7)
            
            # Split into lines and clean
            variations = [
                line.strip().strip('"').strip("'").strip('-').strip()
                for line in response.split('\n')
                if line.strip()
            ]
            
            # Remove empty and duplicates
            variations = list(dict.fromkeys([v for v in variations if v]))
            
            return variations[:count]
            
        except Exception as e:
            logger.error(f"Error generating variations: {e}")
            return [query]
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract key terms from text
        
        Args:
            text: Input text
            max_keywords: Maximum keywords to extract
            
        Returns:
            List of keywords
        """
        system_prompt = f"""Extract the {max_keywords} most important keywords from the text.
Return only the keywords, one per line, no explanation."""

        prompt = f"""Text: "{text}"

Keywords:"""

        try:
            response = self.llm.generate(prompt, system=system_prompt, temperature=0.3)
            
            keywords = [
                line.strip().strip('"').strip("'").strip('-').strip()
                for line in response.split('\n')
                if line.strip()
            ]
            
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

if __name__ == "__main__":
    # Test query enhancer
    print("\n" + "="*70)
    print("Testing Query Enhancer")
    print("="*70 + "\n")
    
    enhancer = QueryEnhancer()
    
    # Test enhancement
    test_queries = [
        "that presentation about sales from last month",
        "my budget spreadsheet",
        "python code for processing data",
        "the report we made yesterday",
        "invoice from acme corp"
    ]
    
    for query in test_queries:
        print(f"Original: '{query}'")
        enhanced = enhancer.enhance_query(query)
        print(f"Enhanced: '{enhanced}'")
        print()
    
    # Test variations
    print("="*70)
    print("Testing Query Variations")
    print("="*70 + "\n")
    
    test_query = "financial report"
    print(f"Original: '{test_query}'")
    print("Variations:")
    
    variations = enhancer.generate_search_variations(test_query)
    for i, var in enumerate(variations, 1):
        print(f"  {i}. {var}")
    
    print()
    
    # Test keyword extraction
    print("="*70)
    print("Testing Keyword Extraction")
    print("="*70 + "\n")
    
    test_text = "Annual sales report for Q4 2024 showing revenue growth and market analysis"
    print(f"Text: '{test_text}'")
    print("Keywords:")
    
    keywords = enhancer.extract_keywords(test_text)
    for keyword in keywords:
        print(f"  - {keyword}")