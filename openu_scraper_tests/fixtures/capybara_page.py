import capybara
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from openu_scraper.constants import OPENU_HOME

LINUX_GOOGLE_CHROME = '/usr/bin/google-chrome'
OSX_GOOGLE_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# Taken from https://stackoverflow.com/a/26605963/1046490.
try:
    import pydevd

    DEBUGGING = True
except ImportError:
    DEBUGGING = False


@capybara.register_driver("selenium_chrome")
def init_selenium_chrome_driver(app):
    from capybara.selenium.driver import Driver

    # When clicking on events, there is a race between the test and JS's registering of the event the handler.
    # In that case, We get a generic WebDriverException which doesn't trigger a retry by capybara.
    # We inherit from the driver and add this exception to the list of errors in which methods are rerun.
    class DriverWhichRetriesOnMoreException(Driver):
        @property
        def invalid_element_errors(self):
            return super().invalid_element_errors + (WebDriverException,)

    options = webdriver.ChromeOptions()

    options.binary_location = OSX_GOOGLE_CHROME if sys.platform == "darwin" else LINUX_GOOGLE_CHROME

    # Comment out to get a Chrome window (useful for debugging).
    # if not DEBUGGING:
    #     options.add_argument('headless')

    options.add_argument('allow-insecure-localhost')

    # If we run as `root`, chrome will complain and refuse to start unless 'no-sandbox' is passed.
    options.add_argument('no-sandbox')

    # set the window size
    options.add_argument('window-size=1600x1400')

    return DriverWhichRetriesOnMoreException(app, browser="chrome", chrome_options=options)


capybara.app_host = OPENU_HOME
capybara.default_driver = "selenium_chrome"
capybara.wait_on_first_by_default = True

if DEBUGGING:
    # When debugging, fail faster for quicker responses when evaluating stuff.
    capybara.default_max_wait_time = 3
else:
    capybara.default_max_wait_time = 15
