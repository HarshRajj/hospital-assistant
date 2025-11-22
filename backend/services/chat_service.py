"""Chat service for text-based hospital assistant using Cerebras LLM with RAG."""
from typing import List, Dict
from openai import OpenAI

from config import settings, HOSPITAL_ASSISTANT_SYSTEM_PROMPT
from services.rag_service import rag_service


# Define the RAG function tool for Cerebras
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_hospital_knowledge",
        "description": "Search the hospital's knowledge base for information about services, departments, doctors, hours, policies, and facilities. Use this function for ANY question about the hospital. Do not answer hospital questions without calling this function.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question or topic to search for in the hospital knowledge base."
                }
            },
            "required": ["query"]
        }
    }
}


class ChatService:
    """Service for text-based chat with RAG-powered hospital knowledge using function calling."""
    
    def __init__(self):
        """Initialize ChatService with Cerebras LLM via OpenAI SDK."""
        self.client = OpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        )
        self.model = "gpt-oss-120b"
        self.system_prompt = HOSPITAL_ASSISTANT_SYSTEM_PROMPT
    
    async def _execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result.
        
        Args:
            tool_call: Tool call object from Cerebras
            
        Returns:
            Tool execution result as string
        """
        if tool_call.function.name == "search_hospital_knowledge":
            import json
            args = json.loads(tool_call.function.arguments)
            query = args.get("query", "")
            
            if rag_service.is_available():
                return await rag_service.search(query)
            else:
                return "Knowledge base is not available. Please contact the information desk."
        
        return "Unknown tool"
    
    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Process a chat message with RAG function calling.
        
        Args:
            message: User's message
            conversation_history: Optional list of previous messages
            
        Returns:
            Dictionary with response, context usage, and model info
        """
        if conversation_history is None:
            conversation_history = []
        
        # Build messages for LLM
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        tool_used = False
        
        try:
            while iteration < max_iterations:
                iteration += 1
                
                # Call LLM with function calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=[RAG_TOOL],
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=500,
                )
                
                response_message = response.choices[0].message
                
                # Check if LLM wants to call a function
                if response_message.tool_calls:
                    tool_used = True
                    
                    # Add assistant's tool call request to messages
                    messages.append(response_message)
                    
                    # Execute each tool call
                    for tool_call in response_message.tool_calls:
                        tool_result = await self._execute_tool_call(tool_call)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": tool_result
                        })
                    
                    # Continue loop to get final response with tool results
                    continue
                
                # No more tool calls - we have the final response
                return {
                    "response": response_message.content,
                    "context_used": tool_used,
                    "model": self.model
                }
            
            # Max iterations reached
            return {
                "response": "I apologize, but I'm having trouble processing your request. Please try rephrasing your question.",
                "context_used": tool_used,
                "model": self.model
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n❌ Chat Error Details:\n{error_details}")
            raise Exception(f"Chat completion error: {str(e)}")


# Singleton instance
chat_service = ChatService()

