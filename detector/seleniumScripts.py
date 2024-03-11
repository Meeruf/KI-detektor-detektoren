from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import time, re

"""
Functions that navigate the AI-detector's websites with the Python module Selenium. 
These functions can sometimes raise unexpected errors that is still not dealt with, that will require a manual restart by closing all the driver windows, and run the scan again.
Images that have already been scanned by all the detectors and been saved in the database,
will not be scanned again as the image files have been moved to another folder.
"""

def contentatscale(self, IMG_PATH, driver):
    """ Selenium script for Contentatscale.com. 
    
    Parameters
    ----------
    IMG_PATH : str
        Path of the image that will be scanned
    driver : obj
        Selenium Chrome driver.

    Returns
    -------
    result : str
        The result in percentage of how likely to be AI, 
        or 'TIMEOUT' if there is no response from the website within a set time.
    """
    time.sleep(3)
    WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.ID, 'content-from-image-file')))
    input_element = driver.find_element(By.ID, 'content-from-image-file')

    time.sleep(1)
    input_element.send_keys(IMG_PATH)

    time.sleep(1)
    submitBtn = driver.find_element(By.XPATH, "//button[contains(text(), 'Check for AI')]")
    driver.execute_script("arguments[0].click();", submitBtn)

    waiting_for_answer = True
    while waiting_for_answer:
        time.sleep(1)
        AIImageCard = driver.find_element(By.CLASS_NAME, 'ai-image-card')
        resultElement = AIImageCard.find_element(By.CLASS_NAME, 'ai-score')
        if re.search(r'\d', resultElement.text):
            waiting_for_answer = False
        else:
            pass
    ai_result = resultElement.text.replace('AI:', '').replace('%', '')

    driver.refresh()
    return ai_result

def hivemoderation(self, IMG_PATH, driver):
    """ Selenium script for hivemoderation.com. 
    
    Parameters
    ----------
    IMG_PATH : str
        Path of the image that will be scanned
    driver : obj
        Selenium Chrome driver.

    Returns
    -------
    result : str
        The result in percentage of how likely to be AI, 
        or 'TIMEOUT' if there is no response from the website within a set time.
    """
    time.sleep(3)
    WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.ID, 'hvaid-upload-input')))

    file_input = driver.find_element(By.ID, 'hvaid-upload-input')

    time.sleep(1)
    file_input.send_keys(IMG_PATH)
    
    try:
        agree_terms = driver.find_element(By.ID, 'hvaid-term-of-service-checkbox')
        agree_terms.click()
    except:
        pass

    time.sleep(1)
    checkBtn = driver.find_element(By.XPATH, "//button[contains(text(), 'Check Origin')]")
    checkBtn.click()

    try:
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, 'hvaid-results-percentage')))
    except TimeoutException:
        tryagainBtn = driver.find_element(By.ID, 'hvaid-try-again-button')
        tryagainBtn.click()
        
    try:
        WebDriverWait(driver, 70).until(EC.presence_of_element_located((By.ID, 'hvaid-results-percentage')))
        result = driver.find_element(By.ID, 'hvaid-results-percentage')
        result = str(result.text).replace('%', '')
        gobackBtn = driver.find_element(By.ID, 'hvaid-results-go-back-buttons-inner-container')
    except TimeoutException:
        print('REFRESH HIVEMODERATION')
        return 'TIMEOUT'
        
    time.sleep(1)
    gobackBtn.click()
    return result
      
