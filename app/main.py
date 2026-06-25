import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import secrets
import bleach
from datetime import datetime
import traceback

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)

# Security configurations
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    logger.error("SECRET_KEY not found in environment variables!")
    # Generate a temporary key for development
    app.secret_key = secrets.token_urlsafe(32)
    logger.warning(f"Generated temporary SECRET_KEY: {app.secret_key}")
    logger.warning("Please set SECRET_KEY in your .env file for production use!")

# Validate secret key length
if len(app.secret_key) < 32:
    logger.warning("SECRET_KEY is less than 32 characters. Please use a stronger key!")

app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# Enable CORS with restrictions
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATELIMIT_DEFAULT', '100/day')],
    enabled=os.getenv('RATELIMIT_ENABLED', 'False').lower() == 'true'
)

def validate_api_keys():
    """Validate API keys"""
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return False
    if not openai_key.startswith('sk-'):
        logger.error("OPENAI_API_KEY doesn't start with 'sk-'")
        return False
    if len(openai_key) < 20:
        logger.error("OPENAI_API_KEY is too short")
        return False
    logger.info("OpenAI API key validation passed")
    return True

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Return empty favicon to avoid 404 errors"""
    return '', 204

@app.route('/api/models', methods=['GET'])
def get_models_status():
    """Get status of all configured models"""
    try:
        from app.model_manager import model_manager
        results = model_manager.test_models()
        return jsonify({
            'status': 'success',
            'models': results,
            'available_count': sum(1 for v in results.values() if v),
            'total_count': len(results),
            'strategy': os.getenv('MODEL_FALLBACK_STRATEGY', 'sequential')
        })
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10/hour")
def generate_article():
    """Generate article based on provided topic"""
    try:
        logger.info("=" * 50)
        logger.info("Received article generation request")
        
        # Get and validate input
        data = request.get_json()
        if not data or 'topic' not in data:
            logger.error("Missing topic parameter")
            return jsonify({
                'error': 'Missing topic parameter',
                'status': 'error'
            }), 400
        
        # Sanitize input
        topic = bleach.clean(data['topic'].strip())
        logger.info(f"Processing topic: {topic}")
        
        if len(topic) < 3:
            logger.error("Topic too short")
            return jsonify({
                'error': 'Topic must be at least 3 characters long',
                'status': 'error'
            }), 400
        
        if len(topic) > 100:
            logger.error("Topic too long")
            return jsonify({
                'error': 'Topic must be less than 100 characters',
                'status': 'error'
            }), 400
        
        # Validate API keys
        if not validate_api_keys():
            logger.error("API key validation failed")
            return jsonify({
                'error': 'OpenAI API key is not properly configured. Please check your .env file.',
                'status': 'error'
            }), 500
        
        # Generate article using CrewAI with multi-model support
        logger.info(f"Starting article generation for topic: {topic}")
        
        try:
            from app.crew import ArticleCrew
            logger.info("Successfully imported ArticleCrew")
            
            crew = ArticleCrew()
            logger.info("Created ArticleCrew instance")
            
            result = crew.generate_article(topic)
            logger.info("Article generation completed successfully")
            
            # Convert result to string if it's not already
            result_str = str(result) if result else "No content generated"
            
            # Sanitize output
            sanitized_result = bleach.clean(
                result_str,
                tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'br', 'a', 'div', 'span', 'blockquote', 'code', 'pre'],
                strip=True
            )
            
            response_data = {
                'status': 'success',
                'topic': topic,
                'article': sanitized_result,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info("Returning successful response")
            return jsonify(response_data)
            
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f'Application configuration error: {str(e)}',
                'status': 'error'
            }), 500
        except Exception as e:
            logger.error(f"CrewAI error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f'AI processing error: {str(e)}',
                'status': 'error'
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_article: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'An unexpected error occurred while generating the article',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from app.model_manager import model_manager
        model_status = model_manager.test_models()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'api_key_valid': validate_api_keys(),
            'python_version': sys.version,
            'secret_key_valid': len(app.secret_key) >= 32,
            'models': {
                'primary': os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo'),
                'fallbacks': [os.getenv(f'OPENAI_MODEL_FALLBACK_{i}') for i in range(1, 4) if os.getenv(f'OPENAI_MODEL_FALLBACK_{i}')],
                'available': {k: v for k, v in model_status.items() if v},
                'unavailable': {k: v for k, v in model_status.items() if not v}
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Flask application...")
    logger.info("=" * 60)
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check SECRET_KEY
    if app.secret_key:
        logger.info(f"SECRET_KEY length: {len(app.secret_key)} characters")
        if len(app.secret_key) >= 32:
            logger.info("✓ SECRET_KEY is properly configured")
        else:
            logger.warning("⚠️ SECRET_KEY is less than 32 characters")
    else:
        logger.error("❌ SECRET_KEY is not configured!")
    
    if not validate_api_keys():
        logger.warning("WARNING: Running without proper API keys - some features may not work")
    
    # Test model availability
    try:
        from app.model_manager import model_manager
        logger.info("Testing model availability...")
        model_status = model_manager.test_models()
        available = [m for m, v in model_status.items() if v]
        if available:
            logger.info(f"✓ Available models: {available}")
        else:
            logger.warning("⚠️ No models are available! Please check your API key and model names.")
    except Exception as e:
        logger.error(f"Error testing models: {str(e)}")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    logger.info(f"Running on port {port} with debug={debug}")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)