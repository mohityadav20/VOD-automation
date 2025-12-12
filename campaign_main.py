import time
import logging

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys

import pandas as pd
import json
from pathlib import Path

import config
from selectors_example import (
    CAMPAIGN_PROJECT_FIRST_CARD,
    CAMPAIGN_TYPE_VOD_CARD,
    CAMPAIGN_NEXT_BUTTON,
    LOGIN_EMAIL_INPUT,
    LOGIN_CONTINUE_BUTTON,
    LOGIN_OTP_INPUT,
    LOGIN_OTP_SUBMIT,
    DIST_REGION_WORLD_BUTTON,
    DIST_REGION_SPECIFIC_BUTTON,
    DIST_REGION_EXCEPT_BUTTON,
    RENTAL_HD_CHECKBOX,
    RENTAL_HD_PRICE_INPUT,
    RENTAL_HD_PERCEIVED_INPUT,
    RENTAL_SD_CHECKBOX,
    RENTAL_SD_PRICE_INPUT,
    RENTAL_SD_PERCEIVED_INPUT,
    PURCHASE_HD_CHECKBOX,
    PURCHASE_HD_PRICE_INPUT,
    PURCHASE_HD_PERCEIVED_INPUT,
    PURCHASE_SD_CHECKBOX,
    PURCHASE_SD_PRICE_INPUT,
    PURCHASE_SD_PERCEIVED_INPUT,
    COUNTRY_SEARCH_INPUT,
    COUNTRY_CHECKBOX_INDIA,
    INDIA_RENTAL_HD_CHECKBOX,
    INDIA_RENTAL_HD_PRICE_INPUT,
    INDIA_RENTAL_HD_PERCEIVED_INPUT,
    INDIA_RENTAL_SD_CHECKBOX,
    INDIA_RENTAL_SD_PRICE_INPUT,
    INDIA_RENTAL_SD_PERCEIVED_INPUT,
    INDIA_PURCHASE_HD_CHECKBOX,
    INDIA_PURCHASE_HD_PRICE_INPUT,
    INDIA_PURCHASE_HD_PERCEIVED_INPUT,
    INDIA_PURCHASE_SD_CHECKBOX,
    INDIA_PURCHASE_SD_PRICE_INPUT,
    INDIA_PURCHASE_SD_PERCEIVED_INPUT,
    SPECIFIC_COUNTRIES_SEARCH_INPUT,
    EXCLUDED_COUNTRIES_SEARCH_INPUT,
    UPLOAD_MOVIE_BUTTON,
    UPLOAD_MOVIE_MODAL_SEARCH,
    UPLOAD_MOVIE_ROW_CHECKBOX,
    UPLOAD_MOVIE_CONFIRM,
    PRIMARY_AUDIO_LANGUAGE_COMBOBOX,
    SUBTITLE_LANGUAGE_COMBOBOX,
    SUBTITLE_LANGUAGE_SEARCH,
    SUBTITLE_CHOOSE_FILE,
    SUBTITLE_MODAL_SEARCH,
    SUBTITLE_MODAL_CHECKBOX,
    SUBTITLE_MODAL_CONFIRM,
    ADD_ANOTHER_SUBTITLE_BUTTON,
    ADD_BACKGROUND_ART_BUTTON,
    BACKGROUND_ART_SEARCH,
    BACKGROUND_ART_CHECKBOX,
    BACKGROUND_ART_CONFIRM,
    QUALITY_HDR_LABEL,
    QUALITY_STEREO_LABEL,
    QUALITY_1080P_LABEL,
    CREATE_CAMPAIGN_BUTTON,
    PRICING_NEXT_BUTTON,
)

from selenium.webdriver.common.by import By
from automation_utils import safe_click, save_ss, wait_for
from main import load_sheet, choose_sheet_path


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_driver():
    options = webdriver.ChromeOptions()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver


def perform_login(driver) -> bool:
    """
    Attempt automated login using configured email/OTP.
    Retries up to 3 times if login page reappears after submission.
    Returns True if successfully logged in (URL changed from login page).
    """
    if not getattr(config, "AUTO_LOGIN", False):
        logging.info("AUTO_LOGIN disabled; skipping automated login.")
        return False

    login_url = "https://filmmakers.brew.tv/filmmaker-login"
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        logging.info(f"Login attempt {attempt}/{max_attempts}...")
        try:
            email_input = wait_for(driver, LOGIN_EMAIL_INPUT, timeout=config.WAIT_TIMEOUT)
            email_input.click()
            try:
                email_input.clear()
            except Exception:
                pass
            email_input.send_keys(getattr(config, "LOGIN_EMAIL", ""))
            save_ss(driver, f"login_email_filled_attempt_{attempt}")

            safe_click(driver, LOGIN_CONTINUE_BUTTON, timeout=config.WAIT_TIMEOUT)
            logging.info("Email submitted, waiting for OTP field...")

            try:
                otp_input = wait_for(driver, LOGIN_OTP_INPUT, timeout=30)
                otp_input.click()
                try:
                    otp_input.clear()
                except Exception:
                    pass
                otp_input.send_keys(getattr(config, "LOGIN_OTP", "123456"))
                save_ss(driver, f"login_otp_filled_attempt_{attempt}")
                try:
                    safe_click(driver, LOGIN_OTP_SUBMIT, timeout=10)
                except Exception:
                    otp_input.send_keys(Keys.ENTER)
                
                time.sleep(3)
                save_ss(driver, f"login_submitted_attempt_{attempt}")
                
                # Check if URL changed away from login page
                current_url = driver.current_url
                logging.info(f"Current URL after login: {current_url}")
                
                if login_url not in current_url:
                    logging.info("✓ Login successful! URL changed away from login page.")
                    save_ss(driver, "login_successful")
                    return True
                else:
                    logging.warning(f"Login page still visible (attempt {attempt}). Retrying...")
                    save_ss(driver, f"login_failed_url_check_attempt_{attempt}")
                    time.sleep(2)
                    continue
                    
            except Exception as e:
                logging.warning(f"OTP input failed (attempt {attempt}): {e}")
                save_ss(driver, f"login_otp_failed_attempt_{attempt}")
                continue
                
        except Exception as e:
            logging.warning(f"Login attempt {attempt} failed at email step: {e}")
            save_ss(driver, f"login_email_failed_attempt_{attempt}")
            continue

    logging.error("Login failed after 3 attempts. Manual login required.")
    return False


