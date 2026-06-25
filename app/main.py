import os
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import secrets
import bleach
from datetime import datetime
import json

from app.crew import ArticleCrew

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)

# Security configurations
app.secret_key = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

# Enable CORS with restrictions
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATELIMIT_DEFAULT', '100/day')],
    enabled=os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
)

# Validate API keys on startup
def validate_api_keys():
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or not openai_key.startswith('sk-'):
        logger.error("Invalid or missing OpenAI API key")
        return False
    return True

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10/hour")
def generate_article():
    """Generate article based on provided topic"""
    try:
        # Get and validate input
        data = request.get_json()
        if not data or 'topic' not in data:
            return jsonify({
                'error': 'Missing topic parameter',
                'status': 'error'
            }), 400
        
        # Sanitize input
        topic = bleach.clean(data['topic'].strip())
        if len(topic) < 3:
            return jsonify({
                'error': 'Topic must be at least 3 characters long',
                'status': 'error'
            }), 400
        
        if len(topic) > 100:
            return jsonify({
                'error': 'Topic must be less than 100 characters',
                'status': 'error'
            }), 400
        
        # Validate API keys
        if not validate_api_keys():
            return jsonify({
                'error': 'API configuration error',
                'status': 'error'
            }), 500
        
        # Generate article using CrewAI
        logger.info(f"Generating article for topic: {topic}")
        crew = ArticleCrew()
        result = crew.generate_article(topic)
        
        # Sanitize output
        sanitized_result = bleach.clean(result, tags=['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'strong', 'em'])
        
        return jsonify({
            'status': 'success',
            'topic': topic,
            'article': sanitized_result,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating article: {str(e)}")
        return jsonify({
            'error': 'An error occurred while generating the article',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if not validate_api_keys():
        logger.warning("Running without proper API keys - some features may not work")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)