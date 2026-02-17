import login
from botasaurus.browser import browser, Driver
import time


def extract_product_id(driver: Driver, url: str):
    """
    Navigates to a card page and extracts the product_id.
    """
    print(f">>> Loading: {url}")
    driver.get(url)

    # Wait for JavaScript to generate the product_id
    selector = 'form.addToCartForm input[name="product_id[0]"]'

    if driver.is_element_present(selector, wait=10):
        product_id = driver.run_js(f"return document.querySelector('{selector}').value")
        print(f">>> ✓ Product ID: {product_id}")
        return product_id
    else:
        print(">>> ✗ Product ID not found")
        return None


@browser(block_images=False, window_size=None)
def get_product_ids(driver: Driver, data=None):
    """
    Login once, then extract product IDs from multiple cards.
    """
    # STEP 1: Login
    print("\n" + "=" * 60)
    print("LOGGING IN...")
    print("=" * 60)

    email, password = login.get_credentials()
    max_retries = 3
    cookies = None

    for attempt in range(max_retries):
        print(f"\n>>> Attempt {attempt + 1}/{max_retries}")
        login.perform_login_attempt(driver, email, password)
        time.sleep(4)

        if driver.current_url.rstrip("/") == "https://www.cardkingdom.com":
            print(">>> ✓ Logged in!")
            cookies = driver.get_cookies()
            break
        elif "customer_login" in driver.current_url:
            if attempt < max_retries - 1:
                email, password = login.get_credentials(retry=True)

    if not cookies:
        print("!!! Login failed")
        return None

    # STEP 2: Extract product IDs from card pages
    print("\n" + "=" * 60)
    print("EXTRACTING PRODUCT IDs...")
    print("=" * 60)

    # List of cards you want to process
    cards = [
        "https://www.cardkingdom.com/mtg/ice-age/brainstorm",
        "https://www.cardkingdom.com/mtg/alpha/black-lotus",
        "https://www.cardkingdom.com/mtg/dominaria/llanowar-elves",
        # Add more URLs here...
    ]

    results = {}

    for url in cards:
        card_name = url.split("/")[-1]  # Extract card name from URL
        product_id = extract_product_id(driver, url)

        if product_id:
            results[card_name] = product_id

        time.sleep(1)  # Be polite to the server

    # STEP 3: Display results
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    for card, pid in results.items():
        print(f"{card}: {pid}")

    return results


if __name__ == "__main__":
    product_ids = get_product_ids()

    if product_ids:
        print(f"\n✓ Extracted {len(product_ids)} product IDs!")
