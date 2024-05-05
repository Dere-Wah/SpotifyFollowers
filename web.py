import re
import time
from urllib.parse import unquote

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumbase import Driver

from utils import extract_access_token

logs_raw = []


def create_driver(proxy, sandbox: bool = False, headless: bool = False):
    driver = Driver(uc=True, uc_cdp=True, disable_ws=True)
    driver.add_cdp_listener("*", lambda data: logs_raw.append(data))
    driver.get("https://spotify.com/accounts")
    return driver


def spotify_login(driver: Driver, mail: str, password: str):
    print("Logging in to spotify...")
    driver.get("https://spotify.com/login")
    email_element = driver.find_element(By.ID, "login-username")
    email_element.send_keys(mail)
    password_element = driver.find_element(By.ID, "login-password")
    password_element.send_keys(password)
    password_element.send_keys(Keys.ENTER)
    time.sleep(3)


def verify_login(driver: Driver):
    print("Verifying login...")
    time.sleep(1)
    driver.get("https://spotify.com/login")
    try:
        button = driver.find_element(By.ID, "login-button")
        print("Login is not verified.")
        # if we can still see the login button, we are NOT logged in.
        return False
    except:
        print("Login is verified!")
        # if we can't see the login button, we probably are logged in.
        return True


def get_spotify_tokens(mail, password):
    print("Getting auth code via selenium...")
    driver = create_driver(None)
    time.sleep(3)

    spotify_login(driver, mail, password)
    if verify_login(driver):
        driver.get("https://spotify.com/")
        time.sleep(5)
        web_token = extract_access_token(driver.page_source)
        sha = get_sha256hash_from_spotify_search(driver)
        driver.quit()
        return web_token, sha
    else:
        driver.quit()
        raise Exception("Could not login to spotify via selenium... Are the credentials correct?")


def get_sha256hash_from_spotify_search(driver):
    follow_test_user(driver)
    url = ""
    for log in logs_raw:
        try:
            url = (log["params"]["request"]["url"])
            if ("persistedQuery" in url) and ("isFollowingUsers" in url):
                url = unquote(url)
                break
        except:
            pass
    pattern = r'"sha256Hash":"([a-f0-9]+)"'
    match = re.search(pattern, url)
    if match:
        sha256hash = match.group(1)
        return sha256hash
    else:
        print("sha256Hash not found in the URL.")
        return None


def follow_test_user(driver):
    search_url = "https://open.spotify.com/user/31goqnxgo5nrimdtmzxyhu3n3squ"
    driver.get(search_url)
    time.sleep(5)
    follow_button = None
    # Try locating the search input field by role and data-testid
    try:
        follow_button = driver.find_element(By.XPATH, "//button[@data-encore-id='buttonSecondary']")
    except:
        pass
    if follow_button is None:
        print("Follow button not found.")
        driver.quit()
        return None
    follow_button.click()
    time.sleep(5)  # Wait for suggestions to load (adjust as needed)
