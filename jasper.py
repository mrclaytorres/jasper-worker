# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import pandas as pd
import datetime
import sys
import os
import os.path
import time
import csv
import re
import creds

def user_agent():
    user_agent_list = []
    with open('user_agents.csv', 'r') as f:
        for agents in f:
            user_agent_list.append(agents)
    return user_agent_list

def work_jasper():
    time_start = datetime.datetime.now().replace(microsecond=0)
    directory = os.path.dirname(os.path.realpath(__file__))

    user_agents = user_agent()

    # Setup random proxy and user-agent
    random_user_agents = random.randint(1, len(user_agents) - 1)
    print(user_agents[random_user_agents])
    options = {
        'user-agent': user_agents[random_user_agents],
        'suppress_connection_errors': True,
        'verify_ssl': True
    }

    # chrome_options = Options()
    # # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--log-level=0")
    # prefs = {
    #     "profile.default_content_settings.popups": 0,
    #     "download.default_directory" : r"D:\Work\UpDigital\financestrategist\erisapedia\csvfiles",
    #     "directory_upgrade": True}
    # chrome_options.add_experimental_option("prefs", prefs)

    options = {
        'user-agent': user_agents[random_user_agents]
        # 'suppress_connection_errors': True
    }

    # browser = webdriver.Chrome(executable_path=r"D:\Work\UpDigital\financestrategist\erisapedia\chromedriver.exe", options=chrome_options)
    driver_path = os.path.join(directory,'chromedriver.exe')
    browser = webdriver.Chrome(executable_path=driver_path, seleniumwire_options=options)

    browser.set_window_size(1920, 1080)

    composed_list = []
    prompt_list = []

    browser.get('https://app.jasper.ai/')
    uname = browser.find_element(By.ID, "email")
    # upass = browser.find_element(By.XPATH, '//*[@id="login_info"]/p[2]/input')

    uname.send_keys(creds.USERNAME)
    # upass.send_keys(creds.PASSWORD)

    # Click Recaptcha
    # WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
    # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-anchor"]'))).click()
    
    # browser.switch_to.default_content()

    time.sleep(2)

    uname.submit()

    time.sleep(10)

    signincode = browser.find_element(By.ID, "signInCode")
    time.sleep(10)
    signincode.submit()
    time.sleep(5)

    templates_button = browser.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/button[2]')
    templates_button.click()
    WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/button[2]'))).click()
    time.sleep(1)

    # documents_button = browser.find_element(By.XPATH, '//*[@id="list"]/div[2]/button[1]')
    # documents_button.click()
    WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="list"]/div[2]/button[1]'))).click()
    time.sleep(1)

    # startfromscratch = browser.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div[5]/div/div/div/div/ul/li[1]/div')
    # startfromscratch.click()
    WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div[5]/div/div/div/div/ul/li[1]/div'))).click()
    time.sleep(1)

    # L_button = browser.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[5]/div/div[1]/div[2]/div[2]/button[3]')
    # L_button.click()
    WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[5]/div/div[1]/div[2]/div[2]/button[3]'))).click()
    time.sleep(1)

    with open('query.csv') as f:
        reader = csv.DictReader(f)

        # rows = list(reader)
        # totalrow = len(rows)
        # print(f"rows - {totalrow}")

        for line in reader:

            # if totalrow == 1:
            #     query_filename = line['query']
            #     print(f"row - {query_filename}")

            prompt = line['prompt']

            try:
                
                # input_editor = browser.find_element(By.CLASS_NAME, 'ql-editor')
                input_editor = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'ql-editor')))
                input_editor.clear()
                time.sleep(2)
                input_editor.send_keys(prompt)
                time.sleep(2)
                
                # Highlight the command and perform
                actions = ActionChains(browser)
                input_editor.send_keys(Keys.CONTROL, "a")
                actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()

                # compose = browser.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[5]/div/div[2]/div/div/button')
                # compose.click()
                time.sleep(10)

                composed_prompt = browser.find_element(By.CLASS_NAME, 'ql-editor')
                composed_list.append(composed_prompt.text)
                print(f'{composed_prompt.text}\n')
                prompt_list.append(prompt)
                time.sleep(2)

            except:
                pass

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start
    print(f"Script runtime: {runtime}.\n")

    # Save scraped URLs to a CSV file
    now = datetime.datetime.now().strftime('%Y%m%d-%Hh%M')
    print('Saving to a CSV file...\n')
    data = {"Prompt": prompt_list,"Composed": composed_list}
    df=pd.DataFrame(data=data)
    df.index+=1

    filename = "jasper_composed" + now + ".csv"

    # filename = "prospects_" + now + ".csv"

    print(f'{filename} saved sucessfully.\n')

    file_path = os.path.join(directory,'csvfiles/', filename)
    df.to_csv(file_path)

    browser.quit()

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start
    print(f"Script runtime: {runtime}.\n")

if __name__ == '__main__':
    work_jasper()