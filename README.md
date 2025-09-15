# 🛒 Grocery AI Backend

FastAPI-based backend for a grocery chatbot and shopping list generator in English(UK) and Dutch language.

## 🔧 Setup

1. Clone the repo:
```bash
git clone https://github.com/sparktechagency/DealDetector-AI.git
cd grocery-ai-backend
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
``` bash
uvicorn app:app --reload
```

## 📌 Endpoints
- GET /
  ✅ Server status

- POST /chat
  Input: { "message": "..." }
  Output: { "response": "..." }

- POST /generate-list
  Input: { "recipe_text": "..." }
  Output: { "shopping_list": [...] }

## 📁 Structure
- app.py: FastAPI app & routes
- grocery_ai.py: Chat logic
- list_generator.py: Extracts ingredients
- requirements.txt
