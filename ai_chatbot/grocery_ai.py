from openai import OpenAI
import os
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_best_model():
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        for preferred in ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]:
            if any(preferred in model_id for model_id in available_models):
                return preferred
        return "gpt-3.5-turbo"  # fallback to a commonly available model
    except Exception:
        return "gpt-3.5-turbo"  # fallback if model listing fails

def detect_language(text: str) -> str:
    try:
        return "nl" if detect(text) == "nl" else "en"
    except Exception:
        return "en"

def grocery_chat(user_input: str, history=None) -> str:
    if history is None:
        history = []

    model = get_best_model()
    language = detect_language(user_input)

    system_prompt = (
        "You are a helpful grocery assistant.\n"
        "- If the user speaks Dutch, reply in Dutch; otherwise reply in UK English.\n"
        "- If they say what they feel like eating, ask: 'Would you like a quick & easy recipe or a professional one?'\n"
        "- If they list ingredients, suggest what they can cook.\n"
        "- When you provide a recipe, do this ORDER exactly:\n"
        "  A) Write the readable recipe first (Ingredients + Steps), friendly tone, max 10 steps.\n"
        "  B) Then output EXACTLY ONE fenced JSON block (```json ... ```), with keys:\n"
        '     { \"dish\": string, \"language\": \"en\"|\"nl\", \"style\": \"quick\"|\"professional\", '
        '\"ingredients\": string[], \"steps\": string[], \"image_prompt\": string }\n'
        "     • 'style' MUST reflect the user choice: 'quick' for quick/easy; 'professional' otherwise.\n"
        "     • 'image_prompt' MUST start with the exact dish name and MUST match the chosen style:\n"
        "        - quick: simple home-style plating, minimal props, overhead or 45° angle, soft natural light\n"
        "        - professional: refined restaurant plating, depth of field, studio lighting, subtle steam\n"
        "     • 'image_prompt' MUST only mention ingredients present in the 'ingredients' array (include 2–4 of them); "
        "       do NOT invent ingredients.\n"
        "     • No duplicate array items. No repeated keys. Valid JSON only.\n"
        "  C) On a new line immediately after the JSON fence, output the literal tag [GENERATE_LIST_BUTTON].\n"
        "- Do not output more than one JSON fence. Do not put anything after the tag."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for i in range(0, len(history), 2):
        messages.append({"role": "user", "content": history[i]})
        if i + 1 < len(history):
            messages.append({"role": "assistant", "content": history[i + 1]})
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_grocery_image(prompt: str) -> str:
    try:
        resp = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024"
        )
        return resp.data[0].url
    except Exception as e:
        # Fallback or error handling
        return f"Error generating image: {str(e)}"