def decide_distribution_strategy(row: pd.Series) -> str:
    """
    Decide which distribution region strategy to use based on the row's
    Avail Countries Included / Excluded columns.

    Priority:
    1. If Excluded has countries => "All Countries Except"
    2. If only Included has countries => "Specific Countries"
    3. If neither or both empty => "World Wide"

    Returns one of: 'world', 'specific', 'except'.
    """
    inc_col = getattr(config, "AVAIL_INCLUDED_COL", "").strip()
    exc_col = getattr(config, "AVAIL_EXCLUDED_COL", "").strip()

    included = row.get(inc_col, "") if inc_col else ""
    excluded = row.get(exc_col, "") if exc_col else ""

    def _clean(val) -> str:
        if pd.isna(val):
            return ""
        s = str(val).strip()
        return "" if s.lower() == "nan" else s

    included_str = _clean(included)
    excluded_str = _clean(excluded)

    has_included = bool(included_str)
    has_excluded = bool(excluded_str)

    # 1) If excluded has countries => All Countries Except (highest priority)
    if has_excluded:
        return "except"
    # 2) If only included has countries => Specific Countries
    if has_included:
        return "specific"
    # 3) Neither or both empty => World Wide
    return "world"


def select_distribution_regions(driver, row: pd.Series):
    """Click the appropriate distribution region card on the VOD campaign page."""
    strategy = decide_distribution_strategy(row)
    logging.info("Distribution strategy chosen from sheet: %s", strategy)

    if strategy == "world":
        target = DIST_REGION_WORLD_BUTTON
        label = "World Wide"
    elif strategy == "specific":
        target = DIST_REGION_SPECIFIC_BUTTON
        label = "Specific Countries"
    else:
        target = DIST_REGION_EXCEPT_BUTTON
        label = "All Countries Except"

    logging.info("Clicking distribution option: %s", label)
    safe_click(driver, target, timeout=config.WAIT_TIMEOUT)
    time.sleep(1.0)
    save_ss(driver, f"campaign_distribution_{strategy}")


