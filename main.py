import os
import requests
from bs4 import BeautifulSoup
import time
from random import uniform
from dotenv import load_dotenv
import argparse
import re
from urllib.parse import urlparse, parse_qs

load_dotenv()

lectures3 = {
    "system_programming": range(156565, 156609),
    "system_analysis_and_design": range(156514, 156558),
    "computer_network_and_security": range(155902, 155946),
    "computer_graphics": range(155953, 155997),
    "visual_based_programming": range(156616, 156660),
    "web_programming": range(156667, 156711),
    "environmental_protection": range(208942, 208986),
    "professional_responsibilities_and_ethics": range(212257, 212301)
}

lectures4 = {
    "automata": {
        "course_id": 10239,
        "folder_range": range(567683, 567727)
    },
    "informatics": {
        "course_id": 10251,
        "folder_range": range(568319, 568363)
    },
    "data_science": {
        "course_id": 10231,
        "folder_range": range(567259, 567303)
    },
    "data_mining": {
        "course_id": 10252,
        "folder_range": range(568376, 568460)
    },
    "deep_learning": {
        "course_id": 10340,
        "folder_range": range(573036, 573080)
    },
    "interdisciplinary1": {
        "course_id": 10249,
        "folder_range": range(568213, 568257)
    },
    "interdisciplinary2": {
        "course_id": 10746,
        "folder_range": range(2026864, 2026908)
    }
}

USERNAME = os.getenv("AREL_UZEM_USERNAME")
PASSWORD = os.getenv("AREL_UZEM_PASSWORD")

LOGIN_URL = "https://uzem.arel.edu.tr/auth/prolizws/login_proliz.php"
BASE_URL = "https://uzem.arel.edu.tr"
OUTPUT_FOLDER = "output"  # Base folder for all downloaded content 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

#! if extra "protection" is needed
# proxies = {
#     'http': 'http://your.proxy.server:port',
#     'https': 'http://your.proxy.server:port'
# }

