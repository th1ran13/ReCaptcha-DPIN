import os
import re
import sys
import time
import urllib.request

import urllib3
import requests
from datetime import datetime

import whisper
from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Initialize the WebDriver with the ChromeService
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

url = 'https://www.google.com/recaptcha/api2/demo'
driver.get(url)

model = whisper.load_model("base")


def transcribe(urlAudio):
    with open('.temp', 'wb') as f:
        f.write(requests.get(urlAudio).content)
    result = model.transcribe('.temp')
    return result["text"].strip()


# Wait for the iframe to be available and switch to it
def delay(waiting_time=5):
    driver.implicitly_wait(waiting_time)


while True:
    try:
        delay()
        frames = driver.find_elements(By.TAG_NAME, 'iframe')
        recaptcha_control_frame = None
        recaptcha_challenge_frame = None
        for index, frame in enumerate(frames):
            if re.search('reCAPTCHA', frame.get_attribute("title")):
                recaptcha_control_frame = frame
            if re.search('recaptcha challenge', frame.get_attribute("title")):
                recaptcha_challenge_frame = frame

        if not (recaptcha_control_frame and recaptcha_challenge_frame):
            print("[ERR] Unable to find recaptcha. Abort solver.")
            sys.exit()

        delay()

        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(recaptcha_control_frame)
        driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()

        delay()

        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(recaptcha_challenge_frame)
        
        # click on audio challenge
        time.sleep(10)
        driver.find_element(By.ID, "recaptcha-audio-button").click()
        
        text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
        driver.find_element(By.ID, "audio-response").send_keys(text)
        driver.find_element(By.ID, "recaptcha-verify-button").click()

    except:
        # if ip is blocked.. renew tor ip
        print("[INFO] IP address has been blocked for recaptcha.")
        sys.exit()
