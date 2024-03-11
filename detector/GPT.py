from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
import time

class GPTBot:
    def __init__(self):
        self.op = uc.ChromeOptions()
        self.op.add_argument(f"user-agent={UserAgent.random}")
        self.op.add_argument("user-data-dir=./")
        self.op.add_experimental_option("detach", True)
        self.op.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = uc.Chrome(chrome_options=self.op)
        self.driver.get('https://chat.openai.com/auth/login')

        def wait_for_specific_text(class_name, timeout=30):
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][multiple]')))
            except TimeoutException:
                print("Not found aaaaai")
                wait_for_specific_text(class_name, timeout)

        wait_for_specific_text(class_name='input[type="file"][multiple]', timeout=3)

        textarea = self.driver.find_element(By.ID, 'prompt-textarea')
        textarea.send_keys(
            """Kan du hjelpe meg med å se på noen bilder, og deretter gi meg et estimat i prosent om bildet er generert av kunstig intelligens? Bruk alt du har lært om hva som kan kjennetegne et kunstig bilde og hva som kan kjennetegne et ekte bilde. I denne sammenheng er et ekte bilde et hvilket som helst bilde som er tatt med et kamera, og som gjenspeiler den virkelige verden.
                Jeg ønsker å få svaret i prosent, selvom jeg forstår at det ikke er mulig å gi et svar som er helt riktig. Et estimat er bra nok, og du behøver ikke å gi noe utbroderende forklaring på hva du ser i bildet. Jeg ønsker i hovedsak kun et estimat. Bekreft at du kan gjøre dette, deretter vil jeg laste opp bildene jeg har.  """
        )
        time.sleep(.5)
        
        # Click send button
        self.driver.execute_script('document.querySelector(\'button[data-testid="send-button"]\').click();')
        
        input('Push enter to start the loop:')
        file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"][multiple]')

        run_loop = True
        index = 0
        while run_loop:
            loop_num = 5
            self.driver.refresh()
            file_input.send_keys('/Users/fure/03Prosjekter/VSProjects/AIDetectors/detector/static/Bildebank/archive/AI/1.webp')

            time.sleep(5)

            # Click send button
            self.driver.execute_script('document.querySelector(\'button[data-testid="send-button"]\').click();')
            

            WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"div[data-testid='conversation-turn-{loop_num}']")))

            input('::: Push enter to save result :::')
            resultelement = self.driver.find_element(By.CSS_SELECTOR, f"div[data-testid='conversation-turn-{loop_num}']")
            result = resultelement.find_element(By.CSS_SELECTOR, 'div[data-message-author-role="assistant"]')

            print(result.text)
            loop_num += 2
            index += 1
            
        

gpt = GPTBot()


