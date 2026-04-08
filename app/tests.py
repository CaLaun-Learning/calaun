from django.test import TestCase
from logic.utils import Eval
import json
from django.urls import reverse


class ViewTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.url = '/'  # Direct URL instead of reverse('main')

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
        self.assertTrue(len(response.json()['text']) > 0)

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
        self.assertTrue(len(response.json()['text']) > 0)

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
