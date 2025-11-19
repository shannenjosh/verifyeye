"""
AI Text Detection Model using PyTorch
Uses a pre-trained transformer model to detect AI-generated text
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np


class AIDetector:
    def __init__(self):
        """Initialize the AI detection model"""
        print("Initializing AI Detector...")
        
        # Option 1: Use RoBERTa-based detector (recommended)
        model_name = "roberta-base"  # You can fine-tune this on AI detection dataset
        
        # Option 2: Use a pre-trained AI detector (if available)
        # model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=2  # Binary classification: Human vs AI
            )
            self.model.eval()
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            print(f"Model loaded on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def calculate_perplexity(self, text):
        """
        Calculate perplexity score
        Lower perplexity = more predictable = likely AI
        """
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                loss = torch.nn.functional.cross_entropy(
                    outputs.logits,
                    torch.zeros(outputs.logits.size(0), dtype=torch.long).to(self.device)
                )
                perplexity = torch.exp(loss).item()
            
            return min(perplexity, 100.0)  # Cap at 100 for display
        except:
            return 0.0
    
    def calculate_burstiness(self, text):
        """
        Calculate burstiness (variation in sentence length)
        Lower burstiness = more uniform = likely AI
        """
        try:
            sentences = text.split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return 0.0
            
            lengths = [len(s.split()) for s in sentences]
            mean_length = np.mean(lengths)
            std_length = np.std(lengths)
            
            if mean_length == 0:
                return 0.0
            
            # Coefficient of variation
            burstiness = std_length / mean_length
            return min(burstiness, 1.0)  # Normalize to 0-1
        except:
            return 0.0
    
    def predict(self, text):
        """
        Main prediction function
        Returns detection result with confidence score
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                
                # Get AI probability (assuming label 1 = AI)
                ai_probability = probabilities[0][1].item()
                confidence = ai_probability * 100
            
            # Calculate additional metrics
            perplexity = self.calculate_perplexity(text)
            burstiness = self.calculate_burstiness(text)
            
            # Determine if AI-generated (threshold: 50%)
            is_ai = confidence > 50
            
            result = {
                "isAI": bool(is_ai),
                "confidence": round(confidence, 2),
                "perplexity": round(perplexity, 2),
                "burstiness": round(burstiness, 2)
            }
            
            print(f"Detection result: {result}")
            return result
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            # Return a default result in case of error
            return {
                "isAI": False,
                "confidence": 50.0,
                "perplexity": 0.0,
                "burstiness": 0.0,
                "error": str(e)
            }


# For testing locally
if __name__ == "__main__":
    detector = AIDetector()
    
    # Test with sample text
    sample_text = """
    Artificial intelligence has revolutionized the way we interact with technology.
    Machine learning algorithms can now process vast amounts of data with unprecedented accuracy.
    These systems continue to evolve and improve over time.
    """
    
    result = detector.predict(sample_text)
    print(f"\nTest Result: {result}")