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

# Step 6 - Project created screen: "Start Campaign" button
# The button is wrapped in an <a href="...create-new-campaign">, so target via the link.
START_CAMPAIGN_BUTTON = (
    By.CSS_SELECTOR,
    'a[href*="create-new-campaign"] button'
)

# VOD Campaign Creation - Step 1: select newly created project (first card)
# Target the active swiper slide's clickable card
CAMPAIGN_PROJECT_FIRST_CARD = (
    By.CSS_SELECTOR,
    'div.swiper-slide.swiper-slide-active div.cursor-pointer'
)

# VOD Campaign Creation - Step 2: choose "Video on Demand" campaign type
# Click the outer card that contains the 'Video on Demand' label to avoid overlays
CAMPAIGN_TYPE_VOD_CARD = (
    By.XPATH,
    '//div[contains(@class,"cursor-pointer") and .//p[normalize-space()="Video on Demand"]]'
)

# VOD Campaign Creation - Step 3: Next button ("Next Step")
CAMPAIGN_NEXT_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"Next Step")]]'
)

# VOD Campaign Pricing - Next Step button (after pricing is complete)
PRICING_NEXT_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"Next Step")]]'
)

# VOD Campaign - Upload Movie (Choose File card)
UPLOAD_MOVIE_BUTTON = (
    By.XPATH,
    '//div[contains(@class,"cursor-pointer") and .//p[contains(normalize-space(.),"Choose File")]]'
)

# Upload modal - search input for movies
UPLOAD_MOVIE_MODAL_SEARCH = (
    By.CSS_SELECTOR,
    'input[placeholder="Search movies, tags..."]'
)

# Upload modal - row checkbox within results
UPLOAD_MOVIE_ROW_CHECKBOX = (
    By.CSS_SELECTOR,
    'button[role="checkbox"]'
)

# Upload modal - confirm button
UPLOAD_MOVIE_CONFIRM = (
    By.CSS_SELECTOR,
    'button[title="Confirm"]'
)

# Primary Audio Language combobox button (find by lucide-languages icon, get parent button)
PRIMARY_AUDIO_LANGUAGE_COMBOBOX = (
    By.CSS_SELECTOR,
    'button[role="combobox"]'
)

# Subtitles Management - Language combobox (for each subtitle row)
# Matches button with "Select language" text OR any combobox with chevron icon in subtitle context
SUBTITLE_LANGUAGE_COMBOBOX = (
    By.XPATH,
    '//button[@role="combobox" and (contains(.,"Select language") or .//svg[contains(@class,"lucide-chevrons-up-down")])]'
)

# Subtitles Management - Language dropdown search input (appears after clicking combobox)
SUBTITLE_LANGUAGE_SEARCH = (
    By.CSS_SELECTOR,
    'input[placeholder="Search language..."]'
)

# Subtitles Management - Choose file button (upload icon)
SUBTITLE_CHOOSE_FILE = (
    By.XPATH,
    '//div[contains(@class,"cursor-pointer") and .//span[text()="Choose file"]]'
)

# Subtitles file upload modal - search input
SUBTITLE_MODAL_SEARCH = (
    By.CSS_SELECTOR,
    'input[placeholder="Search documents, tags..."]'
)

# Subtitles modal - checkbox for selecting subtitle file
SUBTITLE_MODAL_CHECKBOX = (
    By.CSS_SELECTOR,
    'button[role="checkbox"]'
)

# Subtitles modal - confirm button
SUBTITLE_MODAL_CONFIRM = (
    By.CSS_SELECTOR,
    'button[title="Confirm"]'
)

# Add Another Subtitle button
ADD_ANOTHER_SUBTITLE_BUTTON = (
    By.XPATH,
    '//button[contains(normalize-space(.),\"Add Another Subtitle\")]'
)

# Background Art - Add Background Art button
ADD_BACKGROUND_ART_BUTTON = (
    By.XPATH,
    '//button[contains(.,\"Add Background Art\")]'
)

# Background Art modal - search input
BACKGROUND_ART_SEARCH = (
    By.CSS_SELECTOR,
    'input[placeholder="Search images, colors, tags..."]'
)

# Background Art modal - image checkbox
BACKGROUND_ART_CHECKBOX = (
    By.CSS_SELECTOR,
    'button[role="checkbox"]'
)

# Background Art modal - confirm button
BACKGROUND_ART_CONFIRM = (
    By.CSS_SELECTOR,
    'button[title="Confirm"]'
)

# Create Campaign button (final step)
CREATE_CAMPAIGN_BUTTON = (
    By.XPATH,
    '//button[contains(.,\"Create Campaign\")]'
)

