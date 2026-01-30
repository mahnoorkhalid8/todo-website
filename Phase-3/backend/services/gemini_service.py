import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from groq import Groq
import sys
from pathlib import Path

# Load environment variables from .env file
# Look for .env file in the project root directory
project_root = Path(__file__).parent.parent.parent  # Go up to project root (backend -> Phase-3)
env_path = project_root / ".env"

if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try loading from current directory
    load_dotenv()

# Configure the Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("Warning: GROQ_API_KEY not found in environment variables")

class GeminiService:
    def __init__(self):
        if GROQ_API_KEY:
            self.client = client
            self.model_name = "llama-3.1-8b-instant"  # Using Llama 3.1 8B Instant model which is available on Groq
        else:
            self.client = None
            self.model_name = None

    def generate_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response using Groq API based on user message and conversation history.
        """
        if not GROQ_API_KEY:
            return "Groq API key not configured. Please set GROQ_API_KEY in environment variables."

        if not self.client:
            return "Error: Groq client not initialized."

        try:
            # Prepare the messages for the chat completion
            messages = []

            # Add system message
            messages.append({
                "role": "system",
                "content": "You are an AI assistant for a Todo application. Your job is to help users manage their tasks through natural language. Be helpful and friendly."
            })

            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Include last 10 messages for context
                    role = "user" if msg['role'] == 'user' else 'assistant'
                    messages.append({"role": role, "content": msg['content']})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Generate chat completion using Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
            )

            if chat_completion.choices and chat_completion.choices[0].message.content:
                return chat_completion.choices[0].message.content.strip()
            else:
                return "I couldn't generate a response. Could you please rephrase your request?"

        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return f"I encountered an error processing your request: {str(e)}"

    def enhance_response(self, base_response: str, user_intent: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Enhance a base response with more natural, conversational language using Groq.
        """
        if not GROQ_API_KEY or not self.client:
            # If Groq is not available, return the base response
            return base_response

        try:
            enhancement_prompt = f"""
            You are an AI assistant for a Todo application. Your job is to make the following response sound more natural and conversational.

            Original response: {base_response}
            User's intent: {user_intent}

            Please rewrite this response to sound more natural and friendly, as if having a conversation with the user. Keep the essential information but make it more engaging.
            """

            messages = [
                {"role": "system", "content": "You are a helpful AI assistant for a Todo application."},
                {"role": "user", "content": enhancement_prompt}
            ]

            if conversation_history:
                history_context = "\nPrevious conversation context:\n"
                for msg in conversation_history[-3:]:  # Include last 3 messages for context
                    role = "User" if msg['role'] == 'user' else 'Assistant'
                    history_context += f"{role}: {msg['content']}\n"

                # Update the user message with context
                enhancement_prompt_with_context = f"{history_context}\n{enhancement_prompt}"
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant for a Todo application."},
                    {"role": "user", "content": enhancement_prompt_with_context}
                ]

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
            )

            if chat_completion.choices and chat_completion.choices[0].message.content:
                return chat_completion.choices[0].message.content.strip()
            else:
                # If enhancement fails, return the original response
                return base_response

        except Exception as e:
            print(f"Error enhancing response with Groq: {str(e)}")
            # Return original response if enhancement fails
            return base_response

# Global instance
gemini_service = GeminiService()