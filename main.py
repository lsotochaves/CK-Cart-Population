from botasaurus.browser import browser, Driver
from login import LoginManager
from cart import CartManager


@browser(
    block_images=False,
    window_size=None,
)
def run(driver: Driver, data=None):

    # ── Step 1: Login ──
    print("=" * 50)
    print(">>> STEP 1: LOGIN")
    print("=" * 50)

    auth = LoginManager(driver)
    if not auth.login():
        print("\n!!! Login failed. Exiting.")
        return

    print(f">>> Session captured with {len(auth.cookies)} cookies.\n")

    # ── Step 2: Cart ──
    print("=" * 50)
    print(">>> STEP 2: CART")
    print("=" * 50)

    cookies = {c['name']: c['value'] for c in auth.cookies}
    cart = CartManager(cookies)
    cart.load_from_file("Cards_to_add").preview().extract_product_ids().add_all().summary()

    cart.finish_execution()
    print("\n" + "*" * 50)
    print(">>> ALL DONE")
    print("*" * 50)

    input("\n>>> Press ENTER to close the browser...")


if __name__ == "__main__":
    run()