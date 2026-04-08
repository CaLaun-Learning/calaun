"""Tests for the LLM Step Helper chatbot (using Ollama)."""

import unittest
from unittest.mock import patch, MagicMock
from chatbot.llm_chat import LLMStepHelper, llm_response


class TestLLMStepHelper(unittest.TestCase):
    """Tests for the LLMStepHelper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.helper = LLMStepHelper()
    
    def test_is_calculus_related_with_keywords(self):
        """Test calculus keyword detection."""
        helper = self.helper
        
        # Should be calculus-related
        self.assertTrue(helper._is_calculus_related("What is a derivative?"))
        self.assertTrue(helper._is_calculus_related("How do I integrate this?"))
        self.assertTrue(helper._is_calculus_related("Explain the power rule"))
        self.assertTrue(helper._is_calculus_related("What is limit of sin(x)/x?"))
        
        # Should NOT be calculus-related
        self.assertFalse(helper._is_calculus_related("What's the weather today?"))
        self.assertFalse(helper._is_calculus_related("Tell me a joke"))
        self.assertFalse(helper._is_calculus_related("Hello"))
    
    def test_is_calculus_related_with_steps_context(self):
        """Test that questions about steps are considered related when steps exist."""
        helper = self.helper
        
        # Without steps context
        self.assertFalse(helper._is_calculus_related("What does this mean?", has_steps=False))
        
        # With steps context
        self.assertTrue(helper._is_calculus_related("What does this mean?", has_steps=True))
        self.assertTrue(helper._is_calculus_related("Why did we do that step?", has_steps=True))
        self.assertTrue(helper._is_calculus_related("I don't understand step 2", has_steps=True))
    
    @patch('chatbot.llm_chat.LLMStepHelper._is_ollama_available')
    def test_get_response_non_calculus(self, mock_available):
        """Test response for non-calculus questions."""
        mock_available.return_value = True
        
        response = self.helper.get_response("What's your favorite color?")
        
        self.assertIn("calculus", response.lower())
        self.assertIn("derivatives", response.lower())
    
    @patch('chatbot.llm_chat.requests.post')
    @patch('chatbot.llm_chat.LLMStepHelper._is_ollama_available')
    def test_get_response_calculus_question(self, mock_available, mock_post):
        """Test response for calculus questions."""
        mock_available.return_value = True
        
        # Mock Ollama response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "This is a test response about calculus."}
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = self.helper.get_response("How do I use the chain rule?")
        
        # Should have called the API
        mock_post.assert_called_once()
        self.assertEqual(response, "This is a test response about calculus.")
    
    @patch('chatbot.llm_chat.requests.post')
    @patch('chatbot.llm_chat.LLMStepHelper._is_ollama_available')
    def test_get_response_with_steps(self, mock_available, mock_post):
        """Test response includes steps context."""
        mock_available.return_value = True
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Test response"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        steps_html = """
        <div class="step">
            <h3>Step 1: Apply power rule</h3>
            <p>\\( \\frac{d}{dx}x^2 = 2x \\)</p>
        </div>
        """
        
        response = self.helper.get_response("Why do we multiply by 2?", steps_html=steps_html)
        
        # Should have called the API with steps context
        call_args = mock_post.call_args
        json_data = call_args.kwargs['json']
        messages = json_data['messages']
        
        # Should have system prompt, steps context, and user message
        self.assertGreaterEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[-1]['role'], 'user')
        self.assertEqual(messages[-1]['content'], "Why do we multiply by 2?")
    
    def test_format_steps_context(self):
        """Test HTML to text conversion for steps."""
        helper = self.helper
        
        html = """
        <div class="step">
            <h3>Apply power rule</h3>
            <ul>
                <li>First item</li>
                <li>Second item</li>
            </ul>
        </div>
        """
        
        text = helper._format_steps_context(html)
        
        self.assertIn("Apply power rule", text)
        self.assertIn("First item", text)
        self.assertIn("Second item", text)
        self.assertNotIn("<div>", text)
        self.assertNotIn("<h3>", text)
    
    @patch('chatbot.llm_chat.requests.post')
    @patch('chatbot.llm_chat.LLMStepHelper._is_ollama_available')
    def test_conversation_history(self, mock_available, mock_post):
        """Test that conversation history is included."""
        mock_available.return_value = True
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Test response"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        history = [
            {"role": "user", "content": "What is a derivative?"},
            {"role": "assistant", "content": "A derivative measures rate of change."}
        ]
        
        response = self.helper.get_response(
            "Can you give me an example?",
            conversation_history=history
        )
        
        call_args = mock_post.call_args
        json_data = call_args.kwargs['json']
        messages = json_data['messages']
        
        # Should include history
        user_messages = [m for m in messages if m['role'] == 'user']
        self.assertGreaterEqual(len(user_messages), 2)
    
    @patch('chatbot.llm_chat.LLMStepHelper._is_ollama_available')
    def test_ollama_not_available(self, mock_available):
        """Test response when Ollama is not running."""
        mock_available.return_value = False
        
        response = self.helper.get_response("What is a derivative?")
        
        self.assertIn("ollama", response.lower())
        self.assertIn("not available", response.lower())


class TestLLMResponseFunction(unittest.TestCase):
    """Tests for the llm_response convenience function."""
    
    @patch('chatbot.llm_chat.get_llm_helper')
    def test_llm_response_with_helper(self, mock_get_helper):
        """Test response when helper is available."""
        mock_helper = MagicMock()
        mock_helper.get_response.return_value = "Test response"
        mock_get_helper.return_value = mock_helper
        
        response = llm_response("What is a derivative?", steps_html="<div>steps</div>")
        
        mock_helper.get_response.assert_called_once_with(
            "What is a derivative?",
            "<div>steps</div>",
            None
        )
        self.assertEqual(response, "Test response")


if __name__ == '__main__':
    unittest.main()
