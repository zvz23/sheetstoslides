import undetected_chromedriver as uc
import os
import sys

PROFILE_PATH = None
PROFILE_NAME = 'instagram'

# Platform independent profile setting

if sys.platform == 'linux' or sys.platform == 'linux2':
    PROFILE_PATH = os.path.join('~/.config/google-chrome', PROFILE_NAME)
elif sys.platform == 'win32':
    PROFILE_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', PROFILE_NAME)
elif sys.platform == 'darwin':
    PROFILE_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome', PROFILE_NAME)


def create_driver(headless=True):
    return uc.Chrome(user_data_dir=PROFILE_PATH, headless=headless)


def login():
    driver = create_driver(headless=False)
    driver.get("https://www.instagram.com/accounts/login/")
    input("Press ENTER if you have logged in...")
    driver.quit()
