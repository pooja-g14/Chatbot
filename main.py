import os
import logging
import traceback
from google import genai
from google.genai import types
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Gemini Client (automatically picks up GEMINI_API_KEY from env)
client = genai.Client()

# Initialize PostgreSQL Connection Pool
db_url = os.environ.get("DATABASE_URL")

try:
    pool = ConnectionPool(conninfo=db_url, open=True, min_size=1, max_size=10)
except Exception as e:
    logger.error(f"Failed to initialize ConnectionPool: {e}")
    logger.error(traceback.format_exc())

def get_chat_history(session_id: str = "default"):
    """
    Retrieves the chat history for a session from the PostgreSQL database.
    """
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                    (session_id,)
                )
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Error fetching chat history from database: {e}")
        logger.error(traceback.format_exc())
        return []

def save_message(role: str, content: str, session_id: str = "default"):
    """
    Saves a message to the database.
    """
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)",
                    (session_id, role, content)
                )
    except Exception as e:
        logger.error(f"Error saving message to database: {e}")
        logger.error(traceback.format_exc())

def run_agent(message: str):
    """
    Generator function that streams responses from gemini-3.1-flash-lite.
    First retrieves historical context from the database, sends it along
    with the new user message, streams the chunks back, and saves the conversation.
    """
    # 1. Retrieve history
    history = get_chat_history()
    
    # 2. Format history for Google GenAI SDK
    contents = []
    for role, content in history:
        contents.append(
            types.Content(
                role="user" if role == "user" else "model",
                parts=[types.Part.from_text(text=content)]
            )
        )
    
    # Append current user message
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
    )
    
    # Save user message to database
    save_message("user", message)
    
    # 3. Call the API stream using gemini-3.1-flash-lite
    try:
        response = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite",
            contents=contents
        )
        
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
                
        # Save AI response to database
        if full_response:
            save_message("model", full_response)
    except Exception as e:
        logger.error(f"Error during Gemini API generation: {e}")
        yield f"\n[Error: {e}]"