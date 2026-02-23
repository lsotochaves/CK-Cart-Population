import time


class LoginManager:
    """
    Handles authentication with Card Kingdom.

    Usage:
        login_mgr = LoginManager(driver)
        if login_mgr.login(email, password):
            cookies = login_mgr.cookies
    """

    LOGIN_URL = "https://www.cardkingdom.com/customer_login"
    HOME_URL = "https://www.cardkingdom.com"

    def __init__(self, driver, max_retries=3):
        self.driver = driver
        self.max_retries = max_retries
        self.cookies = None
        self.is_logged_in = False

    def login(self, email, password):
        """
        Main login flow. Receives credentials externally, retries on failure.
        Returns True on success, False on failure.
        Cookies are stored in self.cookies.
        """
        for attempt in range(self.max_retries):
            print(f"Login attempt {attempt + 1}/{self.max_retries}")

            self._submit_form(email, password)

            print("Waiting for server response...")
            time.sleep(4)

            result = self._check_result()

            if result == "success":
                self.cookies = self.driver.get_cookies()
                self.is_logged_in = True
                print("Login successful.")
                return True

            elif result == "failed":
                print("Credentials rejected.")
                if attempt >= self.max_retries - 1:
                    print("Max retries reached.")

            elif result == "captcha":
                print("Cloudflare CAPTCHA detected.")
                input("Solve the CAPTCHA in the browser and press ENTER here...")
                if self._is_home():
                    self.cookies = self.driver.get_cookies()
                    self.is_logged_in = True
                    return True

            elif result == "unknown":
                current_url = self.driver.current_url.rstrip("/")
                print(f"Unexpected URL: {current_url}")
                if self.driver.is_element_present(".fa-user", wait=1):
                    print("Found user icon — assuming success.")
                    self.cookies = self.driver.get_cookies()
                    self.is_logged_in = True
                    return True

        return False

    def _submit_form(self, email, password):
        try:
            if "customer_login" not in self.driver.current_url:
                self.driver.get(self.LOGIN_URL)

            self.driver.type("input[name='email'], #email", email)
            self.driver.type("input[name='password'], #password", password)
            self.driver.click("input[type='submit'], button[type='submit']", wait=2)
        except Exception as e:
            print(f"Interaction error: {e}")

    def _check_result(self):
        """Returns: 'success', 'failed', 'captcha', or 'unknown'."""
        current_url = self.driver.current_url.rstrip("/")

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
