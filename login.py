import getpass
import time


class LoginManager:
    """
    Handles authentication with Card Kingdom.

    Usage:
        login_mgr = LoginManager(driver)
        if login_mgr.login():
            cookies = login_mgr.cookies
    """

    LOGIN_URL = "https://www.cardkingdom.com/customer_login"
    HOME_URL = "https://www.cardkingdom.com"

    def __init__(self, driver, max_retries=3):
        self.driver = driver
        self.max_retries = max_retries
        self.cookies = None
        self.is_logged_in = False

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────
    def login(self):
        """
        Main login flow. Prompts for credentials, retries on failure.
        Returns True on success, False on failure.
        Cookies are stored in self.cookies.
        """
        email, password = self._get_credentials()

        for attempt in range(self.max_retries):
            print(f"\n" + "=" * 30)
            print(f">>> LOGIN ATTEMPT {attempt + 1} / {self.max_retries}")
            print("=" * 30)

            self._submit_form(email, password)

            print(">>> Waiting for server response...")
            time.sleep(4)

            result = self._check_result()

            if result == "success":
                self.cookies = self.driver.get_cookies()
                self.is_logged_in = True
                print("\n>>> SUCCESS: Login valid.")
                return True

            elif result == "failed":
                print("\n>>> FAILURE: Credentials rejected.")
                if attempt < self.max_retries - 1:
                    email, password = self._get_credentials(retry=True)
                else:
                    print("!!! Max retries reached.")

            elif result == "captcha":
                print("\n>>> CAPTCHA: Cloudflare detected.")
                input(">>> Solve the CAPTCHA in the browser and press ENTER here...")
                if self._is_home():
                    self.cookies = self.driver.get_cookies()
                    self.is_logged_in = True
                    return True

            elif result == "unknown":
                current_url = self.driver.current_url.rstrip("/")
                print(f"\n>>> UNKNOWN: Landed on {current_url}")
                if self.driver.is_element_present(".fa-user", wait=1):
                    print(">>> Found user icon. Assuming success.")
                    self.cookies = self.driver.get_cookies()
                    self.is_logged_in = True
                    return True

        return False

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────
    def _get_credentials(self, retry=False):
        if retry:
            print("\n" + "!" * 40)
            print("!!! PREVIOUS LOGIN FAILED. Please try again.")
            print("!" * 40)

        print("\n--- Secure Credentials Input ---")
        email = input("Enter Email: ")
        password = getpass.getpass("Enter Password: ")
        return email, password

    def _submit_form(self, email, password):
        print(">>> Filling login form...")
        try:
            if "customer_login" not in self.driver.current_url:
                self.driver.get(self.LOGIN_URL)

            self.driver.type("input[name='email'], #email", email)
            self.driver.type("input[name='password'], #password", password)

            print(">>> Clicking Submit...")
            self.driver.click("input[type='submit'], button[type='submit']", wait=2)
        except Exception as e:
            print(f">>> Interaction Error: {e}")

    def _check_result(self):
        """Returns: 'success', 'failed', 'captcha', or 'unknown'."""
        current_url = self.driver.current_url.rstrip("/")
        print(f">>> Current URL: {current_url}")

        if self._is_home():
            return "success"
        elif "customer_login" in current_url:
            return "failed"
        elif "challenge" in current_url or "attention" in current_url:
            return "captcha"
        else:
            return "unknown"

    def _is_home(self):
        return self.driver.current_url.rstrip("/") == self.HOME_URL
