import traceback
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

# Set up logging
from logger import logger

from .database import get_chat_history, save_chat_history

# Initialize Gemini Client (automatically picks up GEMINI_API_KEY from env)
client = genai.Client()

def run_agent(message: str, session_id: str):
    """
    Generator function that streams responses from gemini-3.1-flash-lite.
    First retrieves historical context from the database, sends it along
    with the new user message, streams the chunks back, and saves the conversation.
    """
    # 1. Retrieve history
    history = get_chat_history(session_id)
    
    # 2. Format history for Google GenAI SDK
    contents = []
    for msg in history:
        contents.append(
            types.Content(
                role=msg.get("role"),
                parts=[types.Part.from_text(text=msg.get("content"))]
            )
        )
    
    # Append current user message
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
    )
    
    # Save user message to database history
    history.append({"role": "user", "content": message})
    save_chat_history(session_id, history)
    
    # 3. Call the API stream using gemini-3.1-flash-lite
    try:
        response = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
        )
        
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
                
        # Save AI response to database history
        if full_response:
            history.append({"role": "model", "content": full_response})
            save_chat_history(session_id, history)
    except Exception as e:
        logger.error(f"Error during Gemini API generation: {e}")
        logger.error(traceback.format_exc())
        yield f"\n[Error: {e}]"