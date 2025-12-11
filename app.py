"""
Flask API Backend for ChicBot UI
Connects the web interface to the chatbot pipeline
"""
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import sys
import uuid
from pathlib import Path
from datetime import timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from chatbot_pipeline import ChatbotPipeline

app = Flask(__name__, static_folder='UI', static_url_path='')
app.config['SECRET_KEY'] = 'chicbot-secret-key-' + str(uuid.uuid4())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
CORS(app, supports_credentials=True)

# Store pipelines per session (in-memory for simplicity)
# In production, use Redis or database
session_pipelines = {}

def get_or_create_pipeline(session_id):
    """Get existing pipeline for session or create new one"""
    if session_id not in session_pipelines:
        print(f"Creating new pipeline for session {session_id[:8]}...")
        pipeline = ChatbotPipeline()
        pipeline.load_models()
        session_pipelines[session_id] = pipeline
    return session_pipelines[session_id]


@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('UI', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from UI with session-based conversation history
    
    Expected JSON:
    {
        "message": "user message text",
        "session_id": "optional-session-id"
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
        
        # Get or create session ID
        session_id = data.get('session_id') or session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            session.permanent = True
        
        # Get pipeline for this session (maintains conversation history)
        pipeline = get_or_create_pipeline(session_id)
        
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
        
        # Return successful response with session info
        return jsonify({
            'response': result.get('response', 'I found some products for you!'),
            'products': result.get('products', [])[:3],  # Limit to top 3 for UI
            'session_id': session_id,
            'metadata': {
                'detected_language': result.get('detected_language'),
                'language_confidence': result.get('language_confidence'),
                'intent': result.get('intent'),
                'query_english': result.get('query_english'),
                'total_products': len(result.get('products', [])),
                'conversation_turns': len(pipeline.conversation_history)
            }
        })
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'details': str(e)
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history for current session"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id') or session.get('session_id')
        
        if session_id and session_id in session_pipelines:
            session_pipelines[session_id].conversation_history = []
            return jsonify({
                'status': 'success',
                'message': 'Conversation history reset'
            })
        
        return jsonify({
            'status': 'success',
            'message': 'No active conversation to reset'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'ChicBot API is running',
        'active_sessions': len(session_pipelines)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ChicBot Server Starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
