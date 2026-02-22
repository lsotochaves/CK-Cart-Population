import os
import glob
import json
import time
import requests 
from bs4 import BeautifulSoup


def parse_card_list(directory="Cards_to_add"):
    """
    Reads the first .txt file found in the given directory.
    Expected format per line (comma-separated):
        url, quality, quantity

    This is a pure function (data in → data out), so it stays
    outside the class on purpose.
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
                print(f" Skipping line {line_num} (expected 3 fields): {line}")
                continue

            url, quality, quantity = parts
            try:
                quantity = int(quantity)
            except ValueError:
                print(f" Skipping line {line_num} (invalid quantity): {line}")
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
# CART MANAGER
# ──────────────────────────────────────────────
class CartManager:
    """
    Manages the full cart pipeline: load → extract IDs → add to cart.

    All operations use the same browser session (self.driver),
    so Cloudflare tokens and cookies are always valid.

    Usage:
        cart = CartManager(driver)
        cart.load_from_file("Cards_to_add")
        cart.extract_product_ids()
        cart.add_all()
        cart.summary()
    """

    PRODUCT_ID_SELECTOR = 'form.addToCartForm input[name="product_id[0]"]'

    API_URL = "https://www.cardkingdom.com/api/cart/add"

    def __init__(self, cookies, delay=1):
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        self.session.headers.update({
            "accept": "application/json;charset=UTF-8",
            "content-type": "application/json;charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        })
        self.delay = delay
        self.cards = []
        self.success_count = 0
        self.fail_count = 0

    def load_from_file(self, directory="Cards_to_add"):
        """Parse card list from a .txt file and store in self.cards."""
        self.cards = parse_card_list(directory)
        return self

    def load_from_list(self, card_list):
        """Load cards directly from a list of dicts (for programmatic use)."""
        self.cards = card_list
        return self

    def preview(self):
        """Print a preview of the loaded cards."""
        if not self.cards:
            print(">>> No cards loaded.")
            return self

        print(">>> Card list preview:")
        for c in self.cards:
            print(f"    {c['url']}  |  {c['quality']}  |  x{c['quantity']}")
        return self

    def extract_product_ids(self):
        """
        Visit each card's URL in the browser and extract its product_id.
        Enriches self.cards in place.
        """
        print("\n" + "=" * 50)
        print(">>> EXTRACTING PRODUCT IDs")
        print("=" * 50)

        for i, card in enumerate(self.cards):
            print(f"\n[{i + 1}/{len(self.cards)}]")
            card["product_id"] = self._extract_single_id(card["url"])
            time.sleep(self.delay)

        return self

    def add_all(self):
        """
        Add all cards (that have a product_id) to the cart via
        XMLHttpRequest inside the browser.
        """
        print("\n" + "=" * 50)
        print(">>> ADDING CARDS TO CART")
        print("=" * 50)

        self.success_count = 0
        self.fail_count = 0

        for i, card in enumerate(self.cards):
            if not card.get("product_id"):
                print(
                    f"\n[{i + 1}/{len(self.cards)}] SKIP (no product_id): {card['url']}"
                )
                self.fail_count += 1
                continue

            print(f"\n[{i + 1}/{len(self.cards)}] Adding: {card['url']}")
            print(
                f"    product_id={card['product_id']}, style={card['quality']}, qty={card['quantity']}"
            )

            if self._add_single(card):
                self.success_count += 1
            else:
                self.fail_count += 1

            time.sleep(self.delay)

        return self

    def summary(self):
        """Print a final summary of the cart operation."""
        total = len(self.cards)
        print(
            f"\n>>> Cart Summary: {self.success_count}/{total} added, {self.fail_count} failed."
        )
        return self

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────
    def _extract_single_id(self, url):
        resp = self.session.get(url)
        if resp.status_code != 200:
            print(f"    Failed to load page (HTTP {resp.status_code})")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        el = soup.select_one('form.addToCartForm input[name="product_id[0]"]')
        return el['value'] if el else None

    def _add_single(self, card):
        payload = {
            "product_id": card["product_id"],
            "style": card["quality"],
            "quantity": card["quantity"],
        }
        resp = self.session.post(self.API_URL, json=payload)
        if resp.status_code == 200:
            print(f"    Added! (HTTP {resp.status_code})")
            return True
        else:
            print(f"    Failed (HTTP {resp.status_code}): {resp.text[:200]}")
            return False

    def finish_execution(self):
        """
        Redirects the browser to the cart page to verify contents.
        """
        cart_url = "https://www.cardkingdom.com/cart"
        print(f"\n>>> Redirecting to cart summary: {cart_url}")
        self.driver.get(cart_url)
