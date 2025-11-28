# main.py
import os
import time, logging
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import config
from selectors_example import *
from automation_utils import wait_for, wait_clickable, save_ss, safe_click

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def build_driver():
    options = webdriver.ChromeOptions()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver

def paste_imdb_and_fetch(driver, imdb_link):
    logging.info("Pasting IMDb link...")
    imdb_input = wait_for(driver, IMDB_INPUT, timeout=config.WAIT_TIMEOUT)
    imdb_input.click()
    imdb_input.send_keys(Keys.CONTROL, "a")
    imdb_input.send_keys(Keys.DELETE)
    imdb_input.send_keys(imdb_link)
    time.sleep(0.4)
    # trigger fetch
    try:
        btn = driver.find_element(*IMDB_TRIGGER_BUTTON)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)
        btn.click()
    except Exception:
        imdb_input.send_keys(Keys.ENTER)
    # give the site time to fetch and populate data before touching synopsis
    time.sleep(6)
    save_ss(driver, "after_imdb_fetch")

def replace_synopsis(driver, synopsis_text):
    logging.info("Replacing synopsis...")
    ta = wait_for(driver, SYNOPSIS_TEXTAREA, timeout=config.WAIT_TIMEOUT)
    ta.click()
    ta.send_keys(Keys.CONTROL, "a")
    ta.send_keys(Keys.DELETE)
    ta.send_keys(str(synopsis_text))
    time.sleep(0.4)
    save_ss(driver, "synopsis_filled")

def go_next_page(driver, next_selector, step_name="next"):
    logging.info(f"Clicking next ({step_name})...")
    safe_click(driver, next_selector, timeout=config.WAIT_TIMEOUT)
    time.sleep(1)
    save_ss(driver, f"after_next_{step_name}")

def clear_keywords(driver):
    """
    Clear all existing keywords by focusing the keywords input and
    repeatedly backspacing / deleting any content.
    """
    logging.info("Clearing keywords via backspace in input...")
    try:
        # If we are already at the 10-keyword limit, the input can be disabled until
        # at least one chip is removed. Try clicking the 'x' on one keyword first.
        try:
            remove_buttons = driver.find_elements(*KEYWORDS_CHIP_REMOVE)
            if remove_buttons:
                btn = remove_buttons[0]
                driver.execute_script("arguments[0].scrollIntoView({block:'center'})", btn)
                btn.click()
                time.sleep(0.3)
                logging.info("Clicked one keyword remove (x) button before clearing via backspace.")
        except Exception as e:
            logging.debug("No removable keyword chip found or click failed: %s", e)

        inp = wait_for(driver, KEYWORDS_INPUT, timeout=config.WAIT_TIMEOUT)
        inp.click()
        # This field does not support Ctrl+A reliably, so just spam BACKSPACE
        for _ in range(100):
            inp.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        save_ss(driver, "keywords_cleared_input")
    except Exception as e:
        logging.error("Clearing keywords via input failed: %s", e)
        save_ss(driver, "keywords_clear_failed")

def add_tags(driver, tags_text):
    if not isinstance(tags_text, str):
        tags_text = "" if pd.isna(tags_text) else str(tags_text)
    parts = [p.strip() for p in tags_text.replace(";", ",").split(",") if p.strip()]
    if not parts:
        logging.info("No tags to add.")
        return
    logging.info("Adding tags: %s", parts)
    # After clear_keywords, the keywords input already has focus. Rely on the active element
    # instead of re-finding by placeholder (which can change once focused).
    try:
        inp = driver.switch_to.active_element
    except Exception:
        inp = wait_for(driver, KEYWORDS_INPUT, timeout=config.WAIT_TIMEOUT)
        inp.click()
    for t in parts:
        inp.send_keys(t)
        time.sleep(0.15)
        inp.send_keys(Keys.ENTER)
        time.sleep(0.2)
    save_ss(driver, "tags_added")

def _normalize_trailer_key(raw_key: str) -> tuple[str, str, str]:
    """
    Given a trailer file name (e.g. 'mpz3-xjjq_beowulf_and_grendel_trailer.mp4'),
    return a tuple of:
      - full file name
      - base name without extension
      - suffix with everything after the first '-' (to ignore random prefixes)
    """
    name_only = (raw_key or "").split("/")[-1].strip()
    base = name_only.rsplit(".", 1)[0] if "." in name_only else name_only
    suffix = base.split("-", 1)[1] if "-" in base else base
    return name_only, base, suffix


