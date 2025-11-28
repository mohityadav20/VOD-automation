# selectors_example.py
from selenium.webdriver.common.by import By

# PAGE 1 - Create Project
IMDB_INPUT = (By.CSS_SELECTOR, 'input[placeholder="https://www.imdb.com/title/tt4574334"]')  # paste IMDb link here
IMDB_TRIGGER_BUTTON = (By.CSS_SELECTOR, 'button.fetch-imdb')   # optional: if you have a fetch button
SYNOPSIS_TEXTAREA = (By.CSS_SELECTOR, 'textarea[placeholder="This is the Star Wars: The Rise of Skywalker synopsis ..."]')
PAGE1_NEXT_BUTTON = (By.XPATH, '//button[.//span[contains(normalize-space(.),"Add Specifications")]]')

# PAGE 2 - Project Specifications (Keywords)
# We clear keywords by first removing one chip via its "x" button (if present),
# then using BACKSPACE in the main input. Scope selectors to the Keywords box only.
KEYWORDS_CHIP = (
    By.CSS_SELECTOR,
    'div.max-w-xl span.flex.items-center.h-8.gap-1.px-3.py-1.text-sm.tracking-tight.text-black.border.rounded-lg.border-slate-100'
)  # keyword chip container inside Keywords section
KEYWORDS_CHIP_REMOVE = (
    By.CSS_SELECTOR,
    'div.max-w-xl button.p-1.rounded-full.hover\\:bg-slate-200'
)  # "x" button inside a keyword chip (Keywords only)
KEYWORDS_INPUT = (By.CSS_SELECTOR, 'input[placeholder="add more Keywords"]')   # input for adding keywords
PAGE2_NEXT_BUTTON = (By.XPATH, '//button[.//span[contains(normalize-space(.),"Add Key Visuals")]]')

# PAGE 3 - Key Visuals / Upload Trailer
# Clickable film icon / button that opens the pre-uploaded trailer modal
UPLOAD_BUTTON = (By.CSS_SELECTOR, 'svg.lucide.lucide-film.w-8.h-8.text-slate-500')

# Search input inside upload modal
UPLOAD_MODAL_SEARCH = (By.CSS_SELECTOR, 'input[placeholder="Search movies, tags..."]')

# Result items & label inside each item
UPLOAD_MODAL_RESULT_ROWS = (
    By.CSS_SELECTOR,
    'div.flex.items-center.px-4.py-3.group.transition.cursor-pointer'
)
UPLOAD_MODAL_ROW_LABEL = (
    By.CSS_SELECTOR,
    'div.font-semibold.font-\\[SwisseMed\\].tracking-tighter.text-gray-900.truncate[title]'
)
UPLOAD_MODAL_ROW_SELECT = (By.CSS_SELECTOR, 'button[role="checkbox"]')

# Confirm / attach button in modal
UPLOAD_MODAL_CONFIRM = (By.CSS_SELECTOR, 'button[title="Confirm"]')

# PAGE 3 -> PAGE 4 - Next button ("Add Socials")
PAGE3_NEXT_BUTTON = (By.XPATH, '//button[.//span[contains(normalize-space(.),"Add Socials")]]')

# PAGE 4 - Socials / Relationship to project
RELATIONSHIP_INPUT = (
    By.CSS_SELECTOR,
    'input.h-12.rounded-lg.tracking-tighter.truncate.bg-transparent.focus\\:outline-none.text-black.pl-10.w-\\[400px\\]'
)

# PAGE 4 -> PAGE 5 - Next button ("Add more production info")
PAGE4_NEXT_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"Add more production info")]]'
)

# PAGE 5 - Final step, submit form ("Create Project")
PAGE5_CREATE_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"Create Project")]]'
)