def fill_worldwide_pricing(driver):
    """
    Fill pricing for World Wide distribution with hardcoded values:
    - Rental (HD & SD): Price = $4.99, Perceived = $6.99
    - Purchase (HD & SD): Price = $9.99, Perceived = $12.99
    """
    logging.info("Filling World Wide pricing options...")
    
    # Rental Price - HD: Price $4.99, Perceived $6.99
    logging.info("Setting Rental HD: Price $4.99, Perceived $6.99")
    safe_click(driver, RENTAL_HD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    rental_hd_price = driver.find_element(*RENTAL_HD_PRICE_INPUT)
    rental_hd_price.clear()
    rental_hd_price.send_keys("4.99")
    time.sleep(0.3)
    rental_hd_perceived = driver.find_element(*RENTAL_HD_PERCEIVED_INPUT)
    rental_hd_perceived.clear()
    rental_hd_perceived.send_keys("6.99")
    time.sleep(0.3)
    save_ss(driver, "pricing_rental_hd_filled")
    
    # Rental Price - SD: Price $4.99, Perceived $6.99
    logging.info("Setting Rental SD: Price $4.99, Perceived $6.99")
    safe_click(driver, RENTAL_SD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    rental_sd_price = driver.find_element(*RENTAL_SD_PRICE_INPUT)
    rental_sd_price.clear()
    rental_sd_price.send_keys("4.99")
    time.sleep(0.3)
    rental_sd_perceived = driver.find_element(*RENTAL_SD_PERCEIVED_INPUT)
    rental_sd_perceived.clear()
    rental_sd_perceived.send_keys("6.99")
    time.sleep(0.3)
    save_ss(driver, "pricing_rental_sd_filled")
    
    # Purchase Price - HD: Price $9.99, Perceived $12.99
    logging.info("Setting Purchase HD: Price $9.99, Perceived $12.99")
    safe_click(driver, PURCHASE_HD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    purchase_hd_price = driver.find_element(*PURCHASE_HD_PRICE_INPUT)
    purchase_hd_price.clear()
    purchase_hd_price.send_keys("9.99")
    time.sleep(0.3)
    purchase_hd_perceived = driver.find_element(*PURCHASE_HD_PERCEIVED_INPUT)
    purchase_hd_perceived.clear()
    purchase_hd_perceived.send_keys("12.99")
    time.sleep(0.3)
    save_ss(driver, "pricing_purchase_hd_filled")
    
    # Purchase Price - SD: Price $9.99, Perceived $12.99
    logging.info("Setting Purchase SD: Price $9.99, Perceived $12.99")
    safe_click(driver, PURCHASE_SD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    purchase_sd_price = driver.find_element(*PURCHASE_SD_PRICE_INPUT)
    purchase_sd_price.clear()
    purchase_sd_price.send_keys("9.99")
    time.sleep(0.3)
    purchase_sd_perceived = driver.find_element(*PURCHASE_SD_PERCEIVED_INPUT)
    purchase_sd_perceived.clear()
    purchase_sd_perceived.send_keys("12.99")
    time.sleep(0.3)
    save_ss(driver, "pricing_purchase_sd_filled")
    
    logging.info("All pricing options filled successfully")
    time.sleep(1.0)


def add_india_custom_pricing(driver):
    """
    Add India as a custom pricing country after filling default pricing.
    """
    logging.info("Adding India for custom pricing...")
    
    # Click on the country search input
    search_input = driver.find_element(*COUNTRY_SEARCH_INPUT)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", search_input)
    search_input.click()
    time.sleep(0.3)
    
    # Type "India" to search
    search_input.send_keys("India")
    time.sleep(1.0)  # Wait for search results
    save_ss(driver, "country_search_india")
    
    # Click the checkbox to select India
    logging.info("Selecting India checkbox...")
    safe_click(driver, COUNTRY_CHECKBOX_INDIA, timeout=config.WAIT_TIMEOUT)
    time.sleep(1.0)
    save_ss(driver, "india_selected")
    
    logging.info("India custom pricing added successfully")


def fill_india_pricing(driver):
    """
    Fill pricing for India (INR) with hardcoded values:
    - Rental (HD & SD): Price = ₹49, Perceived = ₹79
    - Purchase (HD & SD): Price = ₹149, Perceived = ₹249
    """
    logging.info("Filling India pricing options (INR)...")
    
    # Rental Price - HD: Price ₹49, Perceived ₹79
    logging.info("Setting India Rental HD: Price ₹49, Perceived ₹79")
    safe_click(driver, INDIA_RENTAL_HD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    india_rental_hd_price = driver.find_element(*INDIA_RENTAL_HD_PRICE_INPUT)
    india_rental_hd_price.clear()
    india_rental_hd_price.send_keys("49")
    time.sleep(0.3)
    india_rental_hd_perceived = driver.find_element(*INDIA_RENTAL_HD_PERCEIVED_INPUT)
    india_rental_hd_perceived.clear()
    india_rental_hd_perceived.send_keys("79")
    time.sleep(0.3)
    save_ss(driver, "india_pricing_rental_hd_filled")
    
    # Rental Price - SD: Price ₹49, Perceived ₹79
    logging.info("Setting India Rental SD: Price ₹49, Perceived ₹79")
    safe_click(driver, INDIA_RENTAL_SD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    india_rental_sd_price = driver.find_element(*INDIA_RENTAL_SD_PRICE_INPUT)
    india_rental_sd_price.clear()
    india_rental_sd_price.send_keys("49")
    time.sleep(0.3)
    india_rental_sd_perceived = driver.find_element(*INDIA_RENTAL_SD_PERCEIVED_INPUT)
    india_rental_sd_perceived.clear()
    india_rental_sd_perceived.send_keys("79")
    time.sleep(0.3)
    save_ss(driver, "india_pricing_rental_sd_filled")
    
    # Purchase Price - HD: Price ₹149, Perceived ₹249
    logging.info("Setting India Purchase HD: Price ₹149, Perceived ₹249")
    safe_click(driver, INDIA_PURCHASE_HD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    india_purchase_hd_price = driver.find_element(*INDIA_PURCHASE_HD_PRICE_INPUT)
    india_purchase_hd_price.clear()
    india_purchase_hd_price.send_keys("149")
    time.sleep(0.3)
    india_purchase_hd_perceived = driver.find_element(*INDIA_PURCHASE_HD_PERCEIVED_INPUT)
    india_purchase_hd_perceived.clear()
    india_purchase_hd_perceived.send_keys("249")
    time.sleep(0.3)
    save_ss(driver, "india_pricing_purchase_hd_filled")
    
    # Purchase Price - SD: Price ₹149, Perceived ₹249
    logging.info("Setting India Purchase SD: Price ₹149, Perceived ₹249")
    safe_click(driver, INDIA_PURCHASE_SD_CHECKBOX, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.5)
    india_purchase_sd_price = driver.find_element(*INDIA_PURCHASE_SD_PRICE_INPUT)
    india_purchase_sd_price.clear()
    india_purchase_sd_price.send_keys("149")
    time.sleep(0.3)
    india_purchase_sd_perceived = driver.find_element(*INDIA_PURCHASE_SD_PERCEIVED_INPUT)
    india_purchase_sd_perceived.clear()
    india_purchase_sd_perceived.send_keys("249")
    time.sleep(0.3)
    save_ss(driver, "india_pricing_purchase_sd_filled")
    
    logging.info("All India pricing options filled successfully")
    time.sleep(1.0)


# Language code to full name mapping for subtitles
LANGUAGE_MAP = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "cmn": "Chinese",  # Mandarin Chinese
    "yue": "Chinese",  # Cantonese Chinese
    "ar": "Arabic",
    "hi": "Hindi",
    "th": "Thai",
    "vi": "Vietnamese",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "he": "Hebrew",
    "id": "Indonesian",
    "ms": "Malay",
    "tl": "Filipino",
    "uk": "Ukrainian",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "el": "Greek",
    "is": "Icelandic",
    "mt": "Maltese",
    "cy": "Welsh",
    "ga": "Irish",
    "eu": "Basque",
    "ca": "Catalan",
    "gl": "Galician",
}

# Country code to full name mapping
COUNTRY_CODE_MAP = {
    "AF": "Afghanistan",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "CV": "Cabo Verde",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CO": "Colombia",
    "KM": "Comoros",
    "CG": "Congo",
    "CD": "Congo (Democratic Republic of the)",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "SZ": "Eswatini",
    "ET": "Ethiopia",
    "FK": "Falkland Islands",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",          # Added
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "VA": "Holy See",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (North)",
    "KR": "Korea (South)",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia",
    "MD": "Moldova",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar (formerly Burma)",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "MK": "North Macedonia",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine State",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn Islands",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RO": "Romania",
    "RU": "Russia",
    "RW": "Rwanda",
    "RE": "Réunion",
    "BL": "Saint Barthelemy",
    "SH": "Saint Helena",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syria",
    "TW": "Taiwan",
    "TJ": "Tajikistan",
    "TZ": "Tanzania",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States of America",
    "UM": "U.S. Minor Outlying Islands",   # Added
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Vietnam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",

    # Newly added missing codes
    "AX": "Aland Islands",
    "BV": "Bouvet Island",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "HM": "Heard Island and McDonald Islands",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands",
    "SJ": "Svalbard and Jan Mayen"
}


def parse_country_codes(country_string: str) -> list[str]:
    """
    Parse country codes from Excel string (e.g., "US,CA" or "US, CA").
    Returns list of country codes.
    """
    if pd.isna(country_string) or not str(country_string).strip():
        return []
    
    codes = [c.strip().upper() for c in str(country_string).split(",") if c.strip()]
    return codes


def get_country_pricing_selectors(country_name: str):
    """
    Generate XPath selectors for a specific country's pricing fields.
    Returns a dictionary of selectors for all 8 pricing inputs.
    Does not rely on currency symbol - works for any country.
    """
    return {
        'rental_hd_checkbox': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
        ),
        'rental_hd_price': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span/following-sibling::input'
        ),
        'rental_hd_perceived': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span/following-sibling::input'
        ),
        'rental_sd_checkbox': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
        ),
        'rental_sd_price': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span/following-sibling::input'
        ),
        'rental_sd_perceived': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span/following-sibling::input'
        ),
        'purchase_hd_checkbox': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
        ),
        'purchase_hd_price': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span/following-sibling::input'
        ),
        'purchase_hd_perceived': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span/following-sibling::input'
        ),
        'purchase_sd_checkbox': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
        ),
        'purchase_sd_price': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span/following-sibling::input'
        ),
        'purchase_sd_perceived': (
            By.XPATH,
            f'//span[text()="{country_name}"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span/following-sibling::input'
        ),
    }