def login(session, username, password):
    """Logs into the Arel UZEM system using Proliz authentication."""
    try:
        # 1. Get the login page to obtain the sesskey
        response = session.get(LOGIN_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the sesskey (new authentication system uses sesskey instead of logintoken)
        sesskey_input = soup.find('input', {'name': 'sesskey'})
        if not sesskey_input:
            print("Error: Could not find sesskey on the page.")
            print("The website structure might have changed.")
            return False
        
        sesskey = sesskey_input['value']

        # 2. Prepare the login data (using prolizid and password fields)
        login_data = {
            'prolizid': username,
            'password': password,
            'sesskey': sesskey,
            'submitbtn': '1'
        }

        # 3. Send the login request
        response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
        response.raise_for_status()

        # Check for successful login
        # If login is successful, we should be redirected to /my or similar page
        if "prolizid" not in response.text and ("Dashboard" in response.text or "Kontrol Paneli" in response.text or "/my" in response.url):
            print("Login successful!")
            return True
        else:
            print("Login failed. Please check your credentials.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Login error: {e}")
        return False

def check_and_download_files(session, lecture_name, folder_id, week=None):
    """Checks for and downloads files from the specified folder."""
    url = f"https://uzem.arel.edu.tr/mod/folder/view.php?id={folder_id}"
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access folder {folder_id}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Simplified selector: Look for any link with forcedownload
    file_links = soup.find_all('a', href=lambda href: href and "forcedownload=1" in href)

    if not file_links:
        print(f"No files found in {lecture_name} (Folder {folder_id}) using simplified selector")
        return

    # Prepare the folder path
    if week:
        lecture_folder = os.path.join(OUTPUT_FOLDER, lecture_name, f"week_{week}", f"folder_{folder_id}")
    else:
        lecture_folder = os.path.join(OUTPUT_FOLDER, lecture_name, "all_weeks", f"folder_{folder_id}") # all weeks folder

    new_files = []

    for link in file_links:
        file_url = link['href']
        # Ensure the URL is absolute
        if not file_url.startswith('http'):
            file_url = BASE_URL + file_url
        filename = link.text.strip()

        # Check if the file already exists locally
        file_path = os.path.join(lecture_folder, filename)
        if os.path.exists(file_path):
            print(f"File already exists: {filename}")
            continue

        # Create the folder only if there's a file to download
        if not os.path.exists(lecture_folder):
            os.makedirs(lecture_folder)

        # Download the file
        download_file(session, file_url, file_path)  # Pass session to download_file
        new_files.append(filename)

    # Notify if new files are found
    if new_files:
        print(f"New files downloaded in {lecture_name} (Folder {folder_id}):")
        for filename in new_files:
            print(f"- {filename}")
    else:
        print(f"No new files in {lecture_name} (Folder {folder_id})")


def fetch_additional_resources(session, lecture_name, course_id):
    """Fetches additional resources like URLs, documents, etc. from the course page."""
    course_url = f"https://uzem.arel.edu.tr/course/view.php?id={course_id}"
    print(f"\nFetching additional resources for {lecture_name} (Course ID: {course_id})...")
    
    try:
        response = session.get(course_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access course page {course_id}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Create resources folder
    resources_folder = os.path.join(OUTPUT_FOLDER, lecture_name, "additional_resources")
    
    # Find all activity links (mod/resource, mod/url, etc.)
    activity_links = soup.find_all('a', href=lambda href: href and '/mod/' in href)
    
    resources_found = []
    urls_found = []
    
    for link in activity_links:
        href = link['href']
        
        # Handle mod/resource (documents, PDFs, etc.)
        if '/mod/resource/view.php' in href:
            resource_id = parse_qs(urlparse(href).query).get('id', [None])[0]
            if resource_id:
                resource_info = fetch_resource_file(session, lecture_name, resource_id, resources_folder, link)
                if resource_info:
                    resources_found.append(resource_info)
        
        # Handle mod/url (external links)
        elif '/mod/url/view.php' in href:
            url_id = parse_qs(urlparse(href).query).get('id', [None])[0]
            if url_id:
                url_info = fetch_url_resource(session, lecture_name, url_id, resources_folder, link)
                if url_info:
                    urls_found.append(url_info)
    
    # Save summary of resources
    if resources_found or urls_found:
        if not os.path.exists(resources_folder):
            os.makedirs(resources_folder)
        
        summary_path = os.path.join(resources_folder, "resources_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Additional Resources for {lecture_name}\n")
            f.write("=" * 50 + "\n\n")
            
            if resources_found:
                f.write("DOCUMENTS/FILES:\n")
                f.write("-" * 50 + "\n")
                for resource in resources_found:
                    f.write(f"Name: {resource['name']}\n")
                    f.write(f"File: {resource['filename']}\n")
                    f.write(f"Resource ID: {resource['id']}\n\n")
            
            if urls_found:
                f.write("\nEXTERNAL LINKS:\n")
                f.write("-" * 50 + "\n")
                for url_info in urls_found:
                    f.write(f"Name: {url_info['name']}\n")
                    f.write(f"URL: {url_info['url']}\n")
                    f.write(f"Resource ID: {url_info['id']}\n\n")
        
        print(f"\n✓ Found {len(resources_found)} documents and {len(urls_found)} external links")
        print(f"  Summary saved to: {summary_path}")
    else:
        print(f"No additional resources found for {lecture_name}")


def fetch_resource_file(session, lecture_name, resource_id, base_folder, link_element):
    """Fetches and downloads a resource file (doc, pdf, etc.)."""
    resource_url = f"https://uzem.arel.edu.tr/mod/resource/view.php?id={resource_id}"
    
    try:
        response = session.get(resource_url, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Try to get filename from Content-Disposition header
        filename = None
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            filename_match = re.findall(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disp)
            if filename_match:
                filename = filename_match[0][0].strip('"\'')
        
        # If no filename from header, try to get from the page or link text
        if not filename:
            soup = BeautifulSoup(response.text, 'html.parser')
            download_link = soup.find('a', href=lambda href: href and 'forcedownload=1' in href)
            if download_link:
                filename = download_link.text.strip()
            else:
                # Use link text as fallback
                filename = link_element.text.strip()
                # Clean filename
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                if not any(filename.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.zip']):
                    filename += '.file'
        
        if filename:
            if not os.path.exists(base_folder):
                os.makedirs(base_folder)
            
            file_path = os.path.join(base_folder, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                print(f"  Resource already exists: {filename}")
                return None
            
            # Download the actual file
            download_link = soup.find('a', href=lambda href: href and 'forcedownload=1' in href)
            if download_link:
                download_url = download_link['href']
                if not download_url.startswith('http'):
                    download_url = BASE_URL + download_url
                
                download_file(session, download_url, file_path)
                print(f"  ✓ Downloaded resource: {filename}")
                
                return {
                    'name': link_element.text.strip(),
                    'filename': filename,
                    'id': resource_id
                }
        
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching resource {resource_id}: {e}")
    
    return None


def fetch_url_resource(session, lecture_name, url_id, base_folder, link_element):
    """Fetches external URL resources and saves the link information."""
    resource_url = f"https://uzem.arel.edu.tr/mod/url/view.php?id={url_id}"
    
    try:
        response = session.get(resource_url, headers=headers, allow_redirects=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the external URL
        external_link = None
        
        # Look for the workaround link
        workaround_div = soup.find('div', class_='urlworkaround')
        if workaround_div:
            link = workaround_div.find('a')
            if link:
                external_link = link.get('href')
        
        # Alternative: look for meta refresh redirect
        if not external_link:
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh:
                content = meta_refresh.get('content', '')
                url_match = re.search(r'url=(.*)', content)
                if url_match:
                    external_link = url_match.group(1)
        
        if external_link:
            resource_name = link_element.text.strip()
            print(f"  ✓ Found external link: {resource_name}")
            print(f"    URL: {external_link}")
            
            return {
                'name': resource_name,
                'url': external_link,
                'id': url_id
            }
        
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching URL resource {url_id}: {e}")
    
    return None


def download_file(session, url, file_path):  # Take session as argument
    """Downloads a file using the authenticated session."""
    print(f"Downloading: {file_path}")
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download files from Arel UZEM.")
    parser.add_argument("--lecture", help="Specify the lecture to download (e.g., data_mining)")
    parser.add_argument("--week", type=int, help="Specify the week to download (e.g., 3)")
    parser.add_argument("--week_range", help="Specify a week range to download (e.g., 1-5)")
    parser.add_argument("--resources", action="store_true", help="Fetch additional resources (URLs, docs, etc.)")
    parser.add_argument("--all", action="store_true", help="Fetch all content including additional resources")
    args = parser.parse_args()

    # Ensure that the username and password are set
    if not USERNAME or not PASSWORD:
        print("Error: AREL_UZEM_USERNAME and AREL_UZEM_PASSWORD environment variables must be set in .env file.")
        exit()

    # Create a session to persist cookies across requests
    with requests.Session() as session:
        # Log in
        if login(session, USERNAME, PASSWORD):
            # Determine which lectures and folders to process
            if args.lecture:
                if args.lecture in lectures4:
                    selected_lectures = {args.lecture: lectures4[args.lecture]}
                else:
                    print(f"Error: Lecture '{args.lecture}' not found in the list.")
                    exit()
            else:
                selected_lectures = lectures4

            # Process lectures and folders
            for lecture_name, lecture_info in selected_lectures.items():
                folder_range = lecture_info["folder_range"]
                course_id = lecture_info["course_id"]
                
                print(f"\n{'='*60}")
                print(f"Processing: {lecture_name.upper()}")
                print(f"{'='*60}")
                
                # Fetch additional resources if requested
                if args.resources or args.all:
                    fetch_additional_resources(session, lecture_name, course_id)
                
                # Skip folder processing if only resources are requested
                if args.resources and not args.all:
                    continue
                
                # Week range logic
                if args.week_range:
                    try:
                        start_week, end_week = map(int, args.week_range.split('-'))
                        if start_week > end_week or start_week < 1:
                            raise ValueError("Invalid week range.")
                    except ValueError:
                        print("Error: Invalid week range format. Use 'start-end'.")
                        continue

                    for week in range(start_week, end_week + 1):
                        start_folder = folder_range.start + (week - 1) * 3  # Adjust starting folder based on week
                        end_folder = start_folder + 3

                        week_folders = range(start_folder, min(end_folder, folder_range.stop)) # end folder should not exceed the folder_range.stop
                        if not week_folders:
                            print(f"Week {week} is out of range for lecture {lecture_name}")
                            continue

                        for folder_id in week_folders:
                            check_and_download_files(session, lecture_name, folder_id, week)
                            time.sleep(uniform(1, 3))

                # Single week logic
                elif args.week:
                    start_folder = folder_range.start + (args.week - 1) * 3  # Adjust starting folder based on week
                    end_folder = start_folder + 3

                    week_folders = range(start_folder, min(end_folder, folder_range.stop)) # end folder should not exceed the folder_range.stop
                    if not week_folders:
                        print(f"Week {args.week} is out of range for lecture {lecture_name}")
                        continue  # skip this lecture/week combination

                    for folder_id in week_folders:
                        check_and_download_files(session, lecture_name, folder_id, args.week)
                        time.sleep(uniform(1, 3))

                # No week specified, process all folders
                else:
                    for folder_id in folder_range:
                        check_and_download_files(session, lecture_name, folder_id)
                        time.sleep(uniform(1, 3))

        else:
            print("Login failed.  Exiting.")

if __name__ == "__main__":
    main()