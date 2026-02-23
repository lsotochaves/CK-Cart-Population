import os
import glob
import json
import time
from dotenv import load_dotenv


class CartManager:
    """
    Manages the full cart pipeline: load → extract IDs → add to cart.

    All operations use the same browser session (self.driver),
    so Cloudflare tokens and cookies are always valid.

    Usage:
        cart = CartManager(driver)
        cart.load_from_file("Cards_to_add")
        cart.extract_product_ids()
        results = cart.add_all()
    """

    API_URL = "https://www.cardkingdom.com/api/cart/add"
    PRODUCT_ID_SELECTOR = 'form.addToCartForm input[name="product_id[0]"]'

    def __init__(self, driver, delay=1):
        self.driver = driver
        self.delay = delay
        self.cards = []

    @staticmethod
    def _parse_card_list(directory="Cards_to_add"):
        """
        Reads the first .txt file found in the given directory.
        Expected format per line (comma-separated):
            url, quality, quantity
        """
        txt_files = glob.glob(os.path.join(directory, "*.txt"))
        if not txt_files:
            raise FileNotFoundError(f"No .txt file found in '{directory}/' directory.")

        filepath = txt_files[0]
        print(f"Reading card list from: {filepath}")

        cards = []
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 3:
                    print(f"  Skipping line {line_num} (expected 3 fields): {line}")
                    continue

                url, quality, quantity = parts
                try:
                    quantity = int(quantity)
                except ValueError:
                    print(f"  Skipping line {line_num} (invalid quantity): {line}")
                    continue

                cards.append(
                    {
                        "url": url,
                        "quality": quality.upper(),
                        "quantity": quantity,
                    }
                )

        print(f"Parsed {len(cards)} card(s) from file.")
        return cards

    def load_from_file(self, directory="Cards_to_add"):
        """Parse card list from a .txt file and store in self.cards."""
        self.cards = self._parse_card_list(directory)
        return self

    def load_from_list(self, card_list):
        """Load cards directly from a list of dicts (for programmatic use)."""
        self.cards = card_list
        return self

    def preview(self):
        """Print a preview of the loaded cards."""
        if not self.cards:
            print("No cards loaded.")
            return self

        print("Card list preview:")
        for c in self.cards:
            print(f"  {c['url']}  |  {c['quality']}  |  x{c['quantity']}")
        return self

    def obtain_product_ids(self):
        urls = [card["url"] for card in self.cards]
        response = requests.post(f"{self.API_SERVER}/url_cards", json=urls)
        id_map = response.json()

        for card in self.cards:
            card["product_id"] = id_map.get(card["url"])
            if not card["product_id"]:
                print("Failed to fetch one card id from the list")
            else:
                print("id added")

        return self

    def add_all(self):
        """
        Add all cards (that have a product_id) to the cart via
        XMLHttpRequest inside the browser.

        Returns a dict with success/fail/total counts.
        """
        print("Adding cards to cart...")

        success_count = 0
        fail_count = 0

        for i, card in enumerate(self.cards):
            if not card.get("product_id"):
                print(
                    f"  [{i + 1}/{len(self.cards)}] SKIP (no product_id): {card['url']}"
                )
                fail_count += 1
                continue

            print(
                f"  [{i + 1}/{len(self.cards)}] "
                f"id={card['product_id']}, style={card['quality']}, qty={card['quantity']}"
            )

            if self._add_single(card):
                success_count += 1
            else:
                fail_count += 1

            time.sleep(self.delay)

        total = len(self.cards)
        results = {"success": success_count, "failed": fail_count, "total": total}
        print(f"Done: {success_count}/{total} added, {fail_count} failed.")
        return results

    def _extract_single_id(self, url):
        """Navigate to a card page and pull the product_id from the form."""
        self.driver.get(url)

        if self.driver.is_element_present(self.PRODUCT_ID_SELECTOR, wait=10):
            product_id = self.driver.run_js(
                f"return document.querySelector('{self.PRODUCT_ID_SELECTOR}').value"
            )
            return product_id
        else:
            print(f"    Product ID not found for {url}")
            return None

    def _add_single(self, card):
        """Add one card to cart via synchronous XHR in the browser."""
        payload = {
            "product_id": card["product_id"],
            "style": card["quality"],
            "quantity": card["quantity"],
        }

        js_code = """
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "%s", false);
        xhr.setRequestHeader("accept", "application/json;charset=UTF-8");
        xhr.setRequestHeader("content-type", "application/json;charset=UTF-8");
        xhr.setRequestHeader("x-requested-with", "XMLHttpRequest");
        xhr.send(JSON.stringify(%s));
        return JSON.stringify({status: xhr.status, body: xhr.responseText});
        """ % (self.API_URL, json.dumps(payload))

        try:
            result_raw = self.driver.run_js(js_code)
            result = json.loads(result_raw)
            status = result.get("status")
            body = result.get("body", "")

            if status == 200:
                print(f"    Added (HTTP {status})")
                return True
            else:
                print(f"    Failed (HTTP {status}): {body[:200]}")
                return False
        except Exception as e:
            print(f"    JS error: {e}")
            return False
