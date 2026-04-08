"""
Simple analytics for tracking usage.

Tracks:
- Chatbot requests (per IP, timestamp, calculus-related or not)
- Solver requests (expression type: derivative, integral, limit)
- Rate limiting state
"""

import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from django.http import JsonResponse

logger = logging.getLogger('calc_tutor')


class Analytics:
    """Simple in-memory analytics tracker.
    
    For production with multiple workers, replace with Redis or database.
    """
    
    def __init__(self):
        self.chatbot_requests = []
        self.solver_requests = []
        self._rate_limits = defaultdict(list)  # IP -> list of timestamps
        
    def log_chatbot_request(self, ip_address, was_calculus_related=True, 
                            had_steps_context=False):
        """Log a chatbot API request."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip_address,
            'calculus_related': was_calculus_related,
            'had_steps': had_steps_context,
        }
        self.chatbot_requests.append(entry)
        
        # Keep only last 10000 entries in memory
        if len(self.chatbot_requests) > 10000:
            self.chatbot_requests = self.chatbot_requests[-5000:]
        
        logger.info(f"Chatbot request from {ip_address[:12]}... "
                   f"(calculus={was_calculus_related}, steps={had_steps_context})")
    
    def log_solver_request(self, ip_address, expression_type):
        """Log a solver request (derivative, integral, limit, other)."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip_address,
            'type': expression_type,
        }
        self.solver_requests.append(entry)
        
        # Keep only last 10000 entries
        if len(self.solver_requests) > 10000:
            self.solver_requests = self.solver_requests[-5000:]
        
        logger.info(f"Solver request from {ip_address[:12]}... ({expression_type})")
    
    def check_rate_limit(self, ip_address, max_requests=10, window_seconds=60):
        """
        Check if IP is rate limited.
        
        Default: 10 requests per minute per IP for chatbot.
        This is conservative to ensure fair access for all users.
        
        Returns:
            tuple: (is_allowed, requests_remaining, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old entries
        self._rate_limits[ip_address] = [
            ts for ts in self._rate_limits[ip_address] 
            if ts > window_start
        ]
        
        current_count = len(self._rate_limits[ip_address])
        
        if current_count >= max_requests:
            # Find when the oldest request will expire
            oldest = min(self._rate_limits[ip_address])
            retry_after = int(oldest + window_seconds - now) + 1
            return False, 0, retry_after
        
        # Add this request
        self._rate_limits[ip_address].append(now)
        remaining = max_requests - current_count - 1
        
        return True, remaining, 0
    
    def get_stats(self, hours=24):
        """Get usage statistics for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        recent_chatbot = [r for r in self.chatbot_requests 
                         if r['timestamp'] > cutoff_str]
        recent_solver = [r for r in self.solver_requests 
                        if r['timestamp'] > cutoff_str]
        
        # Count by type
        solver_by_type = defaultdict(int)
        for r in recent_solver:
            solver_by_type[r['type']] += 1
        
        # Unique IPs
        chatbot_ips = set(r['ip'] for r in recent_chatbot)
        solver_ips = set(r['ip'] for r in recent_solver)
        
        return {
            'period_hours': hours,
            'chatbot': {
                'total_requests': len(recent_chatbot),
                'unique_users': len(chatbot_ips),
                'calculus_related': sum(1 for r in recent_chatbot if r['calculus_related']),
                'with_steps_context': sum(1 for r in recent_chatbot if r['had_steps']),
            },
            'solver': {
                'total_requests': len(recent_solver),
                'unique_users': len(solver_ips),
                'by_type': dict(solver_by_type),
            }
        }


# Global analytics instance
_analytics = None


def get_analytics():
    """Get or create the analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics


def get_client_ip(request):
    """Extract client IP from request, handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def rate_limit_chatbot(max_requests=10, window_seconds=60):
    """
    Decorator to rate limit chatbot requests per IP.
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            analytics = get_analytics()
            
            is_allowed, remaining, retry_after = analytics.check_rate_limit(
                ip, max_requests, window_seconds
            )
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {ip[:12]}...")
                return JsonResponse({
                    'text': (
                        "You've sent too many messages. "
                        f"Please wait {retry_after} seconds and try again. "
                        "This limit helps ensure fair access for all students."
                    ),
                    'rate_limited': True,
                    'retry_after': retry_after,
                }, status=429)
            
            response = view_func(request, *args, **kwargs)
            
            # Add rate limit headers
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Remaining'] = remaining
                response['X-RateLimit-Limit'] = max_requests
            
            return response
        return wrapper
    return decorator
