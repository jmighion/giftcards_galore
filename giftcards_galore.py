"""Auto buy Amazon Giftcards"""

import os
import random
import re
import sys
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load env variables from ".env" file in the same folder
load_dotenv()

# User-defined variables
# Your Amazon username (email)
AMAZON_USERNAME = os.getenv("AMAZON_USERNAME")

# Your Amazon password
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")

# 0-indexed array of your Amazon payment methods
# Refer to https://www.amazon.com/gp/wallet
CARDS = [0, 1, 2, 3]

# Your credit card numbers, corresponding to the index of each card in the CARDS array
CARD_NUMBERS = [os.getenv("CC0"), os.getenv("CC1"), os.getenv("CC2"), os.getenv("CC3")]

# Iterations array, corresponds to the number of purchases for each card
ITERATIONS = [0, 0, 12, 12]

# Amount to be loaded onto each gift card
GIFT_CARD_AMOUNT = os.getenv("GIFT_CARD_AMOUNT")

# Automatically get and cache the webdriver for Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


class AuthenticationError(Exception):
    pass


# Function to buy the giftcards
def giftcard_buyer():

    wait = WebDriverWait(driver, 10)
    print(AMAZON_USERNAME)
    driver.get("https://www.amazon.com/asv/reload/")
    try:
        wait.until(expected_conditions.title_contains("Gift Card Balance Reload"))
        print("Select one time reload")
        # Note the .// for finding child button in the xpath
        driver.find_element(By.ID, "reload_type_0").click()
        time.sleep(3)
        driver.find_element(By.ID, "gc-ui-form-custom-amount").send_keys(str(GIFT_CARD_AMOUNT))
        time.sleep(3)
        inputs = driver.find_elements(By.NAME, "submit.gc-buy-now")
        for x in inputs:
            if x.is_displayed():
                x.click()
        print("Sign in")
        # Added wait times between most page loads because the driver was going too fast
        # The wait.until() did not seem to work. Could probably change the wait.until to check for the next element.
        time.sleep(4)
        wait.until(expected_conditions.title_contains("Amazon Sign-In"))
        # time.sleep(4)
        driver.find_element(By.ID, "ap_email").send_keys(AMAZON_USERNAME)
    except:
        print("Error?")
        print(sys.exc_info()[0])
        pass

    driver.find_element(By.ID, "continue").click()
    time.sleep(3)
    driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
    driver.find_element(By.ID, "signInSubmit").click()
    time.sleep(12)
    # Not sure how to handle 2FA. Manually inputting during the previous sleep, but the button presses and the rest could be automated.
    # Now there's a page asking for phone number. That could be automatically skipped as well.
    try:
        driver.find_element(By.XPATH, "//h1[contains(.,'Authentication Required')]")
        raise AuthenticationError("You need to manually confirm your login")
    except NoSuchElementException:
        print("Error?")
        print(sys.exc_info()[0])
        pass

    i = 0
    for card in CARDS:
        print(f"card: {card}")
        for iteration in range(ITERATIONS[i]):

            print(f"iteration: {iteration}")

            # Submit new gift card amount after the first time, but also for the first iteration of each subsequent card
            if iteration != 0 or (card > 0 and iteration == 0 and ITERATIONS[card - 1] != 0):
                print("New iteration gift card amount setup")
                wait.until(expected_conditions.title_contains("Gift Card Balance Reload"))
                print("Select one time reload")
                # Note the .// for finding child button in the xpath. .find_element(By.XPATH, ".//button")?
                # driver.find_element(By.ID, "reload_type_0").click()
                driver.find_element(By.XPATH, "//input[@aria-labelledby='reload_type_0-announce']").click()
                time.sleep(3)
                print("Input gift card amount")
                driver.find_element(By.ID, "gc-ui-form-custom-amount").send_keys(str(GIFT_CARD_AMOUNT))
                time.sleep(3)
                try:
                    inputs = driver.find_elements(By.NAME, "submit.gc-buy-now")
                    for x in inputs:
                        if x.is_displayed():
                            x.click()
                except:
                    print("Error?")
                    print(sys.exc_info()[0])
                    try:
                        inputs = driver.find_elements(By.NAME, "submit.gc-buy-now")
                        for x in inputs:
                            if x.is_displayed():
                                x.click()
                    except:
                        print("Error?")
                        print(sys.exc_info()[0])

                # One time I was prompted for the password and token again. Haven't ran into it again yet, so this can probably be deleted.
                try:
                    driver.find_element(By.ID, "ap_password")
                    driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
                    driver.find_element(By.ID, "signInSubmit").click()
                    time.sleep(12)
                except NoSuchElementException:
                    print("No need to log in again, right?")
                    print(sys.exc_info()[0])
                    pass

            time.sleep(2)
            print("Click change card link")
            try:
                wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//a[contains(@href,'chg_payselect')]")))
                driver.find_element(By.XPATH, "//a[contains(@href,'chg_payselect')]").click()
                time.sleep(3)
            except:
                print("Error?")
                print(sys.exc_info()[0])
                try:
                    driver.find_element(By.ID, "payChangeButtonId").click()
                    time.sleep(4)
                except:
                    print("Error?")
                    print(sys.exc_info()[0])
                    pass
                pass

            print("Click CC radio button")
            driver.find_elements(By.XPATH, "//input[@type='radio']")[card].click()
            time.sleep(4)

            # Searching for placeholder$='<last-4-of-card>'. Needs single quotes. Always only 1 card, so [0].
            try:
                cc_input_box = driver.find_elements(By.CSS_SELECTOR, "[placeholder$='" + CARD_NUMBERS[card][-4:] + "']")[0]
                if cc_input_box:
                    try:
                        print("Found verification input")
                        print("Sending CC number to input box")
                        cc_input_box.send_keys(CARD_NUMBERS[card])
                        time.sleep(random.randint(1, 5))

                        print("Verify card")
                        # Find Verify button by cc_input_box_id adding 1 to the trailing digits.
                        # When the page reloads the previously verified cards do not render those buttons,
                        # so the array can't be trusted to be the same each time.
                        cc_input_box_id = cc_input_box.get_attribute("id")  # pp-kFRldw-171

                        button_id = re.sub("[0-9]+$", str(int(re.match(".*?([0-9]+)$", cc_input_box_id).group(1)) + 1), cc_input_box_id)  #
                        driver.find_elements(By.XPATH, "//button[contains(@id,'" + button_id + "')]")[0].click()
                        time.sleep(random.randint(1, 5))
                    except:
                        print("Error?")
                        print(sys.exc_info()[0])
            except:
                print("No need for CC validation?")
                print(sys.exc_info()[0])
                pass

            try:
                use_this_card = driver.find_element(By.XPATH, "//input[@aria-labelledby='orderSummaryPrimaryActionBtn-announce']")
                if use_this_card:
                    print("Click use this card button")

                    use_this_card.click()
                    del use_this_card
                    time.sleep(4)
            except:
                print("Error?")
                print(sys.exc_info()[0])
                pass

            print("Click place your order button")
            driver.find_element(By.XPATH, "//input[@aria-labelledby='submitOrderButtonId-announce']").click()
            time.sleep(3)

            print("Continue loop")
            driver.get("https://www.amazon.com/asv/reload/")
            time.sleep(3)
        i += 1
    driver.quit()


try:
    giftcard_buyer()
except:
    driver.quit
