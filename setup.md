## Create virtual environment and install dependencies

1. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies**

```bash
pip install --no-cache-dir -r requirements.txt
```

# PostgreSQL Setup Instructions

Follow these steps to set up the PostgreSQL database and table for the chatbot history.

## 1. Create the Database

Create a new database in PostgreSQL (e.g., using `psql` or PGAdmin):

```sql
CREATE DATABASE git_chatbot;
```

## 2. Create the Table

Run the following SQL statement in your database to create the `chat_messages` table:

```sql
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL DEFAULT 'default',
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index session_id for faster history lookup
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
```

## 3. Environment Configuration

Add the connection URI to your `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/git_chatbot
GEMINI_API_KEY=your_gemini_api_key_here
```