def select_preuploaded_trailer(driver, trailer_key):
    logging.info("Selecting pre-uploaded trailer for key: %s", trailer_key)
    # Open the upload modal by clicking the film icon / button
    safe_click(driver, UPLOAD_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(0.8)
    save_ss(driver, "upload_modal_opened")

    # Type a normalized search term so we can ignore random prefixes before '-'
    name_only, base, suffix = _normalize_trailer_key(str(trailer_key))
    search_term = suffix or base or name_only

    search = wait_for(driver, UPLOAD_MODAL_SEARCH, timeout=config.WAIT_TIMEOUT)
    search.click()
    search.send_keys(search_term)
    # give the backend a moment to return and render results
    time.sleep(2.0)
    save_ss(driver, "upload_search_results")

    # Find all label divs with a title attribute and try to match by title/text,
    # then click the associated checkbox within the same row.
    labels = driver.find_elements(*UPLOAD_MODAL_ROW_LABEL)
    chosen = False
    for label_el in labels:
        try:
            title_attr = (label_el.get_attribute("title") or "").strip()
            label_text = (label_el.text or "").strip()
            haystack = (title_attr or label_text).lower()

            if not haystack:
                continue

            if (
                search_term.lower() in haystack
                or base.lower() in haystack
                or name_only.lower() in haystack
            ):
                # Find the parent row, then its checkbox button
                click_target = label_el
                try:
                    row_el = label_el.find_element(
                        By.XPATH,
                        ".//ancestor::div[contains(@class,'flex items-center')][1]",
                    )
                    try:
                        click_target = row_el.find_element(*UPLOAD_MODAL_ROW_SELECT)
                    except Exception:
                        click_target = row_el
                except Exception:
                    click_target = label_el

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'})", click_target
                )
                click_target.click()
                chosen = True
                time.sleep(0.4)
                save_ss(driver, f"upload_row_selected_{haystack[:30]}")
                break
        except Exception:
            continue

    if not chosen:
        logging.warning("No match found for trailer key: %s", trailer_key)
        save_ss(driver, "upload_no_match")
        return False

    # Click confirm / attach button if present
    try:
        safe_click(driver, UPLOAD_MODAL_CONFIRM, timeout=config.WAIT_TIMEOUT)
        # give the UI a moment to attach/close modal
        time.sleep(3.0)
        save_ss(driver, "upload_confirmed")
        return True
    except Exception as e:
        logging.error("Upload confirm failed: %s", e)
        save_ss(driver, "upload_confirm_fail")
        return False


def fill_relationship_and_next(driver):
    """
    On the socials / relationship page, hard-code the relationship as 'producer'
    for every project, then advance to the next page.
    """
    logging.info("Filling relationship to project as 'producer'...")
    inp = wait_for(driver, RELATIONSHIP_INPUT, timeout=config.WAIT_TIMEOUT)
    inp.click()
    # Clear anything that might be there, then type 'producer'
    for _ in range(40):
        inp.send_keys(Keys.BACKSPACE)
    inp.send_keys("producer")
    time.sleep(2.0)
    save_ss(driver, "relationship_filled")
    go_next_page(driver, PAGE4_NEXT_BUTTON, "page4->page5")


def submit_final_project(driver):
    """
    On the last page, click the 'Create Project' button to submit.
    """
    logging.info("Clicking final 'Create Project' button...")
    safe_click(driver, PAGE5_CREATE_BUTTON, timeout=config.WAIT_TIMEOUT)
    time.sleep(3.0)
    save_ss(driver, "project_created")

def load_sheet(path: str) -> pd.DataFrame:
    """
    Load data from either an Excel file (.xlsx) or a CSV file (.csv),
    based on the extension of config.EXCEL_PATH.
    """
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)


