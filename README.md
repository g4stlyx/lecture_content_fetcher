# lecture_content_fetcher

It goes to arel uzem website, logs in, checks courses for downloadable lecture contents. if sees any new content, downloads them to the related folder.

**NEW:** Now supports fetching additional resources like:
- External URLs (online lecture links, YouTube videos, etc.)
- Document files (PDF, DOC, DOCX, PPT, etc.) from mod/resource
- Other resource types from course pages

## How To Use

1) install requirements: `pip install python-dotenv requests beautifulsoup4`

2) create a `.env` file containing these parameters: **AREL_UZEM_USERNAME** AND **AREL_UZEM_PASSWORD**

3) run the script:
    * with no arguments (all weeks and all lectures): `py main.py`
    * with lecture selected: `py main.py --lecture "data_mining"`
    * with week selected: `py main.py --week 3`
    * with week-range selected: `py main.py --week_range "1-3"`
    * with both week and lecture selected: `py main.py --lecture "deep_learning" --week 3`
    * **fetch only additional resources (URLs, docs, etc.)**: `py main.py --resources`
    * **fetch specific lecture's additional resources**: `py main.py --lecture "data_mining" --resources`
    * **fetch everything (folders + additional resources)**: `py main.py --all`