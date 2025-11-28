import os, time, logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOG_DIR = "logs"
SCREENSHOT_DIR = os.path.join(LOG_DIR, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def wait_for(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def wait_clickable(driver, locator, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def save_ss(driver, name_prefix):
    ts = int(time.time() * 1000)
    path = f"{SCREENSHOT_DIR}/{name_prefix}_{ts}.png"
    driver.save_screenshot(path)
    logging.info(f"Saved screenshot: {path}")
    return path


def safe_click(driver, locator, timeout=20):
    el = wait_clickable(driver, locator, timeout)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    el.click()
    return el


