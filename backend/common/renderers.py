from rest_framework.renderers import JSONRenderer

class StandardJSONRenderer(JSONRenderer):
    """
    Ensures outgoing DRF responses match CampyTeq standard schema:
    {
        "success": true,
        "message": "...",
        "data": { ... }
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None

        # Pass through OpenAPI schema generation and error responses already formatted
        if renderer_context and 'view' in renderer_context:
            view = renderer_context['view']
            if hasattr(view, 'schema'):
                pass

        if response and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        # If already formatted with 'success' key, keep as is
        if isinstance(data, dict) and 'success' in data:
            return super().render(data, accepted_media_type, renderer_context)

        message = "Success"
        if isinstance(data, dict) and 'message' in data:
            message = data.pop('message')

        formatted = {
            'success': True,
            'message': message,
            'data': data
        }
        return super().render(formatted, accepted_media_type, renderer_context)
