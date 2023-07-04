from googleapis import *
import undetected_chromedriver as uc
from urllib.parse import urlparse
import os
import sys
import parsel
import argparse
from presentation import Presentation
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import time
import atexit

PROFILE_PATH = None
PROFILE_NAME = 'instagram'

# Platform independent profile setting

if sys.platform == 'linux' or sys.platform == 'linux2':
    PROFILE_PATH = os.path.join('~/.config/google-chrome', PROFILE_NAME)
elif sys.platform == 'win32':
    PROFILE_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', PROFILE_NAME)
elif sys.platform == 'darwin':
    PROFILE_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome', PROFILE_NAME)

BASE_SLIDES_URL = "https://docs.google.com/presentation/d/[id]"

def google_sheets(driver: uc.Chrome, sheets_id: str, submission_title: str, image_count:int = 4):
    print("Initializing credentails...")
    creds = get_creds()
    print("Finished initializing credentials.")
    print("Getting instagram profiles with bold name from Google Sheets...")
    instagrams = get_rows_with_bold_name(creds, sheets_id)
    print(f"Found {len(instagrams)} instagram profiles with bold name")
    instagrams_with_images = []
    for ig in instagrams:
        print(f"Getting posts of {ig['name']} from instagram...")
        get_instagram_images(driver, ig, image_count)
        if len(ig['images']) > 0:
            instagrams_with_images.extend(divide_by_instagram_images(ig))
    if len(instagrams_with_images) == 0:
        print("There are images found.")
        print("DONE.")
        return None
    print("Copying Google Slides template...")
    presentation = Presentation.copy_presentation(creds, 'Instagram Photos Template', 'Instagram Photos')
    print("Finished copying Google Slides template.")
    print("Creating slides...")
    presentation.duplicate_slide('p', len(instagrams_with_images))
    presentation.apply_reqs()
    print("Finished creating slides.")
    print("Replacing slide placholders with instagram...")
    slides = presentation.get_all_slides()
    for i, ig in enumerate(instagrams_with_images):
        presentation.replace_shapes_with_instagram(slides[i]['objectId'], ig, submission_title)
    presentation.apply_reqs()
    print("DONE.")
    return BASE_SLIDES_URL.replace('[id]', presentation.presentation_id)

def clean_url(url: str):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)

    domain = parsed_url.netloc

    if domain.startswith('www.'):
        domain = domain[4:]

    cleaned_url = parsed_url.scheme + '://' + domain + parsed_url.path
    return cleaned_url    

def get_instagram_images(driver: uc.Chrome, instagram: dict, count: int):
    cleaned_url = clean_url(instagram['instagram_url'])
    try:
        driver.get(cleaned_url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='splash-screen'][contains(@style, 'display: none')]"))
        )
    except:
        pass
    selector = parsel.Selector(text=driver.page_source)
    image_urls = selector.xpath("//main//article//img/@src").getall()[0:count]
    instagram['images'] = image_urls

def divide_by_instagram_images(instagram: dict):
    instagrams = []
    image_urls = instagram['images']
    for i in range(0, len(image_urls), 2):
        chunk = image_urls[i:i+2]
        instagrams.append({
            'name': instagram['name'],
            'instagram_url': instagram['instagram_url'],
            'submission': instagram['submission'],
            'images': chunk
        })
    return instagrams


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--sheetid", type=str, dest='sheet_id', required=True)
    # parser.add_argument("--imagecount", type=int, default=2, dest='image_count')
    # parser.add_argument("--submissiontitle", type=str, default=None, dest='submission_title')
    # args = parser.parse_args()

    sheet_id = ''
    while not sheet_id:
        sheet_id = input("Enter sheet id:")
    submission_title = input("Enter submission title (Press ENTER if None):")
    image_count = ''
    while not image_count:
        image_count = input("Enter number of image per instagram account:")
        if image_count and image_count.isnumeric():
            image_count = int(image_count)
            if image_count > 0 and image_count % 2 == 0:
                image_count = int(image_count)
                continue
        image_count = ''

    print("Initializing selenium...")
    driver = uc.Chrome(user_data_dir=PROFILE_PATH, headless=True)
    driver.maximize_window()
    print("Selenium initialized.")
    try:
        presentation_url = google_sheets(driver, sheet_id, submission_title, image_count)
        print(f"Result: {presentation_url}")
    finally:
        driver.quit()
        input("Press ENTER to exit...")

