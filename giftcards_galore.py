"""Auto buy Amazon Giftcards"""

import os
import sys
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions  # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
# Needs Python 3
# from webdriver_manager.chrome import ChromeDriverManager

# Load env variables from ".env" file in the same folder
load_dotenv()

# User-defined variables
# Your Amazon username (email)
AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')

# Your Amazon password
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')

# 0-indexed array of your Amazon payment methods
# Refer to https://www.amazon.com/gp/wallet
CARDS = [0, 1, 2, 3]

# Your credit card numbers, corresponding to the index of each card in the CARDS array
CARD_NUMBERS = [
    os.getenv('CC0'),
    os.getenv('CC1'),
    os.getenv('CC2'),
    os.getenv('CC3')]

# Iterations array, corresponds to the number of purchases for each card
ITERATIONS = [0, 0, 12, 12]

# Amount to be loaded onto each gift card
GIFT_CARD_AMOUNT = os.getenv('GIFT_CARD_AMOUNT')

# Ensure Chrome Webdriver is on System PATH
driver = webdriver.Chrome("")
# Needs Python 3
# driver = webdriver.Chrome(ChromeDriverManager().install())


class AuthenticationError(Exception):
    pass


# Function to buy the giftcards
def giftcard_buyer():

    wait = WebDriverWait(driver, 10)
    driver.get('https://www.amazon.com/asv/reload/')
    try:
        wait.until(expected_conditions.title_contains('Amazon Reload'))
        driver.find_element_by_id('gcui-asv-reload-form-custom-amount').send_keys(str(GIFT_CARD_AMOUNT))
        time.sleep(1)
        inputs = driver.find_elements_by_name('submit.gc-buy-now')
        for x in inputs:
            if x.is_displayed():
                x.click()
        print "Sign in"
        # Added wait times between most page loads because the driver was going too fast
        # The wait.until() did not seem to work. Could probably change the wait.until to check for the next element.
        time.sleep(4)
        wait.until(expected_conditions.title_contains('Amazon Sign-In'))
        time.sleep(4)
        driver.find_element_by_id('ap_email').send_keys(AMAZON_USERNAME)
    except:
        print "Error?"
        print sys.exc_info()[0]
        pass

    driver.find_element_by_id('continue').click()
    time.sleep(3)
    driver.find_element_by_id('ap_password').send_keys(AMAZON_PASSWORD)
    driver.find_element_by_id('signInSubmit').click()
    time.sleep(12)
    # Not sure how to handle 2FA. Manually inputting during the previous sleep, but the button presses and the rest
    # could be automated.
    # Now there's a page asking for phone number. That could be automatically skipped as well.
    try:
        driver.find_element_by_xpath("//h1[contains(.,'Authentication Required')]")
        raise AuthenticationError("You need to manually confirm your login")
    except NoSuchElementException:
        pass

    i = 0
    for card in CARDS:
        print "card: %r" % card
        for iteration in range(ITERATIONS[i]):

            print "iteration: %r" % (iteration)

            # Submit new gift card amount after the first time, but also for the first iteration of each subsequent card
            if iteration != 0 or (card > 0 and iteration == 0 and ITERATIONS[card - 1] != 0):
                print "New iteration gift card amount setup"
                wait.until(expected_conditions.title_contains('Amazon Reload'))
                driver.find_element_by_id('gcui-asv-reload-form-custom-amount').send_keys(str(GIFT_CARD_AMOUNT))
                time.sleep(1)
                inputs = driver.find_elements_by_name('submit.gc-buy-now')
                for x in inputs:
                    if x.is_displayed():
                        x.click()

                # One time I was prompted for the password and token again. Haven't ran into it again yet, so this can probably be deleted.
                try:
                    driver.find_element_by_id('ap_password')
                    driver.find_element_by_id('ap_password').send_keys(AMAZON_PASSWORD)
                    driver.find_element_by_id('signInSubmit').click()
                    time.sleep(12)
                except NoSuchElementException:
                    pass

            print "Click change card link"
            try:
                driver.find_element_by_id('payChangeButtonId').click()
                time.sleep(4)
            except NoSuchElementException:
                pass

            print "Click CC radio button"
            driver.find_elements_by_xpath("//input[@type='radio']")[card].click()
            time.sleep(4)

            print "Click use this card button"
            driver.find_element_by_xpath("//input[@aria-labelledby='orderSummaryPrimaryActionBtn-announce']").click()
            time.sleep(4)

            print "Click place your order button"
            driver.find_element_by_xpath("//input[@aria-labelledby='submitOrderButtonId-announce']").click()
            time.sleep(4)

            print "Continue loop"
            driver.get('https://www.amazon.com/asv/reload/')
            time.sleep(4)
        i += 1
    driver.quit()


try:
    giftcard_buyer()
except:
    driver.quit
