"""
Flask API Backend for ChicBot UI
Connects the web interface to the chatbot pipeline
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from chatbot_pipeline import ChatbotPipeline

app = Flask(__name__, static_folder='UI', static_url_path='')
CORS(app)

# Initialize chatbot pipeline
print("Initializing ChicBot...")
pipeline = ChatbotPipeline()
pipeline.load_models()
print("ChicBot ready!")


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('UI', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from UI
    
    Expected JSON:
    {
        "message": "user message text"
    }
    
    Returns:
    {
        "response": "bot response text",
        "products": [...],
        "metadata": {...}
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Process message through pipeline
        result = pipeline.process_message(user_message)
        
        # Handle out-of-context queries
        if result.get('status') == 'rejected':
            return jsonify({
                'response': result.get('message'),
                'products': [],
                'metadata': {
                    'detected_language': result.get('detected_language'),
                    'intent': result.get('intent'),
                    'status': 'rejected'
                }
            })
        
        # Return successful response
        return jsonify({
            'response': result.get('response', 'I found some products for you!'),
            'products': result.get('products', [])[:3],  # Limit to top 3 for UI
            'metadata': {
                'detected_language': result.get('detected_language'),
                'language_confidence': result.get('language_confidence'),
                'intent': result.get('intent'),
                'query_english': result.get('query_english'),
                'total_products': len(result.get('products', []))
            }
        })
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'details': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'ChicBot API is running'
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ChicBot Server Starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
