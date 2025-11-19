"""
Firebase Cloud Functions for AI Text Analysis
Deploy with: firebase deploy --only functions
"""

from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore
import json
from models.detector import AIDetector
from models.summarizer import TextSummarizer
from models.generator import TextGenerator

# Initialize Firebase Admin SDK
initialize_app()
db = firestore.client()

# Initialize AI models (loaded once per cold start)
print("Loading AI models...")
detector = AIDetector()
summarizer = TextSummarizer()
generator = TextGenerator()
print("Models loaded successfully!")


@https_fn.on_request(cors=https_fn.CorsOptions(
    cors_origins=["*"],
    cors_methods=["POST", "OPTIONS"]
))
def detectAIText(req: https_fn.Request) -> https_fn.Response:
    """
    Detect if text is AI-generated
    
    Request body:
    {
        "text": "string (minimum 50 characters)"
    }
    
    Response:
    {
        "isAI": boolean,
        "confidence": float (0-100),
        "perplexity": float,
        "burstiness": float
    }
    """
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=204)
    
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            mimetype='application/json'
        )
    
    try:
        # Parse request
        data = req.get_json()
        text = data.get('text', '').strip()
        
        # Validation
        if not text:
            return https_fn.Response(
                json.dumps({"error": "No text provided"}),
                status=400,
                mimetype='application/json'
            )
        
        if len(text) < 50:
            return https_fn.Response(
                json.dumps({"error": "Text must be at least 50 characters"}),
                status=400,
                mimetype='application/json'
            )
        
        # Run AI detection
        print(f"Processing detection for {len(text)} characters")
        result = detector.predict(text)
        
        # Save to Firestore
        try:
            db.collection('results').add({
                'type': 'detection',
                'input': text[:500],
                'output': result,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception as db_error:
            print(f"Firestore error: {db_error}")
        
        # Return result
        return https_fn.Response(
            json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"Error in detectAIText: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )


@https_fn.on_request(cors=https_fn.CorsOptions(
    cors_origins=["*"],
    cors_methods=["POST", "OPTIONS"]
))
def summarizeText(req: https_fn.Request) -> https_fn.Response:
    """
    Summarize text
    
    Request body:
    {
        "text": "string",
        "ratio": float (0.25, 0.5, 0.75),
        "format": "paragraph" | "bullets"
    }
    
    Response:
    {
        "summary": "string",
        "originalWords": int,
        "summaryWords": int,
        "compressionRatio": float
    }
    """
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=204)
    
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            mimetype='application/json'
        )
    
    try:
        data = req.get_json()
        text = data.get('text', '').strip()
        ratio = float(data.get('ratio', 0.5))
        format_type = data.get('format', 'paragraph')
        
        if not text:
            return https_fn.Response(
                json.dumps({"error": "No text provided"}),
                status=400,
                mimetype='application/json'
            )
        
        # Run summarization
        print(f"Processing summarization with ratio {ratio}")
        result = summarizer.summarize(text, ratio, format_type)
        
        # Save to Firestore
        try:
            db.collection('results').add({
                'type': 'summary',
                'input': text[:500],
                'output': result,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception as db_error:
            print(f"Firestore error: {db_error}")
        
        return https_fn.Response(
            json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"Error in summarizeText: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )


@https_fn.on_request(cors=https_fn.CorsOptions(
    cors_origins=["*"],
    cors_methods=["POST", "OPTIONS"]
))
def generateText(req: https_fn.Request) -> https_fn.Response:
    """
    Generate text from prompt
    
    Request body:
    {
        "prompt": "string",
        "tone": "formal" | "casual" | "creative" | "technical",
        "maxLength": int (100-1000),
        "temperature": float (0.1-1.0)
    }
    
    Response:
    {
        "generatedText": "string",
        "wordCount": int,
        "tokensUsed": int
    }
    """
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=204)
    
    if req.method != 'POST':
        return https_fn.Response(
            json.dumps({"error": "Method not allowed"}),
            status=405,
            mimetype='application/json'
        )
    
    try:
        data = req.get_json()
        prompt = data.get('prompt', '').strip()
        tone = data.get('tone', 'formal')
        max_length = int(data.get('maxLength', 500))
        temperature = float(data.get('temperature', 0.7))
        
        if not prompt:
            return https_fn.Response(
                json.dumps({"error": "No prompt provided"}),
                status=400,
                mimetype='application/json'
            )
        
        # Run text generation
        print(f"Generating text with prompt: {prompt[:50]}...")
        result = generator.generate(prompt, tone, max_length, temperature)
        
        # Save to Firestore
        try:
            db.collection('results').add({
                'type': 'generation',
                'input': prompt,
                'output': result,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception as db_error:
            print(f"Firestore error: {db_error}")
        
        return https_fn.Response(
            json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"Error in generateText: {str(e)}")
        return https_fn.Response(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status=500,
            mimetype='application/json'
        )