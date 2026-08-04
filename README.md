# AI Text Chatbot with PostgreSQL History

A lightweight, streaming chatbot powered by FastAPI, PostgreSQL, and Google Gemini. The application maintains separate chat histories for different browser sessions by generating unique UUIDs on the client-side and storing the entire history as a JSON document per session in a PostgreSQL database.

## How to Run

**Run the Server**: Run the FastAPI application:
```bash
python app.py
```
**Open in Browser**: Open `http://localhost:8001` in your browser.

## Project Structure

```
Chatbot/
├── app.py                  # FastAPI server entrypoint
├── main.py                 # Database operations and streaming completions
├── index.html              # Simple frontend interface
├── setup.md                # PostgreSQL database and table setup instructions
├── requirements.txt        # Python package dependencies
└── .env                    # Environment configurations (API keys, database URLs)
```
