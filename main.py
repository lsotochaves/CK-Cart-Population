import getpass
from botasaurus.browser import browser, Driver
from login import LoginManager
from cart import CartManager


CART_URL = "https://www.cardkingdom.com/cart"


def get_credentials():
    """Prompt the user for email and password."""
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    return email, password


@browser(
    block_images=False,
    window_size=None,
)
def run(driver: Driver, data=None):
    """
    Orchestrator — one browser session for everything.
    Each module is a self-contained manager that receives the driver.
    """

    # Step 1: Login
    email, password = get_credentials()
    auth = LoginManager(driver)
    if not auth.login(email, password):
        print("Login failed. Exiting.")
        return

    print(f"Session captured with {len(auth.cookies)} cookies.")

    # Step 2: Cart
    cart = CartManager(driver)
    cart.load_from_file("Cards_to_add").preview().extract_product_ids()
    results = cart.add_all()

    # Step 3: Finish
    driver.get(CART_URL)
    print("Done.")

    input("Press ENTER to close the browser...")


if __name__ == "__main__":
    run()
