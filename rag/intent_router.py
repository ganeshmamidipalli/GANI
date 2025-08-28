import re
from typing import Dict, List

class IntentRouter:
    def __init__(self):
        # Define keyword patterns for each intent
        self.intent_patterns = {
            'intro': [
                r'\b(intro|introduction|background|about|who are you|elevator pitch|tell me about yourself|your story)\b',
                r'\b(ganesh|gani|personal|bio|story|experience|journey)\b',
                r'\b(where.*from|what.*do|how.*start|beginning|origin)\b'
            ],
            'technical': [
                r'\b(technical|project|code|algorithm|implementation|architecture|system|design|development)\b',
                r'\b(WSDM|machine learning|ML|AI|data|research|paper|methodology|approach|experiment)\b',
                r'\b(performance|metrics|results|evaluation|model|training|optimization|algorithm)\b',
                r'\b(deep learning|neural networks|computer vision|NLP|data science|statistics)\b',
                r'\b(implementation|code|programming|software|engineering|technical details)\b'
            ],
            'hr': [
                r'\b(conflict|teamwork|collaboration|challenge|difficulty|problem|situation|handled|resolved)\b',
                r'\b(behavioral|STAR|example|experience|time when|tell me about a time|situation)\b',
                r'\b(leadership|mentor|help|support|communication|feedback|interpersonal)\b',
                r'\b(work.*team|handle.*conflict|deal.*difficult|resolve.*issue|teamwork)\b',
                r'\b(communication|collaboration|feedback|mentoring|helping others)\b'
            ],
            'manager': [
                r'\b(lead|manage|team|prioritize|roadmap|strategy|decision|tradeoff|resource)\b',
                r'\b(planning|execution|delivery|timeline|budget|stakeholder|coordinate)\b',
                r'\b(mentor|coach|develop|performance|review|feedback|growth|leadership)\b',
                r'\b(team.*lead|project.*manage|prioritize.*work|make.*decision|strategy)\b',
                r'\b(roadmap|planning|execution|delivery|timeline|budget|stakeholder)\b'
            ]
        }
        
        # Compile regex patterns
        self.compiled_patterns = {
            intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for intent, patterns in self.intent_patterns.items()
        }
    
    def route_intent(self, question: str) -> str:
        """
        Route a question to the appropriate intent category.
        
        Args:
            question: The user's question
            
        Returns:
            str: One of 'intro', 'technical', 'hr', 'manager', or 'technical' as default
        """
        question_lower = question.lower()
        
        # Score each intent based on pattern matches
        intent_scores = {}
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(question_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Find the intent with the highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # If no patterns match, default to technical
        if best_intent[1] == 0:
            return 'technical'
        
        return best_intent[0]
    
    def get_intent_confidence(self, question: str, intent: str) -> float:
        """
        Get confidence score for the routed intent.
        
        Args:
            question: The user's question
            intent: The routed intent
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        question_lower = question.lower()
        patterns = self.compiled_patterns.get(intent, [])
        
        if not patterns:
            return 0.0
        
        matches = 0
        for pattern in patterns:
            if pattern.search(question_lower):
                matches += 1
        
        return min(matches / len(patterns), 1.0)
