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
                    "SELECT history FROM chat_sessions WHERE session_id = %s",
                    (session_id,)
                )
                row = cur.fetchone()
                if row:
                    history = row[0]
                    if isinstance(history, str):
                        import json
                        return json.loads(history)
                    return history
                return []
    except Exception as e:
        logger.error(f"Error fetching chat history from database: {e}")
        logger.error(traceback.format_exc())
        return []

def save_chat_history(session_id: str, history: list):
    """
    Saves/updates the complete chat history JSON array for a session.
    """
    try:
        import json
        history_json = json.dumps(history)
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chat_sessions (session_id, history, updated_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (session_id)
                    DO UPDATE SET history = EXCLUDED.history, updated_at = CURRENT_TIMESTAMP
                    """,
                    (session_id, history_json)
                )
    except Exception as e:
        logger.error(f"Error saving chat history to database: {e}")
        logger.error(traceback.format_exc())

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
            contents=contents
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