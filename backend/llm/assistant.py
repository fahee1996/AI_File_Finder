"""
AI Assistant - conversational interface for file finding
"""
from typing import List, Dict, Optional
from dataclasses import dataclass

from operations.file_operations import FileOperations

from llm.ollama_client import OllamaClient
from llm.intent_detector import IntentDetector, UserIntent, Intent
from llm.query_enhancer import QueryEnhancer
from search.search_engine import SearchEngine, SearchResult
from utils.logger import setup_logger

logger = setup_logger('assistant')

@dataclass
class ConversationContext:
    """Maintains conversation context"""
    last_query: str = ""
    last_results: List[SearchResult] = None
    last_intent: Optional[UserIntent] = None
    conversation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.last_results is None:
            self.last_results = []
        if self.conversation_history is None:
            self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        
        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

class FileFinderAssistant:
    """Main AI assistant for file finding"""
    
    def __init__(self):
        self.llm = OllamaClient()
        self.intent_detector = IntentDetector()
        self.query_enhancer = QueryEnhancer()
        self.search_engine = SearchEngine()
        self.file_ops = FileOperations()  # ADD THIS
        self.context = ConversationContext()
        
        logger.info("File finder assistant initialized")
    
    def execute_file_operation(
    self,
    operation: str,
    file_path: str,
    **kwargs
) -> tuple[bool, str]:
        """
        Execute a file operation
        
        Args:
            operation: Operation to perform (open, show, copy_path, move, etc.)
            file_path: Path to file
            **kwargs: Additional arguments for operation
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Executing operation '{operation}' on {file_path}")
        
        if operation == "open":
            return self.file_ops.open_file(file_path)
        
        elif operation == "show":
            return self.file_ops.show_in_folder(file_path)
        
        elif operation == "copy_path":
            return self.file_ops.copy_path_to_clipboard(file_path)
        
        elif operation == "move":
            destination = kwargs.get('destination')
            if not destination:
                return False, "Destination not specified"
            return self.file_ops.move_file(file_path, destination)
        
        elif operation == "copy":
            destination = kwargs.get('destination')
            if not destination:
                return False, "Destination not specified"
            return self.file_ops.copy_file(file_path, destination)
        
        elif operation == "rename":
            new_name = kwargs.get('new_name')
            if not new_name:
                return False, "New name not specified"
            return self.file_ops.rename_file(file_path, new_name)
        
        elif operation == "delete":
            permanent = kwargs.get('permanent', False)
            return self.file_ops.delete_file(file_path, permanent)
        
        else:
            return False, f"Unknown operation: {operation}"
    
    def get_file_for_action(self, file_reference: str) -> Optional[SearchResult]:
        """
        Find file based on user reference
        
        Args:
            file_reference: User's description of the file
            
        Returns:
            SearchResult or None
        """
        # Check if it's a direct reference to last results
        if file_reference.lower() in ['it', 'that', 'this', 'the file']:
            if self.context.last_results:
                return self.context.last_results[0]
            return None
        
        # Check if it's a number reference (e.g., "1", "first", "second")
        number_map = {
            '1': 0, 'first': 0, 'one': 0,
            '2': 1, 'second': 1, 'two': 1,
            '3': 2, 'third': 2, 'three': 2,
            '4': 3, 'fourth': 3, 'four': 3,
            '5': 4, 'fifth': 4, 'five': 4,
        }
        
        ref_lower = file_reference.lower().strip()
        if ref_lower in number_map:
            idx = number_map[ref_lower]
            if self.context.last_results and idx < len(self.context.last_results):
                return self.context.last_results[idx]
        
        # Otherwise search for the file
        results = self.search_engine.search(file_reference, max_results=1)
        if results:
            return results[0]
        
        return None

    def process_message(self, user_message: str) -> str:
        """
        Process user message and return response
        
        Args:
            user_message: User's input message
            
        Returns:
            Assistant's response
        """
        logger.info(f"Processing message: '{user_message}'")
        
        # Add to conversation history
        self.context.add_message('user', user_message)
        
        try:
            # Detect intent
            user_intent = self.intent_detector.detect_intent(user_message)
            self.context.last_intent = user_intent
            
            # Handle based on intent
            if user_intent.intent == Intent.SEARCH:
                response = self._handle_search(user_intent)
            
            elif user_intent.intent == Intent.OPEN:
                response = self._handle_open(user_intent)
            
            elif user_intent.intent == Intent.SHOW_IN_FOLDER:
                response = self._handle_show_in_folder(user_intent)
            
            elif user_intent.intent == Intent.INFO:
                response = self._handle_info(user_intent)
            
            elif user_intent.intent == Intent.HELP:
                response = self._handle_help()
            
            elif user_intent.intent == Intent.UNCLEAR:
                clarification = self.intent_detector.generate_clarification(user_intent)
                response = clarification
            
            else:
                response = f"I understand you want to {user_intent.intent.value}, but this feature is coming soon!"
            
            # Add response to history
            self.context.add_message('assistant', response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I encountered an error. Could you try rephrasing your request?"
    
    def _handle_search(self, user_intent: UserIntent) -> str:
        """Handle search intent"""
        query = user_intent.query
        
        if not query:
            return "What would you like to search for?"
        
        # Enhance query
        enhanced_query = self.query_enhancer.enhance_query(
            query,
            file_type=user_intent.file_type
        )
        
        # Search
        results = self.search_engine.search(
            enhanced_query,
            max_results=10,
            file_type=user_intent.file_type
        )
        
        # Store results
        self.context.last_query = query
        self.context.last_results = results
        
        # Generate response
        if not results:
            return self._generate_no_results_response(query)
        
        return self._generate_search_results_response(query, results)
    
    def _handle_open(self, user_intent: UserIntent) -> str:
        """Handle open file intent"""
        # Get the file
        file_result = self.get_file_for_action(user_intent.query)
        
        if not file_result:
            # Search for it
            results = self.search_engine.search(user_intent.query, max_results=5)
            
            if not results:
                return f"I couldn't find any files matching '{user_intent.query}'."
            
            self.context.last_results = results
            
            if len(results) == 1:
                file_result = results[0]
            else:
                # Multiple results
                response = f"I found {len(results)} files:\n\n"
                for i, result in enumerate(results[:5], 1):
                    response += f"{i}. {result.name}\n"
                response += "\nWhich one? (say 'open 1' or 'open the first')"
                return response
        
        # Open the file
        success, msg = self.execute_file_operation("open", file_result.path)
        
        if success:
            return f"✓ Opened '{file_result.name}'"
        else:
            return f"❌ {msg}"
    
    def _handle_show_in_folder(self, user_intent: UserIntent) -> str:
        """Handle show in folder intent"""
        file_result = self.get_file_for_action(user_intent.query)
        
        if not file_result:
            results = self.search_engine.search(user_intent.query, max_results=5)
            
            if not results:
                return f"I couldn't find any files matching '{user_intent.query}'."
            
            self.context.last_results = results
            
            if len(results) == 1:
                file_result = results[0]
            else:
                response = f"I found {len(results)} files. Which one?\n\n"
                for i, result in enumerate(results[:5], 1):
                    response += f"{i}. {result.name}\n"
                return response
        
        # Show in folder
        success, msg = self.execute_file_operation("show", file_result.path)
        
        if success:
            return f"✓ Showing '{file_result.name}' in folder"
        else:
            return f"❌ {msg}"
    
    def _handle_info(self, user_intent: UserIntent) -> str:
        """Handle file info request"""
        if not user_intent.query and self.context.last_results:
            # Info about last search results
            return self._generate_stats_response()
        
        results = self.search_engine.search(user_intent.query, max_results=1)
        
        if not results:
            return f"I couldn't find any files matching '{user_intent.query}'."
        
        file = results[0]
        return self._generate_file_info_response(file)
    
    def _handle_help(self) -> str:
        """Handle help request"""
        return """I'm your AI file finder assistant! Here's what I can do:

    

