import json
import re
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)

def _try_loads(s):
    try:
        return json.loads(s)
    except Exception:
        return None

def _dedupe_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        k = (x or "").strip()
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out

def _sanitize_recipe_dict(d):
    dish = (d.get("dish") or "").strip() or None
    lang = d.get("language") if d.get("language") in ("en", "nl") else "en"
    style = d.get("style") if d.get("style") in ("quick", "professional") else "quick"

    ingredients = d.get("ingredients") or []
    if not isinstance(ingredients, list):
        ingredients = [str(ingredients)]
    ingredients = _dedupe_preserve([str(i) for i in ingredients])

    steps = d.get("steps") or []
    if not isinstance(steps, list):
        steps = [str(steps)]
    steps = _dedupe_preserve([str(s) for s in steps])[:10]

    image_prompt = (d.get("image_prompt") or "").strip() or None

    return {
        "dish": dish,
        "language": lang,
        "style": style,
        "ingredients": ingredients,
        "steps": steps,
        "image_prompt": image_prompt,
    }

def parse_recipe_json(text: str):
    matches = JSON_BLOCK_RE.findall(text or "")
    for block in reversed(matches):  
        data = _try_loads(block)
        needed = ("dish", "language", "style", "ingredients", "steps", "image_prompt")
        if isinstance(data, dict) and all(k in data for k in needed):
            return _sanitize_recipe_dict(data)
    return None

def extract_ingredients_from_free_text(recipe_text: str) -> str:
    prompt = (
        "Extract a clean shopping list from this recipe. Reply only with a bullet list of ingredients "
        "(no quantities needed). Do not repeat items.\n\n"
        f"Recipe:\n{recipe_text}"
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts ingredient lists."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return resp.choices[0].message.content

def extract_ingredients(recipe_text: str):
    """
    Returns (ingredient_list:list[str], meta:dict)
    meta: dish, language, style, image_prompt, steps
    """
    parsed = parse_recipe_json(recipe_text)
    if parsed:
        return parsed["ingredients"], {
            "dish": parsed["dish"],
            "language": parsed["language"],
            "style": parsed["style"],
            "image_prompt": parsed["image_prompt"],
            "steps": parsed["steps"],
        }

    bullets = extract_ingredients_from_free_text(recipe_text)
    items = [line.strip("-•* ").strip() for line in bullets.splitlines() if line.strip()]
    items = _dedupe_preserve(items)
    return items, {
        "dish": None,
        "language": "en",
        "style": "quick",
        "image_prompt": None,
        "steps": [],
    }