def fill_country_pricing(driver, country_name: str, country_code: str):
    """
    Fill pricing for a specific country.
    - India (IN): INR pricing (₹49/₹79 rental, ₹149/₹249 purchase)
    - All other countries: USD pricing ($4.99/$6.99 rental, $9.99/$12.99 purchase)
    Works for any country regardless of currency symbol (USD, CAD, GBP, etc.)
    """
    if country_code == "IN":
        # India pricing in INR
        rental_price = "49"
        rental_perceived = "79"
        purchase_price = "149"
        purchase_perceived = "249"
        logging.info("Filling India pricing (INR) for %s", country_name)
    else:
        # US pricing (default for all other countries, in their local currency)
        rental_price = "4.99"
        rental_perceived = "6.99"
        purchase_price = "9.99"
        purchase_perceived = "12.99"
        logging.info("Filling US pricing (local currency) for %s", country_name)
    
    selectors = get_country_pricing_selectors(country_name)
    
    try:
        # Rental HD
        safe_click(driver, selectors['rental_hd_checkbox'], timeout=config.WAIT_TIMEOUT)
        time.sleep(0.5)
        rental_hd_price_input = driver.find_element(*selectors['rental_hd_price'])
        rental_hd_price_input.clear()
        rental_hd_price_input.send_keys(rental_price)
        time.sleep(0.3)
        rental_hd_perceived_input = driver.find_element(*selectors['rental_hd_perceived'])
        rental_hd_perceived_input.clear()
        rental_hd_perceived_input.send_keys(rental_perceived)
        time.sleep(0.3)
        
        # Rental SD
        safe_click(driver, selectors['rental_sd_checkbox'], timeout=config.WAIT_TIMEOUT)
        time.sleep(0.5)
        rental_sd_price_input = driver.find_element(*selectors['rental_sd_price'])
        rental_sd_price_input.clear()
        rental_sd_price_input.send_keys(rental_price)
        time.sleep(0.3)
        rental_sd_perceived_input = driver.find_element(*selectors['rental_sd_perceived'])
        rental_sd_perceived_input.clear()
        rental_sd_perceived_input.send_keys(rental_perceived)
        time.sleep(0.3)
        
        # Purchase HD
        safe_click(driver, selectors['purchase_hd_checkbox'], timeout=config.WAIT_TIMEOUT)
        time.sleep(0.5)
        purchase_hd_price_input = driver.find_element(*selectors['purchase_hd_price'])
        purchase_hd_price_input.clear()
        purchase_hd_price_input.send_keys(purchase_price)
        time.sleep(0.3)
        purchase_hd_perceived_input = driver.find_element(*selectors['purchase_hd_perceived'])
        purchase_hd_perceived_input.clear()
        purchase_hd_perceived_input.send_keys(purchase_perceived)
        time.sleep(0.3)
        
        # Purchase SD
        safe_click(driver, selectors['purchase_sd_checkbox'], timeout=config.WAIT_TIMEOUT)
        time.sleep(0.5)
        purchase_sd_price_input = driver.find_element(*selectors['purchase_sd_price'])
        purchase_sd_price_input.clear()
        purchase_sd_price_input.send_keys(purchase_price)
        time.sleep(0.3)
        purchase_sd_perceived_input = driver.find_element(*selectors['purchase_sd_perceived'])
        purchase_sd_perceived_input.clear()
        purchase_sd_perceived_input.send_keys(purchase_perceived)
        time.sleep(0.3)
        
        save_ss(driver, f"pricing_filled_{country_code}")
        logging.info("Pricing filled successfully for %s (%s)", country_name, country_code)
    except Exception as e:
        logging.error("Failed to fill pricing for %s (%s): %s", country_name, country_code, e)
        save_ss(driver, f"pricing_failed_{country_code}")


def select_specific_countries(driver, row: pd.Series):
    """
    Select specific countries from the "Avail Countries Included" column.
    Maps country codes (US, CA, etc.) to full names and selects them,
    then fills appropriate pricing for each country.
    """
    inc_col = getattr(config, "AVAIL_INCLUDED_COL", "").strip()
    if not inc_col:
        logging.warning("AVAIL_INCLUDED_COL not configured")
        return
    
    included_value = row.get(inc_col, "")
    country_codes = parse_country_codes(included_value)
    
    if not country_codes:
        logging.warning("No country codes found in '%s' column", inc_col)
        return
    
    logging.info("Selecting specific countries: %s", country_codes)
    
    for code in country_codes:
        # Get full country name from mapping
        country_name = COUNTRY_CODE_MAP.get(code, code)
        logging.info("Searching for country: %s (%s)", country_name, code)
        
        try:
            # Click search input
            search_input = driver.find_element(*SPECIFIC_COUNTRIES_SEARCH_INPUT)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", search_input)
            search_input.click()
            time.sleep(0.3)
            
            # Clear any previous search
            search_input.send_keys(Keys.CONTROL, "a")
            search_input.send_keys(Keys.DELETE)
            time.sleep(0.2)
            
            # Type country name
            search_input.send_keys(country_name)
            time.sleep(1.0)  # Wait for dropdown results
            save_ss(driver, f"country_search_{code}")
            
            # Click checkbox for this country
            checkbox_xpath = f'//span[contains(text(), "{country_name}")]/preceding-sibling::button[@role="checkbox"]'
            checkbox = driver.find_element(By.XPATH, checkbox_xpath)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", checkbox)
            checkbox.click()
            time.sleep(1.0)
            save_ss(driver, f"country_selected_{code}")
            
            logging.info("Selected country: %s", country_name)
            
            # Fill pricing for this country
            fill_country_pricing(driver, country_name, code)
            
        except Exception as e:
            logging.error("Failed to process country %s (%s): %s", country_name, code, e)
            save_ss(driver, f"country_failed_{code}")
    
    logging.info("All specific countries processed successfully")


