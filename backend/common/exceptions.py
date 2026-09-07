from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
    NotFound,
    MethodNotAllowed,
    Throttled,
)
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Standardized DRF exception handler matching CampyTeq enterprise spec.
    """
    response = exception_handler(exc, context)

    if response is not None:
        code = 'ERROR'
        message = 'An error occurred while processing your request.'

        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            code = 'UNAUTHENTICATED'
            message = getattr(exc, 'detail', 'Authentication credentials were not provided or are invalid.')
        elif isinstance(exc, PermissionDenied):
            code = 'PERMISSION_DENIED'
            message = 'You do not have permission to access this resource.'
        elif isinstance(exc, ValidationError):
            code = 'VALIDATION_ERROR'
            message = 'Invalid request payload or parameters.'
        elif isinstance(exc, NotFound):
            code = 'NOT_FOUND'
            message = getattr(exc, 'detail', 'The requested resource was not found.')
        elif isinstance(exc, MethodNotAllowed):
            code = 'METHOD_NOT_ALLOWED'
            message = f'Method {context["request"].method} not allowed on this endpoint.'
        elif isinstance(exc, Throttled):
            code = 'RATE_LIMITED'
            message = f'Request limit exceeded. Available in {exc.wait} seconds.'
        else:
            if hasattr(exc, 'detail'):
                message = str(exc.detail)

        # Build clean errors payload
        errors = response.data if isinstance(response.data, dict) else {'detail': response.data}

        # If message was a dict or list, extract first item
        if isinstance(message, (dict, list)):
            message = 'Validation failed.'

        response.data = {
            'success': False,
            'message': str(message),
            'code': code,
            'errors': errors,
        }

    return response