🔍 **Search for files:**
- "Find my budget spreadsheet"
- "Show me Python files from last week"
- "Where is that report about sales?"

📂 **Open files:**
- "Open the presentation about marketing"
- "Launch that Excel file"

📁 **Show in folder:**
- "Show me where report.pdf is located"
- "Find the folder with my invoices"

ℹ️  **Get information:**
- "Tell me about this file"
- "What files do I have?"

Just ask me naturally, and I'll help you find what you need!"""
    
    def _generate_search_results_response(
        self,
        query: str,
        results: List[SearchResult]
    ) -> str:
        """Generate natural language response for search results"""
        
        # Build context for LLM
        results_summary = []
        for i, result in enumerate(results[:5], 1):
            results_summary.append(
                f"{i}. {result.name} ({result.extension}, {result.size_mb:.2f} MB, "
                f"score: {result.relevance_score:.2f})"
            )
        
        results_text = "\n".join(results_summary)
        
        system_prompt = """You are a helpful file finder assistant.
The user searched for something and you found results.
Respond in a friendly, natural way. Be concise but helpful.
Mention the top results and their relevance.
Don't just list files - explain what you found."""

        prompt = f"""User searched for: "{query}"

Found {len(results)} results:
{results_text}

Respond to the user about what you found:"""

        try:
            response = self.llm.generate(prompt, system=system_prompt, temperature=0.7)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return f"I found {len(results)} files matching '{query}'. The top result is '{results[0].name}'."
    
    def _generate_no_results_response(self, query: str) -> str:
        """Generate response when no results found"""
        system_prompt = """You are a helpful file finder assistant.
The user searched for something but no results were found.
Respond sympathetically and suggest what they could try."""

        prompt = f"""User searched for: "{query}"

No results found.

Respond to the user:"""

        try:
            response = self.llm.generate(prompt, system=system_prompt, temperature=0.7)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I couldn't find any files matching '{query}'. Try using different keywords or check the file name."
    
    def _generate_file_info_response(self, file: SearchResult) -> str:
        """Generate detailed file information response"""
        return f"""**{file.name}**

📁 Path: {file.path}
📄 Type: {file.extension}
💾 Size: {file.size_mb:.2f} MB
🕐 Modified: {file.modified_time}
⭐ Relevance: {file.relevance_score:.2%}

{f"Preview: {file.preview[:150]}..." if file.preview else ""}"""
    
    def _generate_stats_response(self) -> str:
        """Generate statistics response"""
        stats = self.search_engine.get_statistics()
        
        total = stats.get('total_files_indexed', 0)
        size_gb = stats.get('total_size_gb', 0)
        
        top_types = stats.get('file_types', [])[:5]
        types_text = "\n".join([f"- {t['extension']}: {t['count']} files" for t in top_types])
        
        return f"""📊 **Your File Statistics:**

Total files indexed: **{total:,}**
Total size: **{size_gb:.2f} GB**

Top file types:
{types_text}"""
    
    def clear_context(self):
        """Clear conversation context"""
        self.context = ConversationContext()
        logger.info("Context cleared")

if __name__ == "__main__":
    # Test assistant
    print("\n" + "="*70)
    print("AI File Finder Assistant - Interactive Test")
    print("="*70 + "\n")
    
    assistant = FileFinderAssistant()
    
    print("Assistant ready! Type 'quit' to exit, 'clear' to reset conversation.\n")
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if user_input.lower() == 'clear':
            assistant.clear_context()
            print("\n[Context cleared]\n")
            continue
        
        # Process message
        print("\nAssistant: ", end="")
        response = assistant.process_message(user_input)
        print(response + "\n")