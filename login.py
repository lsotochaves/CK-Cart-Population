from botasaurus.browser import browser, Driver
import getpass
import time


class LoginManager:
    creds = None

    def get_credentials(self):
        print("--- Secure Login ---")
        email = input("Enter Email: ")
        password = getpass.getpass("Enter Password: ")
        self.creds = (email, password)
        return self.creds


@browser(block_images=False, window_size=None)
def login_task(driver: Driver, data):
    email, password = data

    print(">>> Navigating to Login Page...")
    driver.get("https://www.cardkingdom.com/customer_login")

    # 2. Automated Login Attempt
    try:
        print(">>> Attempting to auto-fill credentials...")

        # Robust selectors based on CK's known structure
        # We look for inputs with specific names OR placeholders
        driver.type("input[name='email'], input[placeholder='Enter Email']", email)
        driver.type(
            "input[name='password'], input[placeholder='Enter Password']", password
        )

        print(">>> Clicking Submit...")
        driver.click(
            "input[type='submit'], button[type='submit'], .submit-button", wait=1
        )

    except Exception as e:
        print(f"!!! Auto-fill failed: {e}")
        print("!!! Please type manually.")

    # 3. The "Human Handshake"
    print("\n" + "=" * 50)
    print("ACTION REQUIRED: Check the browser window.")
    print("1. Solve any CAPTCHAs.")
    print("2. Ensure you are fully logged in (Look for your profile icon).")
    print("=" * 50)

    input(">>> Press ENTER here once you are logged in...")

    # 4. Steal Cookies & Test API
    print(">>> Grabbing Session Cookies...")

    # Verification: Try to hit a protected endpoint
    # 'myaccount' usually redirects if not logged in
    response = driver.requests.get("https://www.cardkingdom.com/myaccount")

    if response.url == "https://www.cardkingdom.com/myaccount":
        print("SUCCESS! API Session is valid.")
        print(f"Cookies Captured: {len(response.cookies)}")

        # PRINT THE COOKIES (For your debugging/API step)
        print("\n--- COOKIE DATA (Save this mental note for api.py) ---")
        for cookie in response.cookies:
            # We specifically look for the session ID
            if "SESS" in cookie.name or "session" in cookie.name:
                print(f"Key Cookie Found: {cookie.name}")
    else:
        print("WARNING: API Test failed (Redirected to login).")

    # Keep browser open for inspection
    print("\n>>> Browser staying open for Network Inspection...")
    print(">>> Go to Network Tab -> Filter 'cart' -> Add item -> Check Request")
    time.sleep(300)  # 5 minutes to inspect


if __name__ == "__main__":
    creds = get_credentials()
    login_task(creds)
