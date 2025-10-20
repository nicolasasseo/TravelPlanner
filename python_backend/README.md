# Travel Planner Python Backend

This is the Python FastAPI backend for the Travel Planner AI agent.

## Setup

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the `python_backend` directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPAPI_API_KEY=your_serpapi_api_key_here
   ```

## Running the Backend

### Option 1: Using the batch file (Windows)

Double-click `start_backend.bat` or run:

```bash
start_backend.bat
```

### Option 2: Using uvicorn directly

```bash
uvicorn setup:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

## API Endpoints

- `POST /chat-trip` - Chat with the AI agent about trips
- `GET /trip-weather/{trip_id}` - Get weather information for a destination

## Testing the API

You can test the API using the FastAPI docs at `http://localhost:8000/docs`
