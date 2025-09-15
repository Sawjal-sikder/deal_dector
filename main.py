import json
from datetime import datetime, timezone
from typing import Optional, List
from grocery_ai import grocery_chat, generate_grocery_image
from list_generator import extract_ingredients

GREETING = "Hey! What do you feel like having today? / Hoi! Waar heb je vandaag zin in?"

def _pick_ingredients(ingredients: Optional[List[str]], n: int = 4) -> List[str]:
    if not ingredients:
        return []
    out = []
    for x in ingredients:
        x = (x or "").strip()
        if not x:
            continue
        out.append(x.split(",")[0])
        if len(out) >= n:
            break
    return out

def build_style_prompt(dish: str, style: str, _fallback_image_prompt: Optional[str]) -> str:
    """
    Build a clean, style-consistent image prompt.
    We intentionally ignore fallback to avoid messy/duplicated phrasing.
    """
    dish_name = (dish or "the dish").strip()
    base_common = f"{dish_name}, realistic food photography, single serving, no text or logos, clean background"

    style = (style or "quick").strip().lower()
    if style.startswith("pro"):
        style_part = (
            "refined restaurant plating, selective focus, shallow depth of field, "
            "studio lighting, subtle steam, matte dark backdrop"
        )
    else:
        style_part = (
            "simple home-style plating in a plain bowl or plate, minimal props, natural light, "
            "overhead or 45° angle"
        )
    return f"{base_common}, {style_part}"

def print_json_payload(payload: dict) -> None:
    print("\n=== JSON payload (pretty) ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("\n=== JSON payload (one line) ===")
    print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))

def _append_to_aggregate(payload: dict, path: str = "shopping_list.json") -> None:
    """
    Keep a single JSON array for all sessions so frontend can consume easily.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    except FileNotFoundError:
        data = []
    except Exception:
        data = []

    data.append(payload)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print(GREETING)

    history: List[str] = []

    while True:
        user_input = input("\nMe: ")
        if user_input.lower().strip() in {"exit", "quit"}:
            print(" Goodbye!")
            break

        # 1) Get assistant reply
        response = grocery_chat(user_input, history)
        print("\nGPT:\n", response.strip())

        # Save to history
        history.extend([user_input, response])

        # 2) Only proceed to generate when the tag is present
        if "[GENERATE_LIST_BUTTON]" in response:
            print("\n Generate shopping list?")
            print("1. yes")
            print("2. no")
            choice = input("Choose (1/2): ").strip()

            if choice == "1":
                print("\nGenerating your shopping list...\n")
                items, meta = extract_ingredients(response)

                # 4) Build a style-aware image prompt (clean)
                style = meta.get("style") or "quick"
                dish = meta.get("dish") or ""
                image_prompt = build_style_prompt(dish, style, meta.get("image_prompt"))

                # 5) Generate the image URL (best-effort; don't crash if it fails)
                image_url = None
                try:
                    print("Generating food image...")
                    image_url = generate_grocery_image(image_prompt)
                except Exception as e:
                    print(f"Image generation failed: {e}")

                # 6) Build a single JSON payload for the frontend
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "generated_by_ai": True,
                    "language": meta.get("language", "en"),
                    "dish": dish or None,
                    "style": style,                 
                    "items": items,                    
                    "steps": meta.get("steps", []),   
                    "image_prompt": image_prompt,
                    "image_url": image_url,
                }

                _append_to_aggregate(payload, "shopping_list.json")
                with open("shopping_result.json", "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)

                print("Appended to shopping_list.json")
                print("Saved last result in shopping_result.json")
                print_json_payload(payload)
            else:
                print("Okay! Ask for another dish or type 'quit' to exit.")

if __name__ == "__main__":
    main()
