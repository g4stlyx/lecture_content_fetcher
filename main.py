import os
import requests
from bs4 import BeautifulSoup
import time
from random import uniform
from dotenv import load_dotenv

load_dotenv()

lectures = {
    "system_programming": range(156565, 156575),
    "system_analysis_and_design": range(156514, 156558),
    "computer_network_and_security": range(155902, 155946),
    "computer_graphics": range(155953, 155997),
    "environmental_protection": range(208942, 208986),
    "professional_responsibilities_and_ethics": range(212257, 212301),
    "visual_based_programming": range(156616, 156660),
    "web_programming": range(156667, 156711),
}

USERNAME = os.getenv("AREL_UZEM_USERNAME")
PASSWORD = os.getenv("AREL_UZEM_PASSWORD")

LOGIN_URL = "https://uzem.arel.edu.tr/login/index.php"
BASE_URL = "https://uzem.arel.edu.tr" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

#! if extra "protection" is needed
# proxies = {
#     'http': 'http://your.proxy.server:port',
#     'https': 'http://your.proxy.server:port'
# }

def login(session, username, password):
    """Logs into the Arel UZEM system."""
    try:
        # 1. Get the login page to obtain the logintoken
        response = session.get(LOGIN_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        logintoken = soup.find('input', {'name': 'logintoken'})['value']

        # 2. Prepare the login data
        login_data = {
            'username': username,
            'password': password,
            'logintoken': logintoken
        }

        # 3. Send the login request
        response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
        response.raise_for_status()

        if "Giriş yapmadınız." not in response.text:  # Adjust this check
            print("Login successful!")
            return True
        else:
            print("Login failed.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Login error: {e}")
        return False

def check_and_download_files(session, lecture_name, folder_id):
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

    # Prepare the folder path but don't create it yet
    lecture_folder = os.path.join(lecture_name, f"folder_{folder_id}")
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

if __name__ == "__main__":
    # Create a session to persist cookies across requests
    with requests.Session() as session:
        # Log in
        if login(session, USERNAME, PASSWORD):
            # Loop through lectures and folders after successful login
            for lecture_name, folder_range in lectures.items():
                for folder_id in folder_range:
                    check_and_download_files(session, lecture_name, folder_id)
                    time.sleep(uniform(1, 3))
        else:
            print("Login failed.  Exiting.")