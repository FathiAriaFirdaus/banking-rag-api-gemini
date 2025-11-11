from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.loader_splitter import DocumentLoaderSplitter, MarkdownLoaderSplitter
from modules.vector_database import VectorDatabase
from modules.gemini_multi_query import GeminiMultiQuery
from config import DOCUMENT_PATH
import os
import tempfile
from functools import wraps


app = Flask(__name__)
CORS(app)

# Initialize Componenst
loader = MarkdownLoaderSplitter()
vector_db = VectorDatabase()
gemini_mq = GeminiMultiQuery()

def setup_system():
    """Setup the RAG System"""
    try:
        # Setup vector database
        vector_db.initialize_db()

        # Load documents if database empty
        if vector_db.get_document_count() == 0:
            print("Loading markdown documents")
            chunks = loader.load_and_split(DOCUMENT_PATH)
            vector_db.add_documents(chunks)

        # Setup Gemimi
        gemini_mq.setup()

        print('System Ready')
        return True
    
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        return False
    

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        correct_api_key = os.getenv('APP_API_KEY')

        if not api_key or api_key != correct_api_key:
            return jsonify({
                "success": False,
                "error": "unauthorized - ivalid API key"
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function
    

@app.route('/api/documents', methods=['GET', 'POST', 'DELETE'])
@require_api_key
def configure_documents():
    if request.method == 'DELETE':
        ids = vector_db.get_all_ids()
        vector_db.delete_documents(ids=ids)
        return jsonify({
            "response_message": "all document deleted",
            "documents_count": vector_db.get_document_count()
            }), 204
    
    elif request.method == 'GET':
        documents = vector_db.get_all_documents()
        return jsonify({
            "response_message": "showing available document",
            "documents_count": vector_db.get_document_count(),
            "documents": documents
            })
    
    elif request.method == 'POST':
        # Handle markdown file upload
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not file.filename.endswith('.md'):
            return jsonify({
                "success": False,
                "error": "Only markdown file are allowed"
            }), 400
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name

            # Load and process markdown file
            chunks = loader.load_and_split(temp_path)

            # Clear existing documents
            existing_ids = vector_db.get_all_ids()
            if existing_ids:
                vector_db.delete_documents(existing_ids)

            # Add new documents to vector database
            vector_db.add_documents(chunks)

            # Clear temporarily path
            os.unlink(temp_path)

            return jsonify({
                "success": True,
                "response_message": "Markdown document uploaded and processed successfully",
                "documents_count": vector_db.get_document_count(),
                "chunks_created": len(chunks),
                "filename": file.filename
            })
        
        except Exception as e:
            # Clean up temprarily files if exist
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)

            return jsonify({
                "success": False,
                "error": f"Error processing file: {str(e)}"
            }), 500

@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat():
    """Chat Endpoint"""
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Need message'}), 400
    
    question = data['message']
    answer = gemini_mq.chat(question)

    return jsonify({
        'success': True,
        'response_message': answer,
        'request_message': question
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health Check"""
    return jsonify({
        'status': 'healthy',
        'documents': vector_db.get_document_count()
    })

@app.route('/')
def home():
    return jsonify({
        "response_message": "Gemini Multi-Query RAG API",
        "available_endpoints":  {
            "chat": "POST /api/chat",
            "health": "GET /api/health",
            "documents": "GET/POST/DELETE /api/documents"
        }
    })


# EXCEPTION ROUTE FOR HANDLING UNAVAILABLE ROUTES
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "error": "endpoint not found",
        "response_message": "the requested URL was not found on the server",
        "available_endpoints":  {
            "chat": "POST /api/chat",
            "health": "GET /api/health",
            "documents": "GET/POST/DELETE /api/documents"
        }
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "method not allowed",
        "response_message": "the method is not allowed for the requested URL"
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": "internal server error",
        "response_message": "something went wrong on the server side"
    }), 500

@app.route('/<path:invalid_path>')
def invalid_route(invalid_path):
    return jsonify({
        "success": False,
        "error": "invalid endpoint",
        "response_message": f"The endpoint '/{invalid_path}' does not exist",
        "available_endpoints": {
            "chat": "POST /api/chat",
            "health": "GET /api/health",
            "documents": "GET/POST/DELETE /api/documents"
        }
    }), 404


if __name__ == "__main__":
    if setup_system():
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Cannot Start Server")
