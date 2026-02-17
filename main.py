from botasaurus.browser import browser, Driver
from login import login
from cart import process_cart


# ──────────────────────────────────────────────
# SINGLE BROWSER SESSION — ALL STEPS RUN HERE
# ──────────────────────────────────────────────
@browser(
    block_images=False,
    window_size=None,
)
def run(driver: Driver, data=None):
    """
    Orchestrator — one browser session for everything:
    1. Login
    2. Process cart (extract IDs + add via API)
    3. (Future steps go here)
    """

    # ── Step 1: Login ──
    print("=" * 50)
    print(">>> STEP 1: LOGIN")
    print("=" * 50)

    cookies = login(driver)
    if not cookies:
        print("\n!!! Login failed. Exiting.")
        return

    print(f">>> Session captured with {len(cookies)} cookies.\n")

    # ── Step 2: Cart ──
    print("=" * 50)
    print(">>> STEP 2: CART")
    print("=" * 50)

    process_cart(driver, cookies)

    # ── Step 3: Future steps ──
    # e.g. process_wishlist(driver, cookies)
    # e.g. process_buylist(driver, cookies)

    print("\n" + "*" * 50)
    print(">>> ALL DONE")
    print("*" * 50)

    input("\n>>> Press ENTER to close the browser...")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    run()
