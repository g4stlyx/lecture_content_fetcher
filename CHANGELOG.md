# Changelog

## 2024 Update - 4th Year Features

### What's New

1. **Updated Lecture Structure**
   - Restructured `lectures4` dictionary to include course IDs
   - Now supports fetching resources directly from course pages
   - Added all 7 courses for 4th year

2. **Additional Resources Fetching**
   - NEW: `fetch_additional_resources()` function to scan course pages
   - Fetches document files (PDF, DOC, DOCX, PPT, etc.) from `mod/resource` links
   - Fetches external URLs (online lectures, YouTube links, etc.) from `mod/url` links
   - Downloads resource files to `lecture_name/additional_resources/` folder
   - Creates a `resources_summary.txt` file listing all resources with their URLs

3. **New Functions**
   - `fetch_resource_file()`: Downloads document resources from course pages
   - `fetch_url_resource()`: Extracts external URL links from course pages
   - Better error handling and filename extraction

4. **New Command Line Arguments**
   - `--resources`: Fetch only additional resources (skips folder downloads)
   - `--all`: Fetch everything (folders + additional resources)
   - Example: `py main.py --lecture "data_mining" --resources`

5. **Enhanced Output**
   - Creates `additional_resources` folder for each lecture
   - Generates summary file with all external links and downloaded documents
   - Better console output with visual separators

### Usage Examples

```bash
# Fetch only additional resources for data_mining
py main.py --lecture "data_mining" --resources

# Fetch everything for deep_learning (folders + resources)
py main.py --lecture "deep_learning" --all

# Fetch all additional resources for all lectures
py main.py --resources

# Traditional: fetch week 1-5 folders for data_mining
py main.py --lecture "data_mining" --week_range "1-5"
```

### Technical Changes

- Added `re` and `urllib.parse` imports for better URL parsing
- Updated data structure: `lectures4` now uses nested dictionaries with `course_id` and `folder_range`
- All existing functionality preserved (backward compatible)
- Better handling of Moodle's different resource types
