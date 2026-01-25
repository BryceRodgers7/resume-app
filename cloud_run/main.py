"""
GPT Model API Backend for Google Cloud Run
Provides text generation endpoint for the frontend application
"""

import os
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global model variable
model = None
device = None

def load_model():
    """
    Load the GPT model. Replace this with your actual model loading logic.
    
    This is a placeholder that you should customize based on:
    - Your model architecture
    - Where your model weights are stored (local file, GCS bucket, etc.)
    - Any tokenizer or vocabulary files needed
    """
    global model, device
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # TODO: Replace with your actual model loading
    # Example:
    # from your_model_module import GPTModel
    # model = GPTModel.load_from_checkpoint('path/to/checkpoint.pt')
    # model.to(device)
    # model.eval()
    
    print(f"Model loaded on device: {device}")
    return model


def generate_text(seed, temperature, num_chars):
    """
    Generate text using the GPT model.
    
    Args:
        seed: Random seed for reproducibility
        temperature: Sampling temperature (higher = more random)
        num_chars: Number of characters to generate
    
    Returns:
        Generated text string
    """
    # Set random seed for reproducibility
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    
    # TODO: Replace with your actual generation logic
    # Example:
    # with torch.no_grad():
    #     generated = model.generate(
    #         max_length=num_chars,
    #         temperature=temperature,
    #         device=device
    #     )
    #     return generated
    
    # Placeholder response
    return f"Generated {num_chars} characters with seed={seed}, temperature={temperature}"


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Cloud Run"""
    return jsonify({"status": "healthy", "model_loaded": model is not None})


@app.route('/generate', methods=['POST'])
def generate():
    """
    Main generation endpoint.
    
    Expected JSON payload:
    {
        "seed": int (optional, default: 42),
        "temperature": float (optional, default: 1.0),
        "num_chars": int (required)
    }
    """
    try:
        data = request.get_json()
        
        # Validate and extract parameters
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        num_chars = data.get('num_chars')
        if num_chars is None:
            return jsonify({"error": "num_chars is required"}), 400
        
        if not isinstance(num_chars, int) or num_chars <= 0:
            return jsonify({"error": "num_chars must be a positive integer"}), 400
        
        if num_chars > 5000:  # Set a reasonable limit
            return jsonify({"error": "num_chars must be <= 5000"}), 400
        
        seed = data.get('seed', 42)
        temperature = data.get('temperature', 1.0)
        
        # Validate temperature
        if not isinstance(temperature, (int, float)) or temperature <= 0:
            return jsonify({"error": "temperature must be a positive number"}), 400
        
        # Generate text
        generated_text = generate_text(seed, temperature, num_chars)
        
        return jsonify({
            "success": True,
            "generated_text": generated_text,
            "parameters": {
                "seed": seed,
                "temperature": temperature,
                "num_chars": num_chars
            }
        })
    
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500


@app.before_request
def initialize_model():
    """Initialize model on first request"""
    global model
    if model is None:
        load_model()


if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

