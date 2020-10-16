"""Auto buy Amazon Giftcards"""

import os
import sys
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions # available since 2.26.0
from selenium.common.exceptions import *

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
driver = webdriver.Chrome()


class AuthenticationError(Exception):
    pass


# Function to buy the giftcards
def giftcard_buyer():

    wait = WebDriverWait(driver, 10)
    driver.get('https://www.amazon.com/asv/reload/')
    try:
        wait.until(expected_conditions.title_is('Reload Your Balance'))
        driver.find_element_by_id('form-submit-button').click()
        print "Sign in"
        # Added wait times between most page loads because the driver was going too fast
        # The wait.until() did not seem to work. Could probably change the wait.until to check for the next element.
        time.sleep(4)
        wait.until(expected_conditions.title_is('Amazon Sign-In'))
        time.sleep(4)
        driver.find_element_by_id('ap_email').send_keys(AMAZON_USERNAME)
    except:
        print "Error?"
        print sys.exc_info()[0]
        pass

    driver.find_element_by_id('continue').click()
    time.sleep(2)
    driver.find_element_by_id('ap_password').send_keys(AMAZON_PASSWORD)
    driver.find_element_by_id('signInSubmit').click()
    time.sleep(8)
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
            if driver.title != 'Reload Your Balance':
                driver.get('https://www.amazon.com/asv/reload/')
            wait.until(expected_conditions.title_is('Reload Your Balance'))
            time.sleep(2)
            driver.find_element_by_id('asv-manual-reload-amount').send_keys(str(GIFT_CARD_AMOUNT))
            time.sleep(1)
            print "Click pmts-credit-card-row"
            driver.find_elements_by_class_name('pmts-credit-card-row')[card].click()
            if iteration == 0:
                try:
                    print "Finding form-submit-button"
                    driver.find_element_by_id('form-submit-button').click()
                    time.sleep(random.randint(1, 5))
                    print "Finding CC %r" % (CARD_NUMBERS[card])
                    # Searching for placeholder$='<last-4-of-card>'. Needs single quotes. Always only 1 card, so [0].
                    cc_input_box = driver.find_elements_by_css_selector("[placeholder$='" + CARD_NUMBERS[card][-4:] + "']")[0]
                    time.sleep(1)
                    print "Sending CC number to input box"
                    cc_input_box.send_keys(CARD_NUMBERS[card])
                    time.sleep(random.randint(1, 5))
                    print "Verify card"
                    # Find Verify button by partial id because when the page reloads the previously verified cards do
                    # not render those buttons, so the array is wrong.
                    driver.find_elements_by_xpath("//button[contains(@id,'" + cc_input_box.get_attribute("id")[:-1] + "')]")[0].click()
                    time.sleep(random.randint(1, 5))
                except NoSuchElementException:
                    print "Card did not confirm"
                    print sys.exc_info()[0]
                    pass
                except:
                    print "Error?"
                    print sys.exc_info()[0]
                    pass
            else:
                time.sleep(random.randint(5, 10))

            print "Submit"
            driver.find_element_by_id('form-submit-button').click()
            time.sleep(random.randint(1, 3))
            try:
                driver.find_element_by_xpath("//span[contains(.,'this message again')]").click()
                time.sleep(random.randint(1, 3))
                driver.find_element_by_id('asv-reminder-action-primary').click()
                time.sleep(random.randint(1, 3))
            except NoSuchElementException:
                pass
            driver.get('https://www.amazon.com/asv/reload/')
            time.sleep(2)
        i += 1
    driver.quit()


try:
    giftcard_buyer()
except:
    driver.quit
