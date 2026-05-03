"""
Intent detector - understands what the user wants to do
"""
import json
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

from llm.ollama_client import OllamaClient
from utils.logger import setup_logger

logger = setup_logger('intent_detector')

class Intent(Enum):
    """User intent types"""
    SEARCH = "search"              # Find files
    OPEN = "open"                  # Open a file
    SHOW_IN_FOLDER = "show"        # Show file in folder
    MOVE = "move"                  # Move file
    COPY_PATH = "copy_path"        # Copy file path
    RENAME = "rename"              # Rename file
    DELETE = "delete"              # Delete file
    INFO = "info"                  # Get file information
    LIST = "list"                  # List files
    HELP = "help"                  # Get help
    UNCLEAR = "unclear"            # Unclear intent

@dataclass
class UserIntent:
    """Parsed user intent"""
    intent: Intent
    query: str                          # Search query or file reference
    action_target: Optional[str] = None  # Target for actions (e.g., destination folder)
    file_type: Optional[str] = None     # Filter by file type
    time_filter: Optional[str] = None   # Time-based filter
    confidence: float = 1.0             # Confidence in intent detection
    clarification_needed: bool = False  # Whether to ask for clarification
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'intent': self.intent.value,
            'query': self.query,
            'action_target': self.action_target,
            'file_type': self.file_type,
            'time_filter': self.time_filter,
            'confidence': self.confidence,
            'clarification_needed': self.clarification_needed
        }

class IntentDetector:
    """Detects user intent from natural language"""
    
    def __init__(self):
        self.llm = OllamaClient()
        logger.info("Intent detector initialized")
    
    def detect_intent(self, user_message: str) -> UserIntent:
        """
        Detect user intent from message
        
        Args:
            user_message: User's input message
            
        Returns:
            UserIntent object
        """
        logger.info(f"Detecting intent for: '{user_message}'")
        
        # Build prompt for LLM
        system_prompt = self._get_intent_system_prompt()
        
        prompt = f"""Analyze this user message and extract the intent:

User message: "{user_message}"

Return a JSON object with:
- intent: one of [search, open, show, move, copy_path, rename, delete, info, list, help, unclear]
- query: the search query or file reference (extract the key terms)
- action_target: if moving/copying, where to (e.g., "Desktop", "Documents")
- file_type: if user mentions file type (e.g., ".pdf", ".xlsx")
- time_filter: if user mentions time (e.g., "last week", "yesterday", "this month")
- confidence: 0.0 to 1.0
- clarification_needed: true if you need more info

Examples:

User: "find my budget spreadsheet from last month"
Response: {{"intent": "search", "query": "budget spreadsheet", "file_type": ".xlsx", "time_filter": "last month", "confidence": 0.9, "clarification_needed": false}}

User: "open the python file about data processing"
Response: {{"intent": "open", "query": "python file data processing", "file_type": ".py", "confidence": 0.85, "clarification_needed": false}}

User: "move my reports to desktop"
Response: {{"intent": "move", "query": "reports", "action_target": "Desktop", "confidence": 0.8, "clarification_needed": false}}

Now analyze the user's message and respond with ONLY the JSON object, no other text."""

        try:
            # Get LLM response
            response = self.llm.generate(prompt, system=system_prompt, temperature=0.3)
            
            # Parse JSON response
            intent_data = self._parse_llm_response(response)
            
            # Convert to UserIntent object
            user_intent = self._create_user_intent(intent_data)
            
            logger.info(f"Detected intent: {user_intent.intent.value} (confidence: {user_intent.confidence})")
            
            return user_intent
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            # Return default search intent
            return UserIntent(
                intent=Intent.SEARCH,
                query=user_message,
                confidence=0.5
            )
    
    def _get_intent_system_prompt(self) -> str:
        """Get system prompt for intent detection"""
        return """You are an intent detection system for a file finder application.
Your job is to understand what the user wants to do with their files.

Be precise and extract key information:
- What action they want (search, open, move, etc.)
- What file they're looking for (extract meaningful terms)
- Any filters (file type, date)
- Any action targets (where to move, what to rename to)

Always respond with valid JSON only, no additional text."""
    
    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM JSON response"""
        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.debug(f"Response was: {response}")
            # Return default
            return {
                'intent': 'unclear',
                'query': '',
                'confidence': 0.0,
                'clarification_needed': True
            }
    
    def _create_user_intent(self, intent_data: dict) -> UserIntent:
        """Create UserIntent object from parsed data"""
        # Map intent string to enum
        intent_str = intent_data.get('intent', 'search').lower()
        try:
            intent = Intent(intent_str)
        except ValueError:
            logger.warning(f"Unknown intent: {intent_str}, defaulting to SEARCH")
            intent = Intent.SEARCH
        
        return UserIntent(
            intent=intent,
            query=intent_data.get('query', ''),
            action_target=intent_data.get('action_target'),
            file_type=intent_data.get('file_type'),
            time_filter=intent_data.get('time_filter'),
            confidence=float(intent_data.get('confidence', 0.8)),
            clarification_needed=bool(intent_data.get('clarification_needed', False))
        )
    
    def needs_clarification(self, user_intent: UserIntent) -> bool:
        """Check if clarification is needed"""
        return (
            user_intent.clarification_needed or
            user_intent.confidence < 0.6 or
            user_intent.intent == Intent.UNCLEAR
        )
    
    def generate_clarification(self, user_intent: UserIntent) -> str:
        """Generate a clarification question"""
        if user_intent.intent == Intent.UNCLEAR:
            return "I'm not sure what you'd like me to do. Could you rephrase that? You can ask me to search for files, open them, move them, and more."
        
        if not user_intent.query:
            return "What file are you looking for? Could you provide more details?"
        
        if user_intent.confidence < 0.6:
            return f"Just to confirm, you want me to {user_intent.intent.value} files related to '{user_intent.query}'?"
        
        return "Could you provide more details about what you're looking for?"

if __name__ == "__main__":
    # Test intent detection
    print("\n" + "="*70)
    print("Testing Intent Detector")
    print("="*70 + "\n")
    
    detector = IntentDetector()
    
    # Test cases
    test_messages = [
        "find my budget spreadsheet from last month",
        "open that python file about data processing",
        "show me the report.pdf in folder",
        "move all my invoices to Desktop",
        "what's in my documents folder?",
        "help me find files",
        "the thing from yesterday"
    ]
    
    for message in test_messages:
        print(f"Message: '{message}'")
        print("-" * 70)
        
        intent = detector.detect_intent(message)
        
        print(f"Intent: {intent.intent.value}")
        print(f"Query: {intent.query}")
        if intent.file_type:
            print(f"File type: {intent.file_type}")
        if intent.time_filter:
            print(f"Time filter: {intent.time_filter}")
        if intent.action_target:
            print(f"Action target: {intent.action_target}")
        print(f"Confidence: {intent.confidence:.2f}")
        
        if detector.needs_clarification(intent):
            clarification = detector.generate_clarification(intent)
            print(f"⚠️  Clarification needed: {clarification}")
        
        print("\n")