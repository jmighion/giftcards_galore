# Giftcards Galore!
Python script to auto-buy Amazon giftcards

Based off of: </br>
https://github.com/ageoldpun/amazon_gifts

http://pastebin.com/UW6eC3rn

https://github.com/justinjohnso/giftcards_galore

https://github.com/AFTERWAKE/giftcards_galore

---

### Dependencies:
* Selenium
* Chrome Webdriver
  ([download](https://sites.google.com/a/chromium.org/chromedriver/downloads))
* python-dotenv

---

### Installation/Setup:
Install Selenium using `pip install selenium`</br>
Download the Chrome Webdriver and ensure it can be found on your system [PATH](http://en.wikipedia.org/wiki/PATH_%28variable%29)</br>
Install python-dotenv using `pip install python-dotenv`

#### Variables:
These are environment variables:

* `AMAZON_USERNAME`
* `AMAZON_PASSWORD`
* `CARD_NUMBERS`
* `GIFT_CARD_AMOUNT`

You can define using whatever method works
best for you (`export` in `.bash_profile`, define in Python console, or just
define in the script), or you can create a .env file in the following format:
```
# .env file
AMAZON_USERNAME=user@domain.com
AMAZON_PASSWORD=password
CC0=1234567890123456
CC1=7890123456789012
GIFT_CARD_AMOUNT=1.00
```

You need your card numbers because Amazon will ask to confirm each one for the
first iteration of a given card.

These are arrays that correspond with the (0-indexed) list of cards on your
[Amazon Wallet](https://www.amazon.com/gp/wallet) page:

* `CARDS`
* `ITERATIONS`

---

### Usage:

In terminal, run `python giftcards_galore.py`. Selenium will open a new Chrome
window and start the script.

# Warning
This is incomplete and still needs cleanup. If it works, this will charge your cards.

I intend to fix / clean up :
* PEP 8
* Secure passwords
* Comments
* Imports
* Exceptions
* CARDS and CARD_NUMBERS array functionality
* Update to python 3
* Randomize timings between every action

Use at your own risk.
