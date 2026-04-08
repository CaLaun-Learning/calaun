"""
LLM Step Helper - An AI assistant that helps students understand calculus steps.

Uses OpenAI-compatible API to answer questions about the solution steps.
Only answers questions related to calculus or the current problem.
"""

import os
import re
from openai import OpenAI


# System prompt that constrains the LLM to calculus topics only
SYSTEM_PROMPT = """You are a helpful calculus tutor assistant called Calc Bot. Your role is to help students understand step-by-step solutions for derivatives, integrals, and limits.

RULES:
1. Only answer questions about calculus (derivatives, integrals, limits, related rates, optimization, etc.)
2. Only answer questions related to the current problem steps if provided
3. If a student asks about something unrelated to calculus or math, politely redirect them
4. Keep explanations clear, concise, and appropriate for calculus students
5. Use mathematical notation when helpful (you can use LaTeX: \\( inline \\) or \\[ display \\])
6. Be encouraging and supportive

If the student's question is NOT about calculus or the current problem, respond with:
"I'm here to help with calculus! Feel free to ask me about derivatives, integrals, limits, or any of the steps shown above."

When steps are provided, reference them specifically to help the student understand."""


class LLMStepHelper:
    """An LLM-based assistant that helps students understand calculus solution steps."""
    
    def __init__(self, api_key=None, base_url=None, model=None):
        """
        Initialize the LLM helper.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Optional base URL for OpenAI-compatible APIs
            model: Model to use (defaults to OPENAI_MODEL env var or gpt-4o-mini)
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.base_url = base_url or os.environ.get('OPENAI_BASE_URL')
        self.model = model or os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        client_kwargs = {'api_key': self.api_key}
        if self.base_url:
            client_kwargs['base_url'] = self.base_url
        
        self.client = OpenAI(**client_kwargs)
        
        # Keywords for calculus topic detection
        self.calculus_keywords = {
            'derivative', 'integral', 'limit', 'differentiate', 'integrate',
            'calculus', 'function', 'rule', 'chain', 'power', 'product',
            'quotient', 'substitution', 'parts', 'sin', 'cos', 'tan',
            'log', 'ln', 'exponential', 'antiderivative', 'slope', 'tangent',
            'rate', 'change', 'continuous', 'lhopital', "l'hopital",
            'indeterminate', 'infinity', 'converge', 'diverge', 'step',
            'why', 'how', 'what', 'explain', 'understand', 'confused',
            'help', 'mean', 'formula', 'equation', 'solve', 'simplify',
            'factor', 'expand', 'coefficient', 'constant', 'variable',
            'theorem', 'proof', 'definition', 'notation', 'dx', 'dy',
        }
    
    def _is_calculus_related(self, message, has_steps=False):
        """
        Check if the message is related to calculus or the current problem.
        
        Args:
            message: The user's message
            has_steps: Whether solution steps are provided as context
            
        Returns:
            True if the message seems calculus-related
        """
        message_lower = message.lower()
        
        # If we have steps and they're asking about them, it's valid
        if has_steps:
            step_references = ['step', 'this', 'that', 'here', 'above', 'why', 'how', 'what']
            if any(ref in message_lower for ref in step_references):
                return True
        
        # Check for calculus keywords
        for keyword in self.calculus_keywords:
            if keyword in message_lower:
                return True
        
        # Check for math patterns (numbers, operators, variables)
        math_pattern = r'[xyz]\s*[\+\-\*\/\^]|d[xy]|∫|\d+\s*[\+\-\*\/\^]'
        if re.search(math_pattern, message_lower):
            return True
        
        return False
    
    def _format_steps_context(self, steps_html):
        """
        Extract readable text from HTML steps for context.
        
        Args:
            steps_html: HTML content of the solution steps
            
        Returns:
            Plain text representation of the steps
        """
        if not steps_html:
            return ""
        
        # Remove HTML tags but preserve structure
        text = re.sub(r'<script[^>]*>.*?</script>', '', steps_html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        
        # Convert common elements to readable format
        text = re.sub(r'<h\d[^>]*>', '\n## ', text)
        text = re.sub(r'</h\d>', '\n', text)
        text = re.sub(r'<li[^>]*>', '\n• ', text)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        
        # Preserve LaTeX delimiters
        text = re.sub(r'\\$$', r'\\(', text)
        text = re.sub(r'\\$$', r'\\)', text)
        text = re.sub(r'\\\[', r'\\[', text)
        text = re.sub(r'\\\]', r'\\]', text)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def get_response(self, message, steps_html=None, conversation_history=None):
        """
        Get a response from the LLM.
        
        Args:
            message: The user's question
            steps_html: Optional HTML content of the current solution steps
            conversation_history: Optional list of previous messages
            
        Returns:
            The assistant's response text
        """
        has_steps = bool(steps_html)
        
        # Check if the question is calculus-related
        if not self._is_calculus_related(message, has_steps):
            return (
                "I'm here to help with calculus! Feel free to ask me about "
                "derivatives, integrals, limits, or any of the steps shown above."
            )
        
        # Build the messages list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add steps context if available
        if steps_html:
            steps_text = self._format_steps_context(steps_html)
            if steps_text:
                context_msg = (
                    f"The student is looking at the following solution steps:\n\n"
                    f"---\n{steps_text}\n---\n\n"
                    f"Help them understand these steps if they ask about them."
                )
                messages.append({"role": "system", "content": context_msg})
        
        # Add conversation history if provided
        if conversation_history:
            for entry in conversation_history[-10:]:  # Keep last 10 messages
                messages.append({
                    "role": entry.get("role", "user"),
                    "content": entry.get("content", "")
                })
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Log the error but return a friendly message
            print(f"LLM API error: {e}")
            return (
                "I'm having trouble connecting right now. "
                "Please try again in a moment."
            )


# Singleton instance
_llm_helper = None


def get_llm_helper():
    """Get or create the LLM helper instance."""
    global _llm_helper
    if _llm_helper is None:
        try:
            _llm_helper = LLMStepHelper()
        except ValueError:
            # API key not configured
            return None
    return _llm_helper


def llm_response(message, steps_html=None, conversation_history=None):
    """
    Get an LLM response for the given message.
    
    Args:
        message: The user's question
        steps_html: Optional HTML content of current solution steps
        conversation_history: Optional list of previous messages
        
    Returns:
        The assistant's response, or a fallback if LLM is not available
    """
    helper = get_llm_helper()
    if helper is None:
        return (
            "AI assistant is not configured. Please set the OPENAI_API_KEY "
            "environment variable to enable this feature."
        )
    return helper.get_response(message, steps_html, conversation_history)
