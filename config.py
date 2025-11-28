# config.py
# Folder (relative to project root) where you store all metadata sheets
EXCEL_DIR = r"excel meta data sheets"

# Default sheet to use if you just press ENTER at the prompt.
# Put the file in EXCEL_DIR and set only the file name here.
# Example for Excel: EXCEL_PATH = "my_projects.xlsx"
# Example for CSV:   EXCEL_PATH = "my_projects.csv"
EXCEL_PATH = "qn7h-dcrh_hundreds_of_beavers_metadata.csv"
IMDB_COL = "IMDb Link"
SYNOPSIS_COL = "Movie/Show Synopsis"
TAGS_COL = "Tag(s)"
TRAILER_KEY_COL = "Trailer Filename"     # exact column name in your sheet
# New: column that indicates availability types (must contain 'tvod' to create a project)
AVAIL_TYPE_COL = "Avail Type(s)"
START_URL = "https://filmmakers.brew.tv/dashboard/filmmaker/create-new-project?mode=create"  # starting create page
WAIT_TIMEOUT = 20
HEADLESS = False  # keep False to watch the browser in real-time
