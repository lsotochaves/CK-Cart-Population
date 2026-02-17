import getpass
import time


# ──────────────────────────────────────────────
# 1. SECURE CREDENTIALS INPUT
# ──────────────────────────────────────────────
def get_credentials(retry=False):
    if retry:
        print("\n" + "!" * 40)
        print("!!! PREVIOUS LOGIN FAILED. Please try again.")
        print("!" * 40)

    print("\n--- Secure Credentials Input ---")
    email = input("Enter Email: ")
    password = getpass.getpass("Enter Password: ")
    return email, password


# ──────────────────────────────────────────────
# 2. BROWSER LOGIN INTERACTION
# ──────────────────────────────────────────────
def perform_login_attempt(driver, email, password):
    """Types credentials into the form and submits."""
    print(">>> Filling login form...")
    try:
        if "customer_login" not in driver.current_url:
            driver.get("https://www.cardkingdom.com/customer_login")

        driver.type("input[name='email'], #email", email)
        driver.type("input[name='password'], #password", password)

        print(">>> Clicking Submit...")
        driver.click("input[type='submit'], button[type='submit']", wait=2)
        return True
    except Exception as e:
        print(f">>> Interaction Error: {e}")
        return False


# ──────────────────────────────────────────────
# 3. LOGIN FLOW (receives driver, no decorator)
# ──────────────────────────────────────────────
def login(driver):
    """
    Attempts login up to 3 times.
    Returns cookies on success, None on failure.
    The driver is passed in from main.py — no new browser is opened.
    """
    email, password = get_credentials()
    max_retries = 3

    for attempt in range(max_retries):
        print(f"\n" + "=" * 30)
        print(f">>> LOGIN ATTEMPT {attempt + 1} / {max_retries}")
        print("=" * 30)

        perform_login_attempt(driver, email, password)

        print(">>> Waiting for server response...")
        time.sleep(4)

        current_url = driver.current_url.rstrip("/")
        print(f">>> Current URL: {current_url}")

        # --- Success ---
        if current_url == "https://www.cardkingdom.com":
            print("\n>>> SUCCESS: Login valid.")
            return driver.get_cookies()

        # --- Failed ---
        elif "customer_login" in current_url:
            print("\n>>> FAILURE: Credentials rejected.")
            if attempt < max_retries - 1:
                email, password = get_credentials(retry=True)
            else:
                print("!!! Max retries reached.")

        # --- Captcha ---
        elif "challenge" in current_url or "attention" in current_url:
            print("\n>>> CAPTCHA: Cloudflare detected.")
            input(">>> Solve the CAPTCHA in the browser and press ENTER here...")
            if driver.current_url.rstrip("/") == "https://www.cardkingdom.com":
                return driver.get_cookies()

        # --- Unknown ---
        else:
            print(f"\n>>> UNKNOWN: Landed on {current_url}")
            if driver.is_element_present(".fa-user", wait=1):
                print(">>> Found user icon. Assuming success.")
                return driver.get_cookies()

    return None
