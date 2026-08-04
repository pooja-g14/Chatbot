import os
import traceback
from psycopg_pool import ConnectionPool
# Set up logging
from logger import logger

from dotenv import load_dotenv
load_dotenv()

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