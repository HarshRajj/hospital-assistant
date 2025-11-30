"""Chat service for text-based hospital assistant using Cerebras LLM with RAG."""
from typing import List, Dict
from openai import OpenAI

from config import settings
from config.prompts import get_system_prompt
from services.rag_service import rag_service
from services.appointment_service import appointment_service


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

# Define the appointment booking tool
APPOINTMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "book_appointment",
        "description": "Book a medical appointment for the user. Use this when the user wants to schedule an appointment. You MUST collect patient name, age, and gender before booking.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string",
                    "description": "Patient's full name"
                },
                "patient_age": {
                    "type": "integer",
                    "description": "Patient's age in years"
                },
                "patient_gender": {
                    "type": "string",
                    "enum": ["Male", "Female", "Other"],
                    "description": "Patient's gender"
                },
                "department": {
                    "type": "string",
                    "description": "The medical department (e.g., Cardiology, Pediatrics, Orthopedics, Neurology, General Medicine)"
                },
                "doctor": {
                    "type": "string",
                    "description": "The doctor's name (e.g., Dr. Harsh Sharma)"
                },
                "date": {
                    "type": "string",
                    "description": "Appointment date in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Appointment time in HH:MM format (24-hour, e.g., 09:00, 14:30)"
                }
            },
            "required": ["patient_name", "patient_age", "patient_gender", "department", "doctor", "date", "time"]
        }
    }
}

# Check available appointment slots
CHECK_SLOTS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_available_slots",
        "description": "Check available appointment time slots for a specific date, department, and doctor. Use this before booking to show available times.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "The medical department"
                },
                "doctor": {
                    "type": "string",
                    "description": "The doctor's name"
                },
                "date": {
                    "type": "string",
                    "description": "Date to check in YYYY-MM-DD format"
                }
            },
            "required": ["department", "doctor", "date"]
        }
    }
}

# Check user's existing appointments on a date
CHECK_USER_APPOINTMENTS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_user_appointments_on_date",
        "description": "Check if user already has appointments on a specific date. Call this before booking to inform user if they have existing appointments.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to check in YYYY-MM-DD format"
                }
            },
            "required": ["date"]
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
    
    def _get_system_prompt(self) -> str:
        """Get fresh system prompt with current date/time."""
        return get_system_prompt()
    
    async def _execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result.
        
        Args:
            tool_call: Tool call object from Cerebras
            
        Returns:
            Tool execution result as string
        """
        import json
        
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        print(f"🔧 Executing tool: {function_name} with args: {args}")
        
        if function_name == "search_hospital_knowledge":
            query = args.get("query", "")
            if rag_service.is_available():
                return await rag_service.search(query)
            else:
                return "Knowledge base is not available. Please contact the information desk."
        
        elif function_name == "book_appointment":
            # Book appointment using the authenticated user's ID
            result = appointment_service.book_appointment(
                user_id=getattr(self, '_current_user_id', 'demo_user'),
                patient_name=args.get("patient_name"),
                patient_age=args.get("patient_age"),
                patient_gender=args.get("patient_gender"),
                department=args.get("department"),
                doctor=args.get("doctor"),
                date=args.get("date"),
                time=args.get("time")
            )
            print(f"📅 Booking result: {result}")
            
            if result["success"]:
                return result["message"]
            else:
                return f"Unable to book appointment: {result['error']}"
        
        elif function_name == "check_available_slots":
            slots = appointment_service.get_available_slots(
                date=args.get("date"),
                department=args.get("department"),
                doctor=args.get("doctor")
            )
            
            if slots:
                return f"Available time slots on {args.get('date')} with {args.get('doctor')} in {args.get('department')}: {', '.join(slots)}"
            else:
                return f"No available slots on {args.get('date')} with {args.get('doctor')} in {args.get('department')}. Please try another date."
        
        elif function_name == "check_user_appointments_on_date":
            user_id = getattr(self, '_current_user_id', 'demo_user')
            existing = appointment_service.get_user_appointments_on_date(user_id, args.get("date"))
            
            if existing:
                appointments_text = ", ".join([f"{apt['doctor']} at {apt['time']}" for apt in existing])
                return f"You already have {len(existing)} appointment(s) on {args.get('date')}: {appointments_text}. You can still book another appointment on the same day if you'd like."
            else:
                return f"You don't have any appointments on {args.get('date')}."
        
        return "Unknown tool"
    
    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_id: str = "demo_user"
    ) -> Dict[str, str]:
        """Process a chat message with RAG function calling.
        
        Args:
            message: User's message
            conversation_history: Optional list of previous messages
            user_id: Authenticated user's ID for booking appointments
            
        Returns:
            Dictionary with response, context usage, and model info
        """
        if conversation_history is None:
            conversation_history = []
        
        # Store user_id for tool execution
        self._current_user_id = user_id
        
        # Build messages for LLM with fresh timestamp
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        max_iterations = 10  # Prevent infinite loops (increased for complex queries)
        iteration = 0
        tool_used = False
        
        try:
            while iteration < max_iterations:
                iteration += 1
                print(f"🔄 Iteration {iteration}/{max_iterations}")
                
                # Call LLM with function calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=[RAG_TOOL, APPOINTMENT_TOOL, CHECK_SLOTS_TOOL, CHECK_USER_APPOINTMENTS_TOOL],
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=800,
                )
                
                response_message = response.choices[0].message
                
                # Check if LLM wants to call a function
                if response_message.tool_calls:
                    tool_used = True
                    print(f"🤖 LLM wants to call {len(response_message.tool_calls)} tool(s)")
                    
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
                print(f"✅ Final response (tool_used={tool_used}): {response_message.content[:100]}...")
                return {
                    "response": response_message.content,
                    "context_used": tool_used,
                    "model": self.model
                }
            
            # Max iterations reached - provide helpful fallback
            print(f"⚠️ Max iterations ({max_iterations}) reached")
            return {
                "response": "I understand your question, but I need a bit more clarity. Could you please:\n\n• Be more specific about what you need\n• Ask one question at a time\n• Rephrase your request\n\nI'm here to help with hospital information and appointment bookings!",
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

