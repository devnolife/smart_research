from functools import wraps
from flask import jsonify, request
import logging

logger = logging.getLogger(__name__)

def validate_request(required_fields=None):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return jsonify({
                            'error': f'Missing required fields: {", ".join(missing_fields)}'
                        }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def format_response(data, status_code=200):
    """Format API response consistently"""
    try:
        response = {
            'success': True,
            'data': data,
            'timestamp': data.get('timestamp') if isinstance(data, dict) else None
        }
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return jsonify({
            'success': False,
            'error': 'Error formatting response',
            'details': str(e)
        }), 500

def handle_api_error(error_message, status_code=500, details=None):
    """Handle API errors consistently"""
    logger.error(f"API Error: {error_message}")
    
    response = {
        'success': False,
        'error': error_message
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def paginate_results(data, page=1, per_page=20):
    """Paginate results"""
    try:
        page = max(1, page)
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_data = data[start:end]
        
        return {
            'results': paginated_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(data),
                'pages': (len(data) + per_page - 1) // per_page,
                'has_next': end < len(data),
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        logger.error(f"Error paginating results: {e}")
        return {'results': data, 'pagination': {}}

def sanitize_input(text, max_length=1000):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove HTML tags and dangerous characters
    import re
    text = re.sub(r'<[^>]+>', '', str(text))
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()
