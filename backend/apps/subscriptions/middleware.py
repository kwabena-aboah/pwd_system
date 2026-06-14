"""
apps/subscriptions/middleware.py
Enforces subscription limits and feature gates on every API request.
Returns 402 Payment Required when the subscription is invalid or a
feature / limit is exceeded.
"""
import json
from django.http import JsonResponse
from django.utils import timezone


# Paths that are always allowed regardless of subscription state
ALWAYS_ALLOWED = {
    '/api/auth/',
    '/api/settings/',
    '/api/subscriptions/',
    '/api/schema/',
    '/api/docs/',
    '/admin/',
    '/media/',
    '/static/',
}

# Map API paths → feature flag that must be enabled on the plan
FEATURE_GATES = {
    '/api/audit-logs/':   'audit',
    '/api/reports/':      'reports',
}

# Map API paths → (plan attribute for limit, model to count)
LIMIT_GATES = {}  # checked inside views for finer-grained control


class SubscriptionMiddleware:
    """
    Checks:
    1. Active subscription exists (status active or trialing).
    2. Feature flag is enabled for the requested endpoint.
    3. Trial hasn't expired.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only guard API calls
        if request.path.startswith('/api/'):
            result = self._check(request)
            if result is not None:
                return result
        return self.get_response(request)

    def _is_always_allowed(self, path):
        for prefix in ALWAYS_ALLOWED:
            if path.startswith(prefix):
                return True
        return False

    def _check(self, request):
        if self._is_always_allowed(request.path):
            return None

        # Unauthenticated requests are handled by DRF's own auth
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        # Super admins bypass subscription checks
        if request.user.role == 'super_admin':
            return None

        from .models import Subscription
        sub = (
            Subscription.objects
            .filter(status__in=['active', 'trialing'])
            .select_related('plan')
            .first()
        )

        if sub is None:
            return self._deny(
                'NO_SUBSCRIPTION',
                'No active subscription found. Please subscribe to continue.',
                402,
            )

        # Check trial expiry
        if sub.status == 'trialing' and sub.trial_end:
            if sub.trial_end < timezone.now().date():
                sub.status = 'expired'
                sub.save(update_fields=['status'])
                return self._deny(
                    'TRIAL_EXPIRED',
                    'Your free trial has expired. Please upgrade to continue.',
                    402,
                )

        # Check feature gates
        for path_prefix, feature_key in FEATURE_GATES.items():
            if request.path.startswith(path_prefix):
                if not getattr(sub.plan, f'feature_{feature_key}', False):
                    return self._deny(
                        'FEATURE_NOT_AVAILABLE',
                        f'This feature is not available on your current plan. '
                        f'Please upgrade to access it.',
                        403,
                    )

        return None

    @staticmethod
    def _deny(code, message, http_status):
        return JsonResponse(
            {'error': code, 'message': message, 'upgrade_required': True},
            status=http_status,
        )
