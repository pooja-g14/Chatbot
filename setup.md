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
CREATE DATABASE chatbot_db;
```

## 2. Create the Table

Run the following SQL statement in your database to create the `chat_sessions` table:

```sql
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY,
    history JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Environment Configuration

Add the connection URI to your `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/chatbot_db
GEMINI_API_KEY=your_gemini_api_key_here
```