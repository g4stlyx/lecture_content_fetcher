# lecture_content_checker

It goes to arel uzem website, logs in, checks courses for downloadable lecture contents. if sees any new content, downloads them to the related folder.

TODO:
* check homeworks too if possible (maybe going to the course pages and check for new links)

## How To Use

1) install requirements: `pip install python-dotenv requests beautifulsoup4`

2) create a `.env` file containing these parameters: **AREL_UZEM_USERNAME** AND **AREL_UZEM_PASSWORD**

3) run the script:
    * with no arguments (all weeks and all lectures): `py main.py`
    * with lecture selected: `py main.py --lecture "system_analysis_and_design"`
    * with week selected: `py main.py --week 3`
    * with week-range selected: `py main.py --week_range "1-3"`
    * with both week and lecture selected: `py main.py --lecture "system_analysis_and_design" --week 3 `