def choose_sheet_path() -> str:
    """
    Let the user choose which Excel/CSV file to use for this run.
    Looks in config.EXCEL_DIR and allows selecting by number or typing a path.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    excel_dir = getattr(config, "EXCEL_DIR", "").strip()
    default_name = getattr(config, "EXCEL_PATH", "").strip()

    folder_path = os.path.join(root_dir, excel_dir) if excel_dir else root_dir

    files = []
    if os.path.isdir(folder_path):
        files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".csv", ".xlsx"))
        ]

    print("\n=== Sheet selection ===")
    if files:
        print(f"Folder: {folder_path}")
        for idx, name in enumerate(files, start=1):
            print(f"  [{idx}] {name}")
    else:
        print(f"No .csv/.xlsx files found in: {folder_path}")

    if default_name:
        print(f"\nPress ENTER to use default from config: {default_name}")

    choice = input("Type number to select a file, or type a path, then ENTER: ").strip()

    # Numbered choice from EXCEL_DIR
    if choice.isdigit() and files:
        idx = int(choice)
        if 1 <= idx <= len(files):
            chosen = os.path.join(excel_dir, files[idx - 1])
            logging.info("Using sheet: %s", chosen)
            return chosen

    # Explicit path typed by user
    if choice:
        if os.path.isabs(choice):
            chosen = choice
        else:
            chosen = os.path.join(root_dir, choice)
        logging.info("Using user-provided sheet path: %s", chosen)
        return chosen

    # Fallback to config.EXCEL_PATH inside EXCEL_DIR (if set)
    if default_name:
        chosen = os.path.join(excel_dir, default_name) if excel_dir else default_name
        logging.info("Using default sheet from config: %s", chosen)
        return chosen

    raise RuntimeError("No sheet selected and no default EXCEL_PATH configured.")


def main():
    print("Starting automation...")  # basic sanity check that script is running
    sheet_path = choose_sheet_path()
    df = load_sheet(sheet_path)
    logging.info("Rows loaded: %d", len(df))

    # First gate: only process rows whose Avail Type(s) include 'tvod'.
    avail_col = getattr(config, "AVAIL_TYPE_COL", "").strip()
    if avail_col and avail_col in df.columns:
        def _has_tvod(val) -> bool:
            if pd.isna(val):
                return False
            return "tvod" in str(val).lower()

        mask = df[avail_col].apply(_has_tvod)
        if not mask.any():
            logging.warning(
                "No rows have 'tvod' in column '%s'. Cannot create any projects. "
                "Browser will not be opened.",
                avail_col,
            )
            for idx, row in df.iterrows():
                logging.info(
                    "Row %d skipped: %s=%r",
                    idx + 1,
                    avail_col,
                    row.get(avail_col, ""),
                )
            return

        skipped = len(df) - int(mask.sum())
        if skipped > 0:
            logging.info(
                "Filtering rows by 'tvod' in '%s': %d rows will be processed, %d skipped.",
                avail_col,
                int(mask.sum()),
                skipped,
            )
        df = df[mask].reset_index(drop=True)
    else:
        logging.warning(
            "Column '%s' not found in sheet. TVOD gating is skipped; all rows will be processed.",
            avail_col or "<empty>",
        )
    driver = build_driver()
    driver.get(config.START_URL)
    time.sleep(2)
    logging.info("Please login manually in the opened browser if required, then return to terminal and press ENTER.")
    input("Press ENTER after you log in and are on the create-project start page...")

    for idx, row in df.iterrows():
        logging.info("Processing %d/%d", idx+1, len(df))
        try:
            imdb_link = row.get(config.IMDB_COL, "")
            synopsis = row.get(config.SYNOPSIS_COL, "")
            tags = row.get(config.TAGS_COL, "")
            trailer_key = row.get(config.TRAILER_KEY_COL, "")

            paste_imdb_and_fetch(driver, imdb_link)
            replace_synopsis(driver, synopsis)
            go_next_page(driver, PAGE1_NEXT_BUTTON, "page1->page2")
            clear_keywords(driver)
            add_tags(driver, tags)
            go_next_page(driver, PAGE2_NEXT_BUTTON, "page2->page3")
            if trailer_key and str(trailer_key).strip().lower() != "nan":
                ok = select_preuploaded_trailer(driver, str(trailer_key).strip())
                if not ok:
                    logging.warning("Trailer selection failed for row %d", idx+1)
                else:
                    # After trailer is attached, advance to the socials page
                    go_next_page(driver, PAGE3_NEXT_BUTTON, "page3->page4")
                    fill_relationship_and_next(driver)
                    submit_final_project(driver)
            save_ss(driver, f"row_{idx+1}_done")
            time.sleep(1.0)
        except Exception as e:
            logging.exception("Row %d error: %s", idx+1, e)
            save_ss(driver, f"row_{idx+1}_exc")
    logging.info("All rows processed. Inspect browser; close when ready.")
    # driver.quit()

if __name__ == "__main__":
    main()
