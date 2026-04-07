"""
Math Chatbot - A retrieval-based chatbot for calculus questions.

Uses TF-IDF vectorization and cosine similarity to match user questions
to predefined intents. Only answers math-related questions.
"""

import json
import pathlib
import random
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DIR_NAME = pathlib.Path(__file__).parent


class MathChatbot:
    """A closed-domain chatbot that only answers calculus questions."""
    
    def __init__(self, intents_path=None):
        if intents_path is None:
            intents_path = DIR_NAME / 'data' / 'intents.json'
        
        with open(intents_path, 'r') as f:
            data = json.load(f)
        
        self.intents = data['intents']
        self.patterns = []
        self.pattern_to_intent = []
        
        # Build pattern database
        for intent in self.intents:
            for pattern in intent['patterns']:
                self.patterns.append(self._preprocess(pattern))
                self.pattern_to_intent.append(intent)
        
        # Create TF-IDF vectorizer
        if self.patterns:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words='english',
                max_features=1000
            )
            self.pattern_vectors = self.vectorizer.fit_transform(self.patterns)
        else:
            self.vectorizer = None
            self.pattern_vectors = None
        
        # Fallback intent
        self.fallback = next(
            (i for i in self.intents if i['tag'] == 'fallback'),
            {'responses': ["I'm not sure about that. Try asking about derivatives, integrals, or limits."]}
        )
        
        # Math keywords for filtering
        self.math_keywords = {
            'derivative', 'integral', 'limit', 'differentiate', 'integrate',
            'calculus', 'function', 'rule', 'chain', 'power', 'product',
            'quotient', 'substitution', 'parts', 'sin', 'cos', 'tan',
            'log', 'ln', 'exponential', 'e^x', 'x^', 'dx', 'dy',
            'antiderivative', 'slope', 'tangent', 'rate', 'change',
            'continuous', 'discontinuous', 'lhopital', "l'hopital",
            'indeterminate', 'infinity', 'converge', 'diverge'
        }
    
    def _preprocess(self, text):
        """Clean and normalize text."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s\'^]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _is_math_related(self, text):
        """Check if the question seems math-related."""
        text_lower = text.lower()
        
        # Check for math keywords
        for keyword in self.math_keywords:
            if keyword in text_lower:
                return True
        
        # Check for math symbols/patterns
        math_patterns = [r'\d+', r'x\^', r'd/dx', r'∫', r'lim', r'\+c', r'=']
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def get_response(self, user_input):
        """Get a response for the user's input."""
        if not user_input or not user_input.strip():
            return "Could you repeat that?"
        
        processed = self._preprocess(user_input)
        
        # Handle greetings and basic conversation
        greeting_words = {'hi', 'hello', 'hey', 'howdy', 'yo'}
        goodbye_words = {'bye', 'goodbye', 'later', 'see you'}
        thanks_words = {'thanks', 'thank', 'appreciate'}
        
        words = set(processed.split())
        
        if words & greeting_words and len(words) <= 3:
            intent = next((i for i in self.intents if i['tag'] == 'greeting'), self.fallback)
            return random.choice(intent['responses'])
        
        if words & goodbye_words:
            intent = next((i for i in self.intents if i['tag'] == 'goodbye'), self.fallback)
            return random.choice(intent['responses'])
        
        if words & thanks_words:
            intent = next((i for i in self.intents if i['tag'] == 'thanks'), self.fallback)
            return random.choice(intent['responses'])
        
        # Check if it's a math question
        if not self._is_math_related(user_input):
            # Check if it matches any pattern first
            if self.vectorizer and self.pattern_vectors is not None:
                user_vector = self.vectorizer.transform([processed])
                similarities = cosine_similarity(user_vector, self.pattern_vectors)[0]
                
                if similarities.max() < 0.15:  # Very low similarity
                    not_math = next(
                        (i for i in self.intents if i['tag'] == 'not_math'),
                        self.fallback
                    )
                    return random.choice(not_math['responses'])
        
        # Find best matching intent using TF-IDF similarity
        if self.vectorizer is None or self.pattern_vectors is None:
            return random.choice(self.fallback['responses'])
        
        user_vector = self.vectorizer.transform([processed])
        similarities = cosine_similarity(user_vector, self.pattern_vectors)[0]
        
        # Get the best match
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        
        # Confidence threshold
        if best_score < 0.2:
            return random.choice(self.fallback['responses'])
        
        matched_intent = self.pattern_to_intent[best_idx]
        return random.choice(matched_intent['responses'])


# Create a singleton instance
_chatbot = None


def get_chatbot():
    """Get or create the chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = MathChatbot()
    return _chatbot


def chatbot_response(sentence):
    """Get a response from the chatbot (backwards compatible API)."""
    bot = get_chatbot()
    return bot.get_response(sentence)


# Initialize on import
def start_chatbot(sentence):
    """Initialize the chatbot (backwards compatible)."""
    get_chatbot()


start_chatbot("begin")
