"""
Text Generation Model using PyTorch
Uses GPT-2 or similar models for text generation
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class TextGenerator:
    def __init__(self):
        """Initialize the text generation model"""
        print("Initializing Text Generator...")
        
        # Option 1: GPT-2 (recommended for balance of speed and quality)
        model_name = "gpt2"
        
        # Option 2: DistilGPT-2 (faster, slightly lower quality)
        # model_name = "distilgpt2"
        
        # Option 3: GPT-2 Medium (better quality, slower)
        # model_name = "gpt2-medium"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            self.model.eval()
            print(f"Generator loaded on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def apply_tone(self, prompt, tone):
        """Add tone instructions to the prompt"""
        tone_prefixes = {
            'formal': "Write in a formal, professional manner: ",
            'casual': "Write in a casual, conversational style: ",
            'creative': "Write creatively and imaginatively: ",
            'technical': "Write in a technical, precise manner: "
        }
        
        prefix = tone_prefixes.get(tone, "")
        return prefix + prompt
    
    def generate(self, prompt, tone='formal', max_length=500, temperature=0.7):
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt for generation
            tone: Style of writing (formal, casual, creative, technical)
            max_length: Maximum number of words to generate
            temperature: Controls randomness (0.1-1.0)
        
        Returns:
            Dictionary with generated text and statistics
        """
        try:
            # Apply tone to prompt
            full_prompt = self.apply_tone(prompt, tone)
            
            # Tokenize input
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Calculate max tokens (roughly 1.3 tokens per word)
            max_tokens = int(max_length * 1.3)
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs['input_ids'],
                    max_length=max_tokens,
                    min_length=50,
                    temperature=temperature,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3,  # Avoid repetition
                )
            
            # Decode generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the generated text
            if generated_text.startswith(full_prompt):
                generated_text = generated_text[len(full_prompt):].strip()
            
            # Clean up the text
            generated_text = self.clean_generated_text(generated_text)
            
            # Count words and tokens
            word_count = len(generated_text.split())
            tokens_used = outputs.shape[1]
            
            result = {
                "generatedText": generated_text,
                "wordCount": word_count,
                "tokensUsed": tokens_used
            }
            
            print(f"Generated {word_count} words ({tokens_used} tokens)")
            return result
            
        except Exception as e:
            print(f"Error during generation: {e}")
            return {
                "generatedText": "Error generating text. Please try with a different prompt.",
                "wordCount": 0,
                "tokensUsed": 0,
                "error": str(e)
            }
    
    def clean_generated_text(self, text):
        """Clean up generated text"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Ensure text ends with proper punctuation
        if text and text[-1] not in '.!?':
            # Find the last sentence-ending punctuation
            last_punct = max(
                text.rfind('.'),
                text.rfind('!'),
                text.rfind('?')
            )
            if last_punct > 0:
                text = text[:last_punct + 1]
        
        return text.strip()


# For testing locally
if __name__ == "__main__":
    generator = TextGenerator()
    
    # Test with sample prompts
    prompts = [
        ("Write about artificial intelligence", "formal"),
        ("Tell me a story about a robot", "creative"),
        ("Explain how neural networks work", "technical")
    ]
    
    for prompt, tone in prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print(f"Tone: {tone}")
        print(f"{'='*60}")
        
        result = generator.generate(prompt, tone=tone, max_length=200, temperature=0.7)
        print(f"\nGenerated ({result['wordCount']} words):")
        print(result['generatedText'])