import re
from typing import Dict, List, Any

class Verifier:
    def __init__(self):
        """
        Initialize the verifier for checking answer quality and groundedness.
        """
        pass
    
    def groundedness_score(self, answer_text: str, context_text: str) -> float:
        """
        Calculate a naive groundedness score based on citation density.
        
        Args:
            answer_text: The generated answer text
            context_text: The context used to generate the answer
            
        Returns:
            float: Groundedness score between 0.0 and 1.0
        """
        if not answer_text or not context_text:
            return 0.0
        
        # Count citations in the answer
        citation_pattern = r'\[\d+\]'
        citations = re.findall(citation_pattern, answer_text)
        citation_count = len(citations)
        
        # Count sentences in the answer
        sentence_pattern = r'[.!?]+'
        sentences = re.split(sentence_pattern, answer_text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count == 0:
            return 0.0
        
        # Calculate citation density
        citation_density = citation_count / sentence_count
        
        # Normalize to 0-1 range (0.5 citations per sentence = 1.0 score)
        groundedness = min(citation_density / 0.5, 1.0)
        
        return max(groundedness, 0.0)
    
    def build_confidence(self, groundedness: float, model_hint: float = 0.8) -> float:
        """
        Build a confidence score from groundedness and model confidence hint.
        
        Args:
            groundedness: Groundedness score from verification
            model_hint: Model's self-reported confidence (default 0.8)
            
        Returns:
            float: Combined confidence score between 0.0 and 1.0
        """
        # Weight groundedness more heavily than model hint
        groundedness_weight = 0.7
        model_weight = 0.3
        
        confidence = (groundedness * groundedness_weight) + (model_hint * model_weight)
        
        return max(0.0, min(1.0, confidence))
    
    def verify_citations(self, answer_text: str, snippets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify that citations in the answer correspond to actual snippets.
        
        Args:
            answer_text: The generated answer text
            snippets: List of snippets used as context
            
        Returns:
            Dict: Verification results and suggestions
        """
        # Extract citation numbers from answer
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, answer_text)
        
        # Check if citations are valid
        valid_citations = []
        invalid_citations = []
        
        for citation in citations:
            try:
                citation_num = int(citation)
                if 1 <= citation_num <= len(snippets):
                    valid_citations.append(citation_num)
                else:
                    invalid_citations.append(citation_num)
            except ValueError:
                invalid_citations.append(citation)
        
        # Calculate citation validity score
        total_citations = len(citations)
        valid_citation_ratio = len(valid_citations) / total_citations if total_citations > 0 else 1.0
        
        return {
            'valid_citations': valid_citations,
            'invalid_citations': invalid_citations,
            'total_citations': total_citations,
            'validity_score': valid_citation_ratio,
            'snippet_count': len(snippets)
        }
    
    def extract_citations_from_snippets(self, snippets: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract citation information from snippets for JSON response.
        
        Args:
            snippets: List of snippets with metadata
            
        Returns:
            List[Dict]: List of citation objects with url and section
        """
        citations = []
        
        for snippet in snippets:
            citation = {
                'url': snippet.get('url', ''),
                'section': snippet.get('section', '')
            }
            
            # Only add if we have a URL
            if citation['url']:
                citations.append(citation)
        
        return citations
    
    def validate_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Validate and parse JSON response from the LLM.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            Dict: Parsed response or error information
        """
        import json
        
        # Try to extract JSON from the response
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, response_text, re.DOTALL)
        
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                
                # Validate required fields
                required_fields = ['answer_short', 'answer_expanded', 'citations', 'confidence']
                missing_fields = [field for field in required_fields if field not in parsed]
                
                if missing_fields:
                    return {
                        'is_valid': False,
                        'error': f"Missing required fields: {missing_fields}",
                        'parsed': parsed
                    }
                
                return {
                    'is_valid': True,
                    'parsed': parsed
                }
                
            except json.JSONDecodeError as e:
                return {
                    'is_valid': False,
                    'error': f"JSON decode error: {str(e)}",
                    'raw_text': response_text
                }
        else:
            return {
                'is_valid': False,
                'error': "No JSON found in response",
                'raw_text': response_text
            }
