from .extensions import celery
from .extensions import db
from .models import User, Reservation, RepeatingReservation
# from .boilerKey import generate_password, generate_auth_cookies
from datetime import datetime, timedelta, date, time
from bs4 import BeautifulSoup
from celery import group
from celery.exceptions import SoftTimeLimitExceeded

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests

url_list = [
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=52be22f5-728b-4ef7-8602-972011d8739e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=646d15bd-6fa9-4558-aac8-e70d1a0847c5&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=b5c44d87-bead-49d7-b353-42eb5e595022&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=89d70d51-5760-495d-ba8e-d47fa1627cb4&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=65e7f3fa-4c6b-4fb6-b5bb-b5eea54ea46e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=852d33d3-7615-4b2d-94e7-618d5e3feb1e&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed",
    "https://recwell.purdue.edu/Program/GetProgramDetails?courseId=1e7d1515-87e5-405d-b35a-96cf18c1cd1a&semesterId=6830b6fc-7a4f-4340-ab62-92bf071dffed"
]

@celery.task
def get_reservation(res_id, curr_user_id):
    # perform automation to get reservation
    print("Getting reservation {} for {}...".format(res_id, curr_user_id))

    curr_user = User.query.get(curr_user_id)
    res = Reservation.query.get(res_id)

    username = curr_user.username
    password = curr_user.get_login_pass()
    db.session.commit()

    # "%-m/%d/%Y %-I:%M:%S %p"

    weekday = res.start_time.weekday()
    start_time = res.start_time.strftime("%-m/%-d/%Y %-I:%M:%S %p")
    end_time = res.end_time.strftime("%-m/%-d/%Y %-I:%M:%S %p")

    opts = Options()
    opts.headless = True
    # assert opts.headless  # Operating in headless mode

    driver = webdriver.Firefox(options=opts)

    try:
        driver.get(url_list[weekday])
        # driver.execute_script("submitExternalLoginForm('Shibboleth')")
        login = driver.find_element_by_id("loginLink")
        login.click()

        boiler_key_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-soundcloud"))
        )
        boiler_key_login.click()

        username_field = driver.find_element_by_id("username")
        password_field = driver.find_element_by_id("password")
        submit_button = driver.find_element_by_name("submit")

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

        WebDriverWait(driver, 10).until(
            EC.title_is("Program Details - Purdue RecWell")
        )

        register = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ".//button[contains(@onclick, 'registerInInstance') and contains(@onclick, '{}') and contains(@onclick, '{}')]".format(start_time, end_time)))
        )
        register.click()

        # checkout = driver.find_element_by_id("checkoutButton")
        # checkout.click()
        driver.execute_script("document.getElementById('checkoutButton').click();")

        checkout_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ".//button[contains(@onclick, 'Submit()')]"))
        )
        checkout_2.click()

        success = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        # check whether pass or fail, then return t/f
        res.status = 1
        db.session.commit()
    except Exception as e:
        print("Exception: {}".format(e))
        res.status = 2
        db.session.commit()
    finally:
        print("Done")
        driver.quit()

@celery.task
def cancel_reservation(res_id, curr_user_id):
    # perform automation to get reservation
    print("Canceling reservation {} for {}...".format(res_id, curr_user_id))

    curr_user = User.query.get(curr_user_id)
    res = Reservation.query.get(res_id)

    username = curr_user.username
    password = curr_user.get_login_pass()
    db.session.commit()

    # "%-m/%d/%Y %-I:%M:%S %p"

    weekday = res.start_time.weekday()
    # Wed, Aug 19 2020 3:40 PM to 5:00 PM

    time_str = "{} to {}".format(res.start_time.strftime("%a, %b %-d %Y %-I:%M %p"), res.end_time.strftime("%-I:%M %p"))
    # print(time_str)
    # start_time = res.start_time.strftime("%-m/%d/%Y %-I:%M:%S %p")
    # end_time = res.end_time.strftime("%-m/%d/%Y %-I:%M:%S %p")

    opts = Options()
    opts.headless = True
    # assert opts.headless  # Operating in headless mode

    driver = webdriver.Firefox(options=opts)

    try:
        driver.get("https://recwell.purdue.edu/MemberDetails#Reg")
        # driver.execute_script("submitExternalLoginForm('Shibboleth')")
        # login = driver.find_element_by_id("loginLink")
        # login.click()

        boiler_key_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-soundcloud"))
        )
        boiler_key_login.click()

        username_field = driver.find_element_by_id("username")
        password_field = driver.find_element_by_id("password")
        submit_button = driver.find_element_by_name("submit")

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

        WebDriverWait(driver, 10).until(
            EC.title_is("View Account - Purdue RecWell")
        )

        # programs_tab = driver.find_element_by_partial_link_text("Programs")
        # programs_tab.click()
        driver.execute_script("ChangeTab('#Reg')")

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "grdRegistrationInfo"))
        )

        # dropdown = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//tbody/tr[td/text() = '{}']/td/div[@class='dropdown']/button/@id".format(time_str)))
        # )

        dropdown = driver.find_element_by_xpath("//tbody/tr[td/text() = '{}']/td/div[@class='dropdown']/button".format(time_str))
        driver.execute_script("confirmCancellation('{}')".format(dropdown.get_attribute("id").split('-', 1)[1]))
        # driver.execute_script("document.getElementById('{}').click();".format(dropdown.get_attribute("id")))

        confirm = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CancelRegBtn"))
        )
        confirm.click()

        cancelled = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tbody/tr[td/text() = '{}']/td/div/span[text() = 'Cancelled']".format(time_str)))
        )
        res.status = 3
        db.session.commit()
    except Exception:
        res.status = 2
        db.session.commit()
    finally:
        print("Done")
        driver.quit()