def exclude_countries_and_price(driver, row: pd.Series):
    """
    Handle "All Countries Except" distribution:
    1. Read excluded countries from "Avail Countries Excluded" column
    2. Search and select each country to exclude
    3. Fill default USD pricing (same as worldwide)
    4. If India is NOT excluded, add India-specific pricing (INR)
    """
    exc_col = getattr(config, "AVAIL_EXCLUDED_COL", "").strip()
    if not exc_col:
        logging.warning("AVAIL_EXCLUDED_COL not configured")
        return
    
    excluded_value = row.get(exc_col, "")
    excluded_codes = parse_country_codes(excluded_value)
    
    logging.info("Excluding countries: %s", excluded_codes)
    
    # Step 1: Exclude countries from the list
    for code in excluded_codes:
        country_name = COUNTRY_CODE_MAP.get(code, code)
        logging.info("Searching to exclude country: %s (%s)", country_name, code)
        
        try:
            # Click search input
            search_input = driver.find_element(*EXCLUDED_COUNTRIES_SEARCH_INPUT)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", search_input)
            search_input.click()
            time.sleep(0.3)
            
            # Clear any previous search
            search_input.send_keys(Keys.CONTROL, "a")
            search_input.send_keys(Keys.DELETE)
            time.sleep(0.2)
            
            # Type country name
            search_input.send_keys(country_name)
            time.sleep(1.0)  # Wait for dropdown results
            save_ss(driver, f"exclude_search_{code}")
            
            # Click checkbox to exclude this country
            checkbox_xpath = f'//span[contains(text(), "{country_name}")]/preceding-sibling::button[@role="checkbox"]'
            checkbox = driver.find_element(By.XPATH, checkbox_xpath)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'})", checkbox)
            checkbox.click()
            time.sleep(0.5)
            save_ss(driver, f"excluded_{code}")
            
            logging.info("Excluded country: %s", country_name)
        except Exception as e:
            logging.error("Failed to exclude country %s (%s): %s", country_name, code, e)
            save_ss(driver, f"exclude_failed_{code}")
    
    # Step 2: Fill default pricing (USD) - same as worldwide default
    logging.info("Filling default pricing for 'All Countries Except'...")
    fill_worldwide_pricing(driver)
    
    # Step 3: If India is NOT in excluded list, add India-specific pricing
    if "IN" not in excluded_codes:
        logging.info("India not excluded - adding India-specific pricing...")
        add_india_custom_pricing(driver)
        fill_india_pricing(driver)
    else:
        logging.info("India is excluded - skipping India-specific pricing")
    
    logging.info("'All Countries Except' pricing completed")