def isitAI(self, IMG_PATH, driver):
    """ Selenium script for isitAI.com. 
    
    Parameters
    ----------
    IMG_PATH : str
        Path of the image that will be scanned
    driver : obj
        Selenium Chrome driver.

    Returns
    -------
    result : str
        The result in percentage of how likely to be AI, 
        or 'TIMEOUT' if there is no response from the website within a set time.
    """
    time.sleep(3)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'file-upload')))
    input_element = driver.find_element(By.ID, 'file-upload')
    input_element.send_keys(IMG_PATH)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'submit-button')))
    submitBtn = driver.find_element(By.ID, 'submit-button')
    submitBtn.click()

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'result-container')))
    except TimeoutException:
        print("Timeout isitAI.com")
        return 'TIMEOUT'
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#result-container .bar-fill.human')))
    except TimeoutException:
        print("Timeout isitAI.com")
        return 'TIMEOUT'
    
    result_container = driver.find_element(By.ID, 'result-container')
    ai_result = result_container.find_elements(By.CSS_SELECTOR, '.bar-fill.ai')

    for element in ai_result:
        ai_result = element.get_attribute('style').replace('width: ', '').replace(';', '').replace('%', '')
    driver.refresh()
    return ai_result
    
def illuminarty(self, IMG_PATH, driver):
    """ Selenium script for illuminarty.ai
    
    Parameters
    ----------
    IMG_PATH : str
        Path of the image that will be scanned
    driver : obj
        Selenium Chrome driver.

    Returns
    -------
    result : str
        The result in percentage of how likely to be AI, 
        or 'TIMEOUT' if there is no response from the website within a set time.
    """
    time.sleep(3)
    if self.firstClick:
        button = driver.find_element(By.XPATH, "//button[normalize-space(text())='Go to main page']")
        button.click()
        self.firstClick = False

    # Now, you can use the send_keys method to upload files
    file_input = driver.find_element(By.CSS_SELECTOR, 'input[type=file]')
    file_input.send_keys(IMG_PATH)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'outputImage')))
    except TimeoutException:
        print("Timeout illuminarty")
        return 'TIMEOUT'
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//p[contains(text(), 'AI Probability:')]")))
    except TimeoutException:
        print("Timeout illuminarty")
        return 'TIMEOUT'
    
    probability_element = driver.find_element(By.XPATH, "//p[contains(text(), 'AI Probability:')]")
    probability_text = probability_element.text
    ai_result = probability_text.replace('AI Probability: ', '').replace('%', '')
    return ai_result


def ChatGPT():
    from time import sleep
    op = webdriver.ChromeOptions()
    op.add_argument(f"user-agent={UserAgent.random}")
    op.add_argument("user-data-dir=./")
    op.add_experimental_option("detach", True)
    op.add_experimental_option("excludeSwitches", ["enable-logging"])

    prompt = 'What do you think, is the image AI or real?. Return a estimate on how likely the image is AI-generated as a percentage between 0 and 100%, with 0% being definitely not AI-generated and 100% being definitely AI-generated. Just the percentage, please, no extra info.'

    driver = uc.Chrome(chrome_options=op)

    MAIL = "thomasafure@gmail.com"
    PASSWORD = "!#djWo==d13"

    driver.get('google.com')
    driver.options.add_extension('/path/til/utvidelse.crx')
    driver.get('https://chat.openai.com/auth/login')

    
    wait = WebDriverWait(driver, 100)
    inputElement = wait.until(EC.presence_of_element_located((By.ID, "prompt-textarea")))

    script = "document.querySelector('input[type=\"file\"][multiple][tabindex=\"-1\"].hidden').classList.remove('hidden');"
    driver.execute_script(script)
    xpath = "//input[@type='file' and @multiple='' and @tabindex='-1' and contains(@class, 'hidden')]"
    fileInputElement = driver.find_element_by_xpath(xpath)

    print(1, inputElement)
    print(2, fileInputElement)

    sleep(10)

    inputElement = driver.find_elements(By.ID, "prompt-textarea")
    fileInputElement.sendkeys('/Users/fure/03Prosjekter/VSProjects/AIDetectors/detector/static/Bildebank/archive/AI/2.webp')

    i = 0
    # while i<10:
    inputElement[0].send_keys(prompt)
    sleep(2)
    inputElement[0].send_keys(Keys.ENTER)
    sleep(10)
    inputElement = driver.find_elements(By.TAG_NAME, "p")
    sleep(5)
    results = []

    for element in inputElement:
        results.append(element.text)
        print(results)
        i+=1
    
    sleep(5)

