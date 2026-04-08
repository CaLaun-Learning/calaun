"""Tests for the analytics module."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time

from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from app.analytics import (
    Analytics, get_analytics, get_client_ip, rate_limit_chatbot
)


class TestAnalytics(TestCase):
    """Tests for the Analytics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics = Analytics()
    
    def test_log_chatbot_request(self):
        """Test logging a chatbot request."""
        self.analytics.log_chatbot_request(
            ip_address='192.168.1.1',
            was_calculus_related=True,
            had_steps_context=False
        )
        
        self.assertEqual(len(self.analytics.chatbot_requests), 1)
        entry = self.analytics.chatbot_requests[0]
        self.assertEqual(entry['ip'], '192.168.1.1')
        self.assertTrue(entry['calculus_related'])
        self.assertFalse(entry['had_steps'])
    
    def test_log_solver_request(self):
        """Test logging a solver request."""
        self.analytics.log_solver_request(
            ip_address='192.168.1.2',
            expression_type='derivative'
        )
        
        self.assertEqual(len(self.analytics.solver_requests), 1)
        entry = self.analytics.solver_requests[0]
        self.assertEqual(entry['ip'], '192.168.1.2')
        self.assertEqual(entry['type'], 'derivative')
    
    def test_rate_limit_allows_under_limit(self):
        """Test that requests under limit are allowed."""
        ip = '192.168.1.3'
        
        # First 10 requests should be allowed
        for i in range(10):
            is_allowed, remaining, retry_after = self.analytics.check_rate_limit(
                ip, max_requests=10, window_seconds=60
            )
            self.assertTrue(is_allowed, f"Request {i+1} should be allowed")
            self.assertEqual(remaining, 10 - i - 1)
            self.assertEqual(retry_after, 0)
    
    def test_rate_limit_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        ip = '192.168.1.4'
        
        # Use up the limit
        for _ in range(10):
            self.analytics.check_rate_limit(ip, max_requests=10, window_seconds=60)
        
        # 11th request should be blocked
        is_allowed, remaining, retry_after = self.analytics.check_rate_limit(
            ip, max_requests=10, window_seconds=60
        )
        
        self.assertFalse(is_allowed)
        self.assertEqual(remaining, 0)
        self.assertGreater(retry_after, 0)
    
    def test_rate_limit_independent_per_ip(self):
        """Test that rate limits are tracked per IP."""
        ip1 = '192.168.1.5'
        ip2 = '192.168.1.6'
        
        # Use up IP1's limit
        for _ in range(10):
            self.analytics.check_rate_limit(ip1, max_requests=10, window_seconds=60)
        
        # IP2 should still be allowed
        is_allowed, _, _ = self.analytics.check_rate_limit(
            ip2, max_requests=10, window_seconds=60
        )
        self.assertTrue(is_allowed)
    
    def test_get_stats(self):
        """Test getting usage statistics."""
        # Add some requests
        self.analytics.log_chatbot_request('ip1', True, False)
        self.analytics.log_chatbot_request('ip1', True, True)
        self.analytics.log_chatbot_request('ip2', False, False)
        
        self.analytics.log_solver_request('ip1', 'derivative')
        self.analytics.log_solver_request('ip2', 'integral')
        self.analytics.log_solver_request('ip3', 'derivative')
        
        stats = self.analytics.get_stats(hours=1)
        
        self.assertEqual(stats['chatbot']['total_requests'], 3)
        self.assertEqual(stats['chatbot']['unique_users'], 2)
        self.assertEqual(stats['chatbot']['calculus_related'], 2)
        self.assertEqual(stats['chatbot']['with_steps_context'], 1)
        
        self.assertEqual(stats['solver']['total_requests'], 3)
        self.assertEqual(stats['solver']['unique_users'], 3)
        self.assertEqual(stats['solver']['by_type']['derivative'], 2)
        self.assertEqual(stats['solver']['by_type']['integral'], 1)
    
    def test_memory_limit_chatbot(self):
        """Test that chatbot requests are trimmed at memory limit."""
        # Add more than 10000 entries
        for i in range(10005):
            self.analytics.log_chatbot_request(f'ip{i}', True, False)
        
        # Should be trimmed to ~5000 (5000 base + up to 5 more before next trim)
        self.assertLessEqual(len(self.analytics.chatbot_requests), 5005)
        self.assertGreaterEqual(len(self.analytics.chatbot_requests), 5000)
    
    def test_memory_limit_solver(self):
        """Test that solver requests are trimmed at memory limit."""
        # Add more than 10000 entries
        for i in range(10005):
            self.analytics.log_solver_request(f'ip{i}', 'derivative')
        
        # Should be trimmed to ~5000 (5000 base + up to 5 more before next trim)
        self.assertLessEqual(len(self.analytics.solver_requests), 5005)
        self.assertGreaterEqual(len(self.analytics.solver_requests), 5000)


class TestGetClientIP(TestCase):
    """Tests for the get_client_ip function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
    
    def test_get_ip_from_remote_addr(self):
        """Test getting IP from REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_get_ip_from_x_forwarded_for(self):
        """Test getting IP from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')
    
    def test_get_ip_x_forwarded_for_single(self):
        """Test getting IP from single X-Forwarded-For value."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '198.51.100.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '198.51.100.1')


class TestRateLimitDecorator(TestCase):
    """Tests for the rate_limit_chatbot decorator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        
        # Reset analytics for each test
        import app.analytics
        app.analytics._analytics = None
    
    def test_decorator_allows_request(self):
        """Test that decorator allows requests under limit."""
        @rate_limit_chatbot(max_requests=5, window_seconds=60)
        def dummy_view(request):
            return JsonResponse({'text': 'ok'})
        
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        response = dummy_view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-RateLimit-Limit'], '5')
    
    def test_decorator_blocks_over_limit(self):
        """Test that decorator blocks requests over limit."""
        @rate_limit_chatbot(max_requests=3, window_seconds=60)
        def dummy_view(request):
            return JsonResponse({'text': 'ok'})
        
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.101'
        
        # Make 3 requests (within limit)
        for _ in range(3):
            dummy_view(request)
        
        # 4th request should be blocked
        response = dummy_view(request)
        
        self.assertEqual(response.status_code, 429)
        self.assertIn('rate_limited', response.content.decode())
