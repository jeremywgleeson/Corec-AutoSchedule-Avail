import requests
import pyotp
import base64
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

def get_hotp_secret(link):
    # link will be of valid type, but code may not be valid (already used etc.)
    code = link.split("/")[-1]

    HEADERS = {"User-Agent": "okhttp/3.11.0"}

    PARAMS = {
        "app_id": "com.duosecurity.duomobile.app.DMApplication",
        "app_version": "2.3.3",
        "app_build_number": "323206",
        "full_disk_encryption": False,
        "manufacturer": "Google",
        "model": "Pixel",
        "platform": "Android",
        "jailbroken": False,
        "version": "6.0",
        "language": "EN",
        "customer_protocol": 1,
    }

    ENDPOINT = "https://api-1b9bef70.duosecurity.com/push/v2/activation/{}"

    res = requests.post(ENDPOINT.format(code), headers=HEADERS, params=PARAMS)
    # print("URL: ", res.request.url)

    if res.json().get("code") == 40403:
        return None
    if not res.json()["response"]:
        return None

    return res.json()["response"]["hotp_secret"]

def generate_password(hotp_secret, counter, pin):
    # you must add 1 to counter after every invocation of this function

    hotp = pyotp.HOTP(base64.b32encode(hotp_secret.encode()))

    hotpPassword = hotp.at(counter)

    password = "{},{}".format(pin, hotpPassword)

    return password

def check_credentials(username, password):
    opts = Options()
    opts.headless = True
    browser = webdriver.Firefox(options=opts)
    browser.get("https://www.purdue.edu/apps/account/cas/login")
    try:
        if browser.current_url.startswith("https://www.purdue.edu/apps/account/cas/login"):
            # time to log in
            # login = BoilerKey.generateLogin()

            username_field = browser.find_element_by_id("username")
            password_field = browser.find_element_by_id("password")
            submit_button = browser.find_element_by_name("submit")

            username_field.send_keys(username)
            password_field.send_keys(password)
            submit_button.click()

            try:
                registration_fail = browser.find_element_by_class_name('error')
            except NoSuchElementException:
                browser.quit()
                return True
    except Exception as e:
        """Error using browser"""
    browser.quit()
    return False
