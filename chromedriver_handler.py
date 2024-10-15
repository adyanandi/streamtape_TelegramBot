import os
import platform
import subprocess
import requests
from zipfile import ZipFile
import time
import shutil

# Function to get Chrome version
def get_chrome_version():
    try:
        if platform.system() == 'Windows':
            process = subprocess.Popen(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version', 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL, 
                text=True)
            version_info, _ = process.communicate()
            version = version_info.strip().split()[-1]
        elif platform.system() == 'Darwin':  # macOS
            process = subprocess.Popen(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            version = process.communicate()[0].decode("UTF-8").strip().split()[-1]
        else:  # Linux
            process = subprocess.Popen(
                ["google-chrome", "--version"], stdout=subprocess.PIPE)
            version = process.communicate()[0].decode("UTF-8").strip().split()[-1]
        
        return version
    except Exception as e:
        print(f"Error fetching Chrome version: {e}")
        return None

# Function to detect platform architecture
def get_platform_architecture():
    system = platform.system()
    architecture = platform.machine()
    if system == 'Linux':
        return 'linux64'
    elif system == 'Darwin':
        if architecture == 'arm64':
            return 'mac-arm64'
        return 'mac-x64'
    elif system == 'Windows':
        if architecture.endswith('64'):
            return 'win64'
        return 'win32'
    return None

# Function to download ChromeDriver with retries
def download_chromedriver(chrome_version, platform_arch):
    # Mapping URLs for Chrome version >= 115
    base_url = "https://storage.googleapis.com/chrome-for-testing-public/"
    if int(chrome_version.split('.')[0]) >= 115:
        driver_version = chrome_version
        driver_url = f"{base_url}{driver_version}/{platform_arch}/chromedriver-{platform_arch}.zip"
    else:
        # Older versions logic (you can add conditions or more URLs here)
        driver_url = f"https://chromedriver.storage.googleapis.com/{chrome_version}/chromedriver_{platform_arch}.zip"
    
    driver_dir = 'driver/'
    if not os.path.exists(driver_dir):
        os.makedirs(driver_dir)
    
    driver_path = os.path.join(driver_dir, f'chromedriver_{platform_arch}.zip')
    
    # Path to the ChromeDriver binary (after extraction)
    binary_name = 'chromedriver.exe' if platform.system() == 'Windows' else 'chromedriver'
    binary_path = os.path.join(driver_dir, binary_name)

    # Skip download if the binary already exists
    if os.path.exists(binary_path):
        print(f"ChromeDriver binary already exists at {binary_path}. Skipping download.")
        return

    # Retry logic
    retries = 3
    for attempt in range(retries):
        try:
            print(f"Attempting to download ChromeDriver (Attempt {attempt + 1})")
            response = requests.get(driver_url, timeout=10)  # Added timeout for safety
            if response.status_code == 200:
                with open(driver_path, 'wb') as file:
                    file.write(response.content)
                print(f"Extracting {driver_path}...")
                with ZipFile(driver_path, 'r') as zip_ref:
                    zip_ref.extractall(driver_dir)
                
                # Move the binary to the driver folder (if extracted to a subfolder)
                extracted_folder = os.path.join(driver_dir, f"chromedriver-{platform_arch}")
                extracted_binary = os.path.join(extracted_folder, binary_name)
                if os.path.exists(extracted_binary):
                    shutil.move(extracted_binary, binary_path)
                    shutil.rmtree(extracted_folder)  # Delete extracted contents
                print(f"ChromeDriver downloaded and placed at {binary_path}")

                # Delete the zip file
                os.remove(driver_path)
                print(f"Deleted the ChromeDriver zip file at {driver_path}")
                break  # Break out of loop if download succeeds
            else:
                print(f"Failed to download ChromeDriver: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error during download: {e}")
            if attempt < retries - 1:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Max retries reached. Failed to download ChromeDriver.")
                raise

# Main function to handle logic
def setup_chromedriver():
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Could not determine Chrome version.")
        return
    
    platform_arch = get_platform_architecture()
    if not platform_arch:
        print("Could not determine platform architecture.")
        return
    
    download_chromedriver(chrome_version, platform_arch)

# If this script is run as the main script, execute setup
if __name__ == "__main__":
    setup_chromedriver()
