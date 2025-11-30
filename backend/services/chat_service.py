"""Chat service for hospital assistant using Cerebras LLM with RAG."""
import json
from typing import List, Dict
from openai import OpenAI

from config import settings
from config.prompts import get_system_prompt
from services.rag_service import rag_service
from services.appointment_service import appointment_service


# Tool definitions for Cerebras function calling
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_hospital_knowledge",
        "description": "Search hospital knowledge base. Use for ANY hospital question.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to search for"}
            },
            "required": ["query"]
        }
    }
}

APPOINTMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "book_appointment",
        "description": "Book an appointment. Collect name, age, gender first.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "patient_age": {"type": "integer"},
                "patient_gender": {"type": "string", "enum": ["Male", "Female", "Other"]},
                "department": {"type": "string"},
                "doctor": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD format"},
                "time": {"type": "string", "description": "HH:MM format"}
            },
            "required": ["patient_name", "patient_age", "patient_gender", "department", "doctor", "date", "time"]
        }
    }
}

CHECK_SLOTS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_available_slots",
        "description": "Check available appointment slots for a doctor on a date.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {"type": "string"},
                "doctor": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD format"}
            },
            "required": ["department", "doctor", "date"]
        }
    }
}

CHECK_USER_APPOINTMENTS_TOOL = {
    "type": "function",
    "function": {
        "name": "check_user_appointments_on_date",
        "description": "Check if user has existing appointments on a date.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD format"}
            },
            "required": ["date"]
        }
    }
}


class ChatService:
    """Service for text-based chat with RAG-powered hospital knowledge."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        )
        self.model = "gpt-oss-120b"
        self._current_user_id = "demo_user"
    
    async def _execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result."""
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        if function_name == "search_hospital_knowledge":
            if rag_service.is_available():
                return await rag_service.search(args["query"])
            return "Knowledge base is not available."
        
        elif function_name == "book_appointment":
            result = appointment_service.book_appointment(
                user_id=self._current_user_id,
                patient_name=args["patient_name"],
                patient_age=args["patient_age"],
                patient_gender=args["patient_gender"],
                department=args["department"],
                doctor=args["doctor"],
                date=args["date"],
                time=args["time"]
            )
            if result["success"]:
                return result["message"]
            return f"Unable to book: {result['error']}"
        
        elif function_name == "check_available_slots":
            slots = appointment_service.get_available_slots(
                date=args["date"],
                department=args["department"],
                doctor=args["doctor"]
            )
            if slots:
                return f"Available slots on {args['date']} with {args['doctor']}: {', '.join(slots)}"
            return f"No available slots on {args['date']} with {args['doctor']}."
        
        elif function_name == "check_user_appointments_on_date":
            existing = appointment_service.get_user_appointments_on_date(
                self._current_user_id, 
                args["date"]
            )
            if existing:
                appointments_text = ", ".join([f"{apt['doctor']} at {apt['time']}" for apt in existing])
                return f"You have {len(existing)} appointment(s) on {args['date']}: {appointments_text}"
            return f"No appointments on {args['date']}."
        
        return "Unknown tool"
    
    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_id: str = "demo_user"
    ) -> Dict[str, str]:
        """Process a chat message with RAG function calling."""
        if conversation_history is None:
            conversation_history = []
        
        self._current_user_id = user_id
        
        # Build messages for LLM
        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        tools = [RAG_TOOL, APPOINTMENT_TOOL, CHECK_SLOTS_TOOL, CHECK_USER_APPOINTMENTS_TOOL]
        max_iterations = 10
        tool_used = False
        
        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=800,
            )
            
            response_message = response.choices[0].message
            
            # If no tool calls, return final response
            if not response_message.tool_calls:
                return {
                    "response": response_message.content,
                    "context_used": tool_used,
                    "model": self.model
                }
            
            # Execute tool calls
            tool_used = True
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                tool_result = await self._execute_tool_call(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                })
        
        # Max iterations reached
        return {
            "response": "Please ask one question at a time for better results.",
            "context_used": tool_used,
            "model": self.model
        }


chat_service = ChatService()

