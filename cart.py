import os
import glob
import time


# ──────────────────────────────────────────────
# 1. PARSE THE TXT FILE
# ──────────────────────────────────────────────
def parse_card_list(directory="Cards_to_add"):
    """
    Reads the first .txt file found in the given directory.
    Expected format per line (comma-separated):
        url, quality, quantity

    Example:
        https://www.cardkingdom.com/mtg/foundations/llanowar-elves, NM, 4

    Returns a list of dicts:
        [{"url": "...", "quality": "NM", "quantity": 4}, ...]
    """
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt file found in '{directory}/' directory.")

    filepath = txt_files[0]
    print(f"\n>>> Reading card list from: {filepath}")

    cards = []
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 3:
                print(f"    ⚠ Skipping line {line_num} (expected 3 fields): {line}")
                continue

            url, quality, quantity = parts
            try:
                quantity = int(quantity)
            except ValueError:
                print(f"    ⚠ Skipping line {line_num} (invalid quantity): {line}")
                continue

            cards.append(
                {
                    "url": url,
                    "quality": quality.upper(),
                    "quantity": quantity,
                }
            )

    print(f">>> Parsed {len(cards)} card(s) from file.\n")
    return cards


# ──────────────────────────────────────────────
# 2. EXTRACT PRODUCT ID (Single Card)
# ──────────────────────────────────────────────
def extract_product_id(driver, url):
    """
    Navigates to a card page and extracts the product_id.
    Uses the same browser session passed from main.py.
    """
    print(f">>> Loading: {url}")
    driver.get(url)

    selector = 'form.addToCartForm input[name="product_id[0]"]'

    if driver.is_element_present(selector, wait=10):
        product_id = driver.run_js(f"return document.querySelector('{selector}').value")
        print(f"    ✔ Product ID: {product_id}")
        return product_id
    else:
        print(f"    ✘ Product ID not found")
        return None


# ──────────────────────────────────────────────
# 3. ADD CARDS TO CART VIA API (through browser)
# ──────────────────────────────────────────────
def add_card_to_cart(driver, card):
    """
    Adds a single card to cart by executing fetch() inside the browser.
    This inherits all cookies, Cloudflare tokens, and session state
    automatically — no separate requests.Session needed.
    """
    import json

    payload = {
        "product_id": card["product_id"],
        "style": card["quality"],
        "quantity": card["quantity"],
    }

    # Synchronous XMLHttpRequest executed inside the authenticated browser
    js_code = """
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://www.cardkingdom.com/api/cart/add", false);
    xhr.setRequestHeader("accept", "application/json;charset=UTF-8");
    xhr.setRequestHeader("content-type", "application/json;charset=UTF-8");
    xhr.setRequestHeader("x-requested-with", "XMLHttpRequest");
    xhr.send(JSON.stringify(%s));
    return JSON.stringify({status: xhr.status, body: xhr.responseText});
    """ % json.dumps(payload)

    try:
        result_raw = driver.run_js(js_code)
        result = json.loads(result_raw)
        status = result.get("status")
        body = result.get("body", "")

        if status == 200:
            print(f"    ✔ Added successfully! (HTTP {status})")
            return True
        else:
            print(f"    ✘ Failed (HTTP {status}): {body[:200]}")
            return False
    except Exception as e:
        print(f"    ✘ JS Error: {e}")
        return False


def add_cards_to_cart(driver, cards):
    """
    Iterates through cards and adds each to cart via browser fetch().
    """
    print("\n" + "=" * 50)
    print(">>> ADDING CARDS TO CART")
    print("=" * 50)

    success_count = 0
    for i, card in enumerate(cards):
        if not card.get("product_id"):
            print(f"\n[{i + 1}/{len(cards)}] SKIP (no product_id): {card['url']}")
            continue

        print(f"\n[{i + 1}/{len(cards)}] Adding: {card['url']}")
        print(
            f"    Payload: product_id={card['product_id']}, style={card['quality']}, qty={card['quantity']}"
        )

        if add_card_to_cart(driver, card):
            success_count += 1

        time.sleep(1)

    print(f"\n>>> Done: {success_count}/{len(cards)} cards added to cart.")
    return success_count


# ──────────────────────────────────────────────
# 4. PROCESS CART (orchestrates steps 1-3)
# ──────────────────────────────────────────────
def process_cart(driver, cookies):
    """
    Full cart pipeline — called from main.py with the same driver.
    1. Parse card list from Cards_to_add/
    2. Extract product IDs (same browser)
    3. POST to API
    """
    # Step 1: Parse
    cards = parse_card_list("Cards_to_add")
    if not cards:
        print("!!! No cards to process.")
        return

    print(">>> Card list preview:")
    for c in cards:
        print(f"    {c['url']}  |  {c['quality']}  |  x{c['quantity']}")

    # Step 2: Extract product IDs (same browser session)
    print("\n" + "=" * 50)
    print(">>> EXTRACTING PRODUCT IDs")
    print("=" * 50)

    for i, card in enumerate(cards):
        print(f"\n[{i + 1}/{len(cards)}]")
        card["product_id"] = extract_product_id(driver, card["url"])
        time.sleep(1)

    # Step 3: Add to cart via browser fetch
    add_cards_to_cart(driver, cards)
