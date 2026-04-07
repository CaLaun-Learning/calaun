from django.test import TestCase
from logic.utils import Eval
from chatbot.math_chat import MathChatbot, chatbot_response
import json
from django.urls import reverse


class ViewTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('main')

    def test_get_main_page(self):
        """
        Test that the main page can be loaded.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ApiTestCase(TestCase):
    """
    Tests to make sure that the chatBot app is
    properly working with the Django app.
    """

    def setUp(self):
        super().setUp()
        self.api_url = reverse('chatbot')

    def test_post(self):
        """
        Test that a response is returned.
        """
        data = {
            'text': 'How are you?'
        }
        response = self.client.post(
            self.api_url,
            data=json.dumps(data),
            content_type='application/json',
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text', response.json())

    def test_other_post(self):
        """
        Test that a response is returned.
        """
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'text': 'Im stuck'
            }),
            content_type='application/json',
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text', response.json())
        self.assertEqual(len(response.json()['text']), 1)

    def test_post_unicode(self):
        """
        Test that a response is returned.
        """
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'text': u'سلام'
            }),
            content_type='application/json',
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text', response.json())
        self.assertEqual(len(response.json()['text']), 1)

    def test_escaped_unicode_post(self):
        """
        Test that unicode reponce
        """
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'text': '\u2013'
            }),
            content_type='application/json',
            format=json
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text', response.json())

    def test_post_tags(self):
        post_data = {
            'text': 'Good morning.',
            'tags': [
                'user:jen@example.com'
            ]
        }
        response = self.client.post(
            self.api_url,
            data=json.dumps(post_data),
            content_type='application/json',
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text', response.json())

    def test_get(self):
        response = self.client.get(self.api_url)

        self.assertEqual(response.status_code, 405)

    def test_patch(self):
        response = self.client.patch(self.api_url)

        self.assertEqual(response.status_code, 405)

    def test_put(self):
        response = self.client.put(self.api_url)

        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.api_url)

        self.assertEqual(response.status_code, 405)


class TestEval(TestCase):
    def test_eval_simple_arithmetic(self):
        e = Eval()
        self.assertEqual(e.eval("1+1"), "2")
        self.assertEqual(e.eval("1+1\n"), "2")

    def test_eval_assignment(self):
        e = Eval()
        self.assertEqual(e.eval("a=1+1"), "")
        self.assertEqual(e.eval("a=1+1\n"), "")

    def test_eval_assignment_and_use(self):
        e = Eval()
        self.assertEqual(e.eval("a=1+1\na"), "2")
        self.assertEqual(e.eval("a=1+1\na\n"), "2")

    def test_eval_multiple_assignments(self):
        e = Eval()
        self.assertEqual(e.eval("a=1+1\na=3"), "")
        self.assertEqual(e.eval("a=1+1\na=3\n"), "")

    def test_eval_function_definition(self):
        e = Eval()
        self.assertEqual(e.eval("\ndef f(x):\n\treturn x**2\nf(3)"), "9")

    def test_eval_function_no_return(self):
        e = Eval()
        self.assertEqual(e.eval("\ndef f(x):\n\treturn x**2\nf(3)\na = 5"), "")

    def test_eval_conditional_true(self):
        e = Eval()
        self.assertEqual(
            e.eval("\ndef f(x):\n\treturn x**2\nif f(3) == 9:\n\ta = 1\nelse:\n\ta = 0\na"), "1")

    def test_eval_conditional_false(self):
        e = Eval()
        self.assertEqual(
            e.eval("\ndef f(x):\n\treturn x**2 + 1\nif f(3) == 9:\n\ta = 1\nelse:\n\ta = 0\na"), "0")

    def test_eval_undefined_variable(self):
        e = Eval()
        result = e.eval("xxxx")
        self.assertTrue(result.startswith("Traceback"))

    def test_eval_undefined_in_function(self):
        e = Eval()
        result = e.eval("""\
def f(x):
    return x**2 + 1 + y
if f(3) == 9:
    a = 1
else:
    a = 0
a
""")
        self.assertTrue(result.startswith("Traceback"))


class TestMathChatbot(TestCase):
    """Tests for the math-focused chatbot."""
    
    def setUp(self):
        self.bot = MathChatbot()
    
    def test_greeting(self):
        """Test that greetings get a friendly response."""
        response = self.bot.get_response("hello")
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
    
    def test_power_rule_question(self):
        """Test that power rule questions get relevant answers."""
        response = self.bot.get_response("what is the power rule")
        # Should mention exponents or x^n
        self.assertTrue(
            "power" in response.lower() or
            "exponent" in response.lower() or
            "x^n" in response or
            "x^" in response
        )
    
    def test_chain_rule_question(self):
        """Test that chain rule questions get relevant answers."""
        response = self.bot.get_response("explain the chain rule")
        # Should mention chain, composite, outer/inner, derivative, or give an example
        self.assertTrue(
            "chain" in response.lower() or
            "composite" in response.lower() or
            "outer" in response.lower() or
            "inner" in response.lower() or
            "layers" in response.lower() or
            "derivative" in response.lower() or
            "differentiate" in response.lower() or
            "f(g(x))" in response or
            "peeling" in response.lower()
        )
    
    def test_non_math_question(self):
        """Test that non-math questions are deflected."""
        response = self.bot.get_response("what's the weather like")
        # Should redirect to math topics
        self.assertTrue(
            "calculus" in response.lower() or 
            "math" in response.lower() or
            "derivative" in response.lower() or
            "integral" in response.lower()
        )
    
    def test_integration_by_parts(self):
        """Test integration by parts questions."""
        response = self.bot.get_response("how do I use integration by parts")
        self.assertTrue(
            "parts" in response.lower() or 
            "uv" in response.lower() or
            "∫" in response or
            "liate" in response.lower() or
            "integrate" in response.lower() or
            "differentiate" in response.lower()
        )
    
    def test_lhopital_rule(self):
        """Test L'Hopital's rule questions."""
        response = self.bot.get_response("when do I use l'hopital's rule")
        self.assertTrue(
            "indeterminate" in response.lower() or 
            "0/0" in response or
            "derivative" in response.lower()
        )
    
    def test_empty_input(self):
        """Test handling of empty input."""
        response = self.bot.get_response("")
        self.assertIsNotNone(response)
    
    def test_chatbot_response_function(self):
        """Test the backwards-compatible chatbot_response function."""
        response = chatbot_response("what is a derivative")
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