# Quality Settings - Video Enhancement, Audio Quality, Resolution (click labels, not hidden inputs)
QUALITY_HDR_LABEL = (
    By.XPATH,
    '//label[.//div[text()="HDR"]]'
)

QUALITY_STEREO_LABEL = (
    By.XPATH,
    '//label[.//div[text()="Stereo"]]'
)

QUALITY_1080P_LABEL = (
    By.XPATH,
    '//label[.//div[text()="Full HD/1080p"]]'
)

# VOD Campaign Creation - Distribution Regions cards
DIST_REGION_WORLD_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"World Wide")]]'
)
DIST_REGION_SPECIFIC_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"Specific Countries")]]'
)
DIST_REGION_EXCEPT_BUTTON = (
    By.XPATH,
    '//button[.//span[contains(normalize-space(.),"All Countries Except")]]'
)

# VOD Campaign Pricing - Default Pricing (USD) for World Wide
# Rental Price - HD checkbox, price and perceived inputs
RENTAL_HD_CHECKBOX = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
RENTAL_HD_PRICE_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="$"]/following-sibling::input'
)
RENTAL_HD_PERCEIVED_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="$"]/following-sibling::input'
)

# Rental Price - SD checkbox, price and perceived inputs
RENTAL_SD_CHECKBOX = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
RENTAL_SD_PRICE_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="$"]/following-sibling::input'
)
RENTAL_SD_PERCEIVED_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="$"]/following-sibling::input'
)

# Purchase Price - HD checkbox, price and perceived inputs
PURCHASE_HD_CHECKBOX = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
PURCHASE_HD_PRICE_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="$"]/following-sibling::input'
)
PURCHASE_HD_PERCEIVED_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="$"]/following-sibling::input'
)

# Purchase Price - SD checkbox, price and perceived inputs
PURCHASE_SD_CHECKBOX = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
PURCHASE_SD_PRICE_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="$"]/following-sibling::input'
)
PURCHASE_SD_PERCEIVED_INPUT = (
    By.XPATH,
    '//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[contains(@class,"flex items-center gap-3")]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="$"]/following-sibling::input'
)

# Country-specific pricing search and selection
COUNTRY_SEARCH_INPUT = (
    By.CSS_SELECTOR,
    'input[placeholder="Search countries for custom pricing..."]'
)
COUNTRY_CHECKBOX_INDIA = (
    By.XPATH,
    '//span[text()="India"]/preceding-sibling::button[@role="checkbox"]'
)

# India-specific pricing (INR) - selectors using rupee symbol ₹
# Rental Price - HD checkbox, price and perceived inputs
INDIA_RENTAL_HD_CHECKBOX = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
INDIA_RENTAL_HD_PRICE_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="₹"]/following-sibling::input'
)
INDIA_RENTAL_HD_PERCEIVED_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="₹"]/following-sibling::input'
)

# Rental Price - SD checkbox, price and perceived inputs
INDIA_RENTAL_SD_CHECKBOX = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
INDIA_RENTAL_SD_PRICE_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="₹"]/following-sibling::input'
)
INDIA_RENTAL_SD_PERCEIVED_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Rental Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="₹"]/following-sibling::input'
)

# Purchase Price - HD checkbox, price and perceived inputs
INDIA_PURCHASE_HD_CHECKBOX = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
INDIA_PURCHASE_HD_PRICE_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="₹"]/following-sibling::input'
)
INDIA_PURCHASE_HD_PERCEIVED_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="HD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="₹"]/following-sibling::input'
)

# Purchase Price - SD checkbox, price and perceived inputs
INDIA_PURCHASE_SD_CHECKBOX = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//button[@role="checkbox"]'
)
INDIA_PURCHASE_SD_PRICE_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Price"]/following-sibling::span[text()="₹"]/following-sibling::input'
)
INDIA_PURCHASE_SD_PERCEIVED_INPUT = (
    By.XPATH,
    '//span[text()="India"]/ancestor::div[contains(@class,"bg-white shadow-sm")]//h4[contains(normalize-space(.),"Purchase Price")]/ancestor::div[@class="space-y-4 pb-6"]//div[text()="SD"]/ancestor::div[contains(@class,"flex items-center gap-3")]//span[text()="Perceived"]/following-sibling::span[text()="₹"]/following-sibling::input'
)

# Specific Countries selection search
SPECIFIC_COUNTRIES_SEARCH_INPUT = (
    By.CSS_SELECTOR,
    'input[placeholder="Search countries..."]'
)

# Excluded Countries selection search (for "All Countries Except" option)
EXCLUDED_COUNTRIES_SEARCH_INPUT = (
    By.CSS_SELECTOR,
    'input[placeholder="Search countries to exclude..."]'
)