def run_vod_campaign_flow(driver, row: pd.Series):
    """
    Standalone VOD campaign creation flow.
    Assumes we are on the 'create-new-campaign' page after login.
    """
    # Step 1: select first project card
    logging.info("Selecting first project card for VOD campaign (standalone)...")
    safe_click(driver, CAMPAIGN_PROJECT_FIRST_CARD, timeout=config.WAIT_TIMEOUT)
    time.sleep(1.0)
    save_ss(driver, "campaign_project_selected_standalone")

    # Step 2: choose 'Video on Demand'
    logging.info("Choosing 'Video on Demand' campaign type (standalone)...")
    safe_click(driver, CAMPAIGN_TYPE_VOD_CARD, timeout=config.WAIT_TIMEOUT)
    time.sleep(1.0)
    save_ss(driver, "campaign_type_vod_selected_standalone")

    # Step 3: click Next Step
    logging.info("Clicking 'Next Step' in VOD campaign setup (standalone)...")
    safe_click(driver, CAMPAIGN_NEXT_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(2.0)
    save_ss(driver, "campaign_next_step_clicked_standalone")

    # Step 4: on the next page, select distribution regions based on sheet data
    select_distribution_regions(driver, row)
    
    # Step 5: fill pricing options based on distribution strategy
    strategy = decide_distribution_strategy(row)
    if strategy == "world":
        fill_worldwide_pricing(driver)
        # Step 6: add India for custom pricing when World Wide is selected
        add_india_custom_pricing(driver)
        # Step 7: fill India-specific pricing (INR)
        fill_india_pricing(driver)
    elif strategy == "specific":
        # Step 5a: select specific countries from the sheet
        select_specific_countries(driver, row)
    elif strategy == "except":
        # Step 5b: exclude countries and fill default + India pricing if applicable
        exclude_countries_and_price(driver, row)
    
    # Step 6: Click Next Step after pricing is complete
    logging.info("Clicking Next Step after pricing completion...")
    safe_click(driver, PRICING_NEXT_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(2.0)
    save_ss(driver, "pricing_next_step_clicked")

    # Step 7: Upload movie from sheet (pre-uploaded selection via modal)
    try:
        movie_filename_col = "Movie Filename"
        movie_filename = str(row.get(movie_filename_col, "")).strip()
        if movie_filename and movie_filename.lower() != "nan":
            logging.info("Starting movie upload selection for: %s", movie_filename)
            select_preuploaded_movie(driver, movie_filename)
        else:
            logging.info("No movie filename provided in sheet; skipping upload selection.")
    except Exception as e:
        logging.exception("Movie upload selection step failed: %s", e)

    # Step 8: Select primary audio language from sheet
    try:
        lang_col = "Original Spoken Language"
        raw_language = row.get(lang_col, "")
        select_primary_audio_language(driver, raw_language)
    except Exception as e:
        logging.exception("Primary audio language step failed: %s", e)
    
    # Step 9: Upload subtitles from sheet (on same page as audio language)
    try:
        upload_subtitles_from_sheet(driver, row)
    except Exception as e:
        logging.exception("Subtitle upload step failed: %s", e)
    
    # Step 10: Click Next Step to proceed after audio language and subtitles
    logging.info("Clicking Next Step after audio/subtitles...")
    safe_click(driver, CAMPAIGN_NEXT_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(2.0)
    save_ss(driver, "after_audio_subtitles_next")
    
    # Step 11: Upload background art (16:9) from sheet
    try:
        bg_art_col = "Key Art 16:9 Filename"
        bg_art_filename = str(row.get(bg_art_col, "")).strip()
        if bg_art_filename and bg_art_filename.lower() != "nan":
            logging.info("Starting background art upload: %s", bg_art_filename)
            upload_background_art(driver, bg_art_filename)
        else:
            logging.info("No background art filename provided in sheet; skipping upload.")
    except Exception as e:
        logging.exception("Background art upload step failed: %s", e)
    
    # Step 12: Select quality settings (HDR, Stereo, 1080p)
    try:
        select_quality_settings(driver)
    except Exception as e:
        logging.exception("Quality settings step failed: %s", e)
    
    # Step 13: Click Next Step after quality settings
    logging.info("Clicking Next Step after quality settings...")
    safe_click(driver, CAMPAIGN_NEXT_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(2.0)
    save_ss(driver, "after_quality_settings_next")
    
    # Step 14: Click Create Campaign button (final step)
    logging.info("Clicking Create Campaign button...")
    safe_click(driver, CREATE_CAMPAIGN_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(3.0)
    save_ss(driver, "campaign_created")
    logging.info("Campaign created successfully!")


def select_preuploaded_movie(driver, filename: str) -> bool:
    """
    Open the upload modal via the Choose File card, search by filename (or suffix
    after the first '-'), select the checkbox, and confirm.
    Returns True on success, False otherwise.
    """
    # Open the upload area/modal
    logging.info("Opening movie upload modal...")
    safe_click(driver, UPLOAD_MOVIE_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.8)
    save_ss(driver, "movie_upload_modal_opened")

    # Normalize filename to search term (ignore random prefix before '-')
    name_only = (filename or "").split("/")[-1].strip()
    base = name_only.rsplit(".", 1)[0] if "." in name_only else name_only
    suffix = base.split("-", 1)[1] if "-" in base else base
    search_term = suffix or base or name_only

    # Type search term
    inp = wait_for(driver, UPLOAD_MOVIE_MODAL_SEARCH, timeout=config.WAIT_TIMEOUT)
    inp.click()
    inp.send_keys(Keys.CONTROL, "a")
    inp.send_keys(Keys.DELETE)
    inp.send_keys(search_term)
    # Mandatory 2 second delay after typing search to allow results to populate
    time.sleep(2.0)
    save_ss(driver, "movie_upload_search_results")

    # Try clicking the first matching row checkbox
    try:
        # Prefer a checkbox within the first visible result block
        checkboxes = driver.find_elements(*UPLOAD_MOVIE_ROW_CHECKBOX)
        if not checkboxes:
            logging.warning("No result checkboxes found for movie search: %s", search_term)
            save_ss(driver, "movie_upload_no_results")
            return False
        target = checkboxes[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", target)
        target.click()
        time.sleep(0.4)
        save_ss(driver, "movie_upload_row_selected")
    except Exception as e:
        logging.error("Failed to select movie row: %s", e)
        save_ss(driver, "movie_upload_select_failed")
        return False

    # Confirm selection
    try:
        safe_click(driver, UPLOAD_MOVIE_CONFIRM, timeout=config.WAIT_TIMEOUT)
        time.sleep(2.0)
        save_ss(driver, "movie_upload_confirmed")
        return True
    except Exception as e:
        logging.error("Movie upload confirm failed: %s", e)
        save_ss(driver, "movie_upload_confirm_fail")
        return False


def load_subtitle_language_json():
    """Load subtitle language codes from JSON file."""
    json_path = Path(__file__).parent / "subtiles code.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            entries = data.get('data', [])
            logging.info("Loaded %d subtitle language entries from JSON", len(entries))
            return entries
    except Exception as e:
        logging.error("Failed to load subtitle language JSON from %s: %s", json_path, e)
        return []

# Load subtitle language data once
SUBTITLE_LANG_DATA = load_subtitle_language_json()


def normalize_language_code(code: str) -> str:
    """Convert language code to full name, with fallback to JSON lookup.
    
    Process:
    1. Check simplified LANGUAGE_MAP first (en -> English)
    2. If not found, search JSON by rfc5646Tag (cmn-hans -> Chinese)
    3. Map to simplified language name (Chinese - Mandarin - Simplified -> Chinese)
    4. If still not found, return empty and log warning
    
    Examples:
        en -> English (from LANGUAGE_MAP)
        en-GB -> English (strip region, use LANGUAGE_MAP)
        cmn-hans -> Chinese (from JSON, simplified)
        es-MX -> Spanish (strip region, use LANGUAGE_MAP)
    """
    if not code or str(code).lower() == 'nan':
        return ""
    
    original_code = str(code).strip()
    logging.debug("Normalizing language code: '%s'", original_code)
    
    # Step 1: Try simplified LANGUAGE_MAP with base code (strip region)
    base_code = original_code.split('-')[0].lower()
    if base_code in LANGUAGE_MAP:
        result = LANGUAGE_MAP[base_code]
        logging.debug("Found '%s' -> '%s' in LANGUAGE_MAP", original_code, result)
        return result
    
    # Step 2: Search in JSON by rfc5646Tag (case-insensitive match)
    code_lower = original_code.lower()
    logging.debug("Searching JSON for code: '%s'", code_lower)
    
    for entry in SUBTITLE_LANG_DATA:
        rfc_tag = entry.get('rfc5646Tag', '').lower()
        if rfc_tag == code_lower:
            # Extract base language name (before dash or special markers)
            dcnc_lang = entry.get('dcncLanguage', '')
            logging.debug("Found in JSON: rfc5646Tag='%s', dcncLanguage='%s'", rfc_tag, dcnc_lang)
            
            # Map to simplified form
            base_lang = dcnc_lang.split(' - ')[0]  # "Chinese - Mandarin - Simplified" -> "Chinese"
            
            # Try to match in LANGUAGE_MAP by checking if base_lang matches any value
            for map_code, map_name in LANGUAGE_MAP.items():
                if map_name.lower() == base_lang.lower():
                    logging.info("Mapped '%s' to '%s' via JSON lookup (matched '%s' in LANGUAGE_MAP)", 
                               original_code, map_name, base_lang)
                    return map_name
            
            # If not in LANGUAGE_MAP, use the base language from JSON
            if base_lang:
                logging.info("Using base language '%s' from JSON for code '%s' (not in LANGUAGE_MAP)", 
                           base_lang, original_code)
                return base_lang
    
    # Step 3: Not found - log warning and return empty
    logging.warning("Language code '%s' not found in LANGUAGE_MAP or JSON (loaded %d entries) - skipping", 
                   original_code, len(SUBTITLE_LANG_DATA))
    return ""


def parse_subtitle_data(row: pd.Series) -> list[tuple[str, str, str]]:
    """Parse subtitle languages and filenames from sheet.
    
    Returns list of (language_name, filename, original_code) tuples.
    Both columns are comma-separated and paired by index.
    Returns empty list if either column is missing/empty.
    Skips duplicate languages (only keeps first occurrence).
    """
    lang_col = "Movie Subtitles/Captions Languages"
    file_col = "Movie Subtitles/Captions Filenames"
    
    # Get values and check if they exist
    lang_val = row.get(lang_col, "")
    file_val = row.get(file_col, "")
    
    # Convert to string and check for empty/NaN
    lang_str = str(lang_val).strip() if pd.notna(lang_val) else ""
    file_str = str(file_val).strip() if pd.notna(file_val) else ""
    
    # If either is empty or 'nan', skip subtitles
    if not lang_str or lang_str.lower() == 'nan' or not file_str or file_str.lower() == 'nan':
        logging.info("No subtitle data found in sheet (empty or NaN)")
        return []
    
    # Split by comma and clean
    lang_codes = [c.strip() for c in lang_str.split(',') if c.strip()]
    filenames = [f.strip() for f in file_str.split(',') if f.strip()]
    
    # Pair them up, tracking seen languages to skip duplicates
    pairs = []
    seen_languages = set()
    
    for i, code in enumerate(lang_codes):
        if i < len(filenames):
            lang_name = normalize_language_code(code)
            if lang_name:
                # Check for duplicate language
                if lang_name.lower() in seen_languages:
                    logging.warning("Duplicate language '%s' (code: %s) detected - skipping file '%s'", 
                                  lang_name, code, filenames[i])
                    continue
                
                seen_languages.add(lang_name.lower())
                pairs.append((lang_name, filenames[i], code))
            else:
                logging.warning("Language code '%s' could not be mapped - skipping file '%s'", 
                              code, filenames[i])
    
    return pairs


def select_subtitle_language_and_file(driver, language_name: str, filename: str, is_first: bool) -> bool:
    """Select subtitle language via combobox, then upload file via modal.
    
    Args:
        language_name: Full language name (e.g., "English", "Spanish")
        filename: Subtitle filename to search and select
        is_first: True if this is the first subtitle (row already exists), False to click Add Another
    
    Returns True on success.
    """
    try:
        # If not first subtitle, click "Add Another Subtitle"
        if not is_first:
            logging.info("Clicking 'Add Another Subtitle' button...")
            safe_click(driver, ADD_ANOTHER_SUBTITLE_BUTTON, timeout=config.WAIT_TIMEOUT)
            time.sleep(0.8)
            save_ss(driver, f"add_subtitle_{language_name}")
        
        # Click language combobox (find last one on page for newly added rows)
        logging.info("Selecting subtitle language: %s", language_name)
        time.sleep(0.5)
        
        # Find all comboboxes with chevron icon (subtitle language dropdowns)
        lang_buttons = driver.find_elements(*SUBTITLE_LANGUAGE_COMBOBOX)
        logging.info("Found %d subtitle language combobox(es)", len(lang_buttons))
        
        if not lang_buttons:
            logging.warning("No subtitle language combobox found")
            save_ss(driver, "no_subtitle_combobox")
            return False
        
        target_btn = lang_buttons[-1]  # Last one (newest row)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", target_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click()", target_btn)  # Use JS click
        time.sleep(1.0)
        save_ss(driver, f"subtitle_combobox_opened_{language_name}")
        
        # Type language name directly in the active element (dropdown auto-focuses input)
        logging.info("Typing subtitle language in dropdown: %s", language_name)
        for char in language_name:
            driver.switch_to.active_element.send_keys(char)
            time.sleep(0.1)
        time.sleep(1.0)
        save_ss(driver, f"subtitle_lang_typed_{language_name}")
        
        # Press Enter to select
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(0.8)
        save_ss(driver, f"subtitle_lang_selected_{language_name}")
        
        # Click "Choose file" button for subtitle upload
        logging.info("Opening subtitle file modal for: %s", filename)
        file_buttons = driver.find_elements(*SUBTITLE_CHOOSE_FILE)
        if not file_buttons:
            logging.warning("No subtitle choose file button found")
            return False
        
        target_file_btn = file_buttons[-1]  # Last one (newest row)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", target_file_btn)
        target_file_btn.click()
        time.sleep(0.8)
        save_ss(driver, "subtitle_modal_opened")
        
        # Search for subtitle file
        search_input = wait_for(driver, SUBTITLE_MODAL_SEARCH, timeout=config.WAIT_TIMEOUT)
        search_input.click()
        search_input.send_keys(Keys.CONTROL, 'a')
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(filename)
        time.sleep(2.0)  # 2 second delay as requested
        save_ss(driver, f"subtitle_search_{filename}")
        
        # Select first checkbox
        checkboxes = driver.find_elements(*SUBTITLE_MODAL_CHECKBOX)
        if not checkboxes:
            logging.warning("No subtitle file checkbox found for: %s", filename)
            save_ss(driver, f"subtitle_no_results_{filename}")
            return False
        
        checkbox = checkboxes[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", checkbox)
        checkbox.click()
        time.sleep(0.4)
        save_ss(driver, f"subtitle_selected_{filename}")
        
        # Confirm selection
        safe_click(driver, SUBTITLE_MODAL_CONFIRM, timeout=config.WAIT_TIMEOUT)
        time.sleep(1.5)
        save_ss(driver, f"subtitle_confirmed_{language_name}")
        
        logging.info("Subtitle uploaded: %s - %s", language_name, filename)
        return True
        
    except Exception as e:
        logging.error("Failed to upload subtitle %s - %s: %s", language_name, filename, e)
        save_ss(driver, f"subtitle_failed_{language_name}")
        return False


def select_quality_settings(driver):
    """Select hardcoded quality settings: HDR, Stereo, 1080p."""
    try:
        logging.info("Selecting quality settings: HDR, Stereo, 1080p")
        
        # Click HDR label (Video Enhancement)
        hdr_label = wait_for(driver, QUALITY_HDR_LABEL, timeout=config.WAIT_TIMEOUT)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", hdr_label)
        time.sleep(0.3)
        
        # Check if already selected (border-blue-500 class)
        if 'border-blue-500' not in hdr_label.get_attribute('class'):
            driver.execute_script("arguments[0].click()", hdr_label)
            time.sleep(0.5)
            logging.info("Selected HDR")
        else:
            logging.info("HDR already selected")
        
        # Click Stereo label (Audio Quality)
        stereo_label = wait_for(driver, QUALITY_STEREO_LABEL, timeout=config.WAIT_TIMEOUT)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", stereo_label)
        time.sleep(0.3)
        
        if 'border-blue-500' not in stereo_label.get_attribute('class'):
            driver.execute_script("arguments[0].click()", stereo_label)
            time.sleep(0.5)
            logging.info("Selected Stereo")
        else:
            logging.info("Stereo already selected")
        
        # Click 1080p label (Resolution)
        p1080_label = wait_for(driver, QUALITY_1080P_LABEL, timeout=config.WAIT_TIMEOUT)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", p1080_label)
        time.sleep(0.3)
        
        if 'border-blue-500' not in p1080_label.get_attribute('class'):
            driver.execute_script("arguments[0].click()", p1080_label)
            time.sleep(0.5)
            logging.info("Selected 1080p")
        else:
            logging.info("1080p already selected")
        
        save_ss(driver, "quality_settings_selected")
        logging.info("Quality settings selected successfully")
        
    except Exception as e:
        logging.error("Failed to select quality settings: %s", e)
        save_ss(driver, "quality_settings_failed")


def upload_background_art(driver, filename: str) -> bool:
    """Upload background art (16:9) from pre-uploaded images.
    
    Args:
        filename: Background art filename from sheet
        
    Returns True on success.
    """
    try:
        logging.info("Uploading background art: %s", filename)
        
        # Click "Add Background Art" button
        safe_click(driver, ADD_BACKGROUND_ART_BUTTON, timeout=config.WAIT_TIMEOUT)
        time.sleep(0.8)
        save_ss(driver, "background_art_modal_opened")
        
        # Search for image
        search_input = wait_for(driver, BACKGROUND_ART_SEARCH, timeout=config.WAIT_TIMEOUT)
        search_input.click()
        search_input.send_keys(Keys.CONTROL, 'a')
        search_input.send_keys(Keys.DELETE)
        search_input.send_keys(filename)
        time.sleep(2.0)  # Wait for search results
        save_ss(driver, f"background_art_search_{filename}")
        
        # Select first checkbox
        checkboxes = driver.find_elements(*BACKGROUND_ART_CHECKBOX)
        if not checkboxes:
            logging.warning("No background art found for: %s", filename)
            save_ss(driver, f"background_art_no_results_{filename}")
            return False
        
        checkbox = checkboxes[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", checkbox)
        checkbox.click()
        time.sleep(0.4)
        save_ss(driver, f"background_art_selected_{filename}")
        
        # Confirm selection
        safe_click(driver, BACKGROUND_ART_CONFIRM, timeout=config.WAIT_TIMEOUT)
        time.sleep(1.5)
        save_ss(driver, "background_art_confirmed")
        
        logging.info("Background art uploaded successfully: %s", filename)
        return True
        
    except Exception as e:
        logging.error("Failed to upload background art %s: %s", filename, e)
        save_ss(driver, f"background_art_failed_{filename}")
        return False


def upload_subtitles_from_sheet(driver, row: pd.Series):
    """Upload all subtitles from the sheet's subtitle columns."""
    subtitle_pairs = parse_subtitle_data(row)
    
    if not subtitle_pairs:
        logging.info("No subtitles to upload from sheet")
        return
    
    logging.info("Uploading %d subtitle(s)...", len(subtitle_pairs))
    logging.info("Subtitle codes detected: %s", 
                 ', '.join([f"{code} -> {lang}" for lang, _, code in subtitle_pairs]))
    
    # Scroll down to subtitle section and wait for it to load
    time.sleep(1.0)
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(1.5)
    save_ss(driver, "subtitle_section_visible")
    
    for idx, (lang_name, filename, original_code) in enumerate(subtitle_pairs):
        is_first = (idx == 0)
        logging.info("Processing subtitle %d/%d: %s (%s) - %s", 
                    idx + 1, len(subtitle_pairs), lang_name, original_code, filename)
        select_subtitle_language_and_file(driver, lang_name, filename, is_first)
    
    logging.info("All subtitles processed")


def select_primary_audio_language(driver, raw_language: str) -> bool:
    """Select the primary audio language using the combobox.

    raw_language may include region in parentheses (e.g. 'English (United Kingdom)').
    We strip anything in parentheses and use the base language token.
    The dropdown filters as you type letter-by-letter (no delete/backspace needed).
    Returns True if selection attempt executed.
    """
    if not raw_language or str(raw_language).lower() == 'nan':
        logging.info("No primary audio language provided; skipping selection.")
        return False

    import re
    base = re.sub(r'\s*\(.*?\)\s*', '', str(raw_language)).strip()
    if not base:
        logging.info("Primary audio language empty after cleaning; skipping.")
        return False

    logging.info("Selecting primary audio language: %s (cleaned: %s)", raw_language, base)
    try:
        btn = wait_for(driver, PRIMARY_AUDIO_LANGUAGE_COMBOBOX, timeout=config.WAIT_TIMEOUT)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)
        btn.click()
        time.sleep(0.5)
        save_ss(driver, "language_dropdown_opened")

        # After clicking combobox, type each letter one by one (dropdown filters as you type)
        # No need to find input field - just send keys directly
        for char in base:
            driver.switch_to.active_element.send_keys(char)
            time.sleep(0.1)  # small delay between letters
        
        time.sleep(0.8)  # brief pause for final filtering
        save_ss(driver, "language_typed")
        
        # Press ENTER to select the filtered result
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        time.sleep(0.8)
        save_ss(driver, "primary_language_selected")
        return True
    except Exception as e:
        logging.error("Primary audio language selection failed: %s", e)
        save_ss(driver, "primary_language_select_failed")
        return False


def main():
    print("Starting VOD campaign-only automation...")

    # Choose sheet and row to drive campaign metadata (e.g. distribution regions)
    sheet_path = choose_sheet_path()
    df = load_sheet(sheet_path)
    if df.empty:
        logging.error("Selected sheet has no rows; aborting.")
        return
    row = df.iloc[0]

    driver = build_driver()

    # Use a dedicated campaign start URL so we can test without creating a project
    campaign_url = getattr(
        config,
        "CAMPAIGN_START_URL",
        "https://filmmakers.brew.tv/dashboard/filmmaker/create-new-campaign",
    )
    driver.get(campaign_url)
    time.sleep(2)
    auto_ok = perform_login(driver)
    if auto_ok:
        logging.info("Automated login submitted. Waiting 2s before continuing...")
        time.sleep(2)
    logging.info("If login still needed, complete it in the browser.")
    input("Press ENTER once you are on the campaign creation page with project cards visible...")

    try:
        run_vod_campaign_flow(driver, row)
        logging.info("VOD campaign flow (standalone) completed for current sheet row.")
    except Exception as e:
        logging.exception("Standalone VOD campaign flow failed: %s", e)
        save_ss(driver, "campaign_standalone_exc")

    logging.info("="*80)
    logging.info("Campaign creation completed.")
    logging.info("Browser will remain open for inspection.")
    logging.info("="*80)
    
    input("\nPress ENTER to close the browser and exit...")
    # driver.quit()


if __name__ == "__main__":
    main()


