"""
Ollama client - handles communication with local LLM
"""
import ollama
from typing import Dict, List, Optional
from utils.logger import setup_logger
from config import config

logger = setup_logger('ollama_client')

class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, model: str = None):
        self.model = model or config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        logger.info(f"Ollama client initialized with model: {self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Send chat messages to LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            system_prompt: Optional system prompt to prepend
            
        Returns:
            LLM response text
        """
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    *messages
                ]
            
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': temperature or self.temperature
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        system: Optional[str] = None
    ) -> str:
        """
        Generate text from a single prompt
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            system: System prompt
            
        Returns:
            Generated text
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                system=system,
                options={
                    'temperature': temperature or self.temperature
                }
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

if __name__ == "__main__":
    # Test Ollama client
    print("\n" + "="*60)
    print("Testing Ollama Client")
    print("="*60 + "\n")
    
    client = OllamaClient()
    
    # Check availability
    if not client.is_available():
        print("❌ Ollama is not running!")
        print("Start Ollama and try again.")
        exit(1)
    
    print("✓ Ollama is running\n")
    
    # Test generation
    print("Testing text generation...")
    response = client.generate("Say 'Hello, I am your AI file finder assistant!' in a friendly way.")
    print(f"Response: {response}\n")
    
    # Test chat
    print("Testing chat...")
    messages = [
        {'role': 'user', 'content': 'What is your purpose?'}
    ]
    response = client.chat(
        messages,
        system_prompt="You are an AI assistant that helps users find files on their computer."
    )
    print(f"Response: {response}\n")
    
    print("✓ Ollama client working!")