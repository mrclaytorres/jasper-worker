#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from curses import raw
from genericpath import isfile
import os
import sys
import random
import datetime
import time
import json
import glob
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from itertools import islice
from random import randint

class Logger():
    def __init__(self, group_id=0, prompt_id=0, max_group_id=0, max_prompt_id=0) -> None:
        self.__group_id = group_id
        self.__prompt_id = prompt_id
        self.__max_group_id = max_group_id
        self.__max_prompt_id = max_prompt_id

    def print_full(self, message: str, include_prompt_id=True) -> None:
        print(f':: Group [{ self.__group_id }/{ self.__max_group_id }] ' + (f'| Prompt [{ self.__prompt_id } / { self.__max_prompt_id }] ' if include_prompt_id else '') + f': { message }')

    def print_limited(self, message: str) -> None:
        print(f':: { message }')

    def increment_prompt_id(self) -> None:
        self.__prompt_id += 1

    def increment_group_id(self) -> None:
        self.__group_id += 1

def checkfiles():
    g_version = Path('VERSION').read_text()
    g_required_files = [
        'chromedriver',
        'creds.json',
        'query.json',
        'ua.json'
    ]

    print(f'Welcome to Jasper Worker ({ g_version })')
    print("Starting checks")

    for rf in g_required_files:
        if not os.path.isfile(rf):
            print(f"E: File '{ rf }' couldn't be found, aborting.")
            sys.exit(1)

        print(f":: File '{ rf }' was found, proceeding...")

    print('\n:: All OK.\n')

def get_random_user_agent():
    with open('ua.json', 'r', encoding='utf8') as fp_ua:
        return random.choice(json.load(fp_ua))

def login_jasper():
    logger = Logger()

    chrome_options = webdriver.ChromeOptions()

    ua = get_random_user_agent()
    logger.print_limited(f'UA = { ua }')

    chrome_options.add_argument(f'user-agent={ ua }')
    chrome_options.add_argument('user-data-dir=./chrome-prefs')

    driver_path = glob.glob('./chromedriver*')[0]

    logger.print_limited('Starting webdriver...')
    browser_handle = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    screen_x = random.randint(1280, 1920)
    screen_y = random.randint(720, 1080)

    logger.print_limited(f'Window size : { screen_x } x { screen_y }')
    browser_handle.set_window_size(screen_x, screen_y)

    logger.print_limited('Connecting...')
    browser_handle.get('https://app.jasper.ai/')

    try:
        logger.print_limited('Checking for a login form...')
        WebDriverWait(browser_handle, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div[3]/div/form/div[1]/div/input')))
    except:
        # Assume we're already logged-in
        logger.print_limited('webdriver is already logged-in.')
        return

    with open('creds.json', 'r', encoding='utf8') as creds_fp:
        logger.print_limited('Submitting username keys...\n')
        username_value = json.load(creds_fp)['username']
        username_field = browser_handle.find_element(By.ID, 'email')
        username_field.clear()
        username_field.send_keys(username_value)
        username_field.submit()

        # User will now manually log-in
        # So we'll wait 10 minutes 'till we have a dashboard available
        logger.print_limited(f'Please enter the code sent at { username_value } - waiting 10 minutes for you to manually enter it.\n')
        WebDriverWait(browser_handle, 600).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div/nav[1]/ul[3]/li/span/a')))

    logger.print_limited('Found Jasper.ai dashboard')
    logger.print_limited('Closing window.\n')
    browser_handle.close()

def run_prompts(prompts_list: list, group_id: int, max_group_id: int) -> list:
    # Initialize a new browser window
    # Assume we're already logged-in

    print(f'\nStarting run_prompts\n')
    print(f':: Prompts to generate : { len(prompts_list) }')

    print(f':: Initializing webdriver...')
    chrome_options = webdriver.ChromeOptions()

    ua = get_random_user_agent()
    print(f':: UA = { ua }')

    chrome_options.add_argument(f'user-agent={ ua }')
    chrome_options.add_argument('user-data-dir=./chrome-prefs')

    driver_path = glob.glob('./chromedriver*')[0]

    print(f':: Starting webdriver...')
    browser_handle = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    screen_x = random.randint(1280, 1920)
    screen_y = random.randint(720, 1080)

    print(f':: Window size : { screen_x } x { screen_y }')
    browser_handle.set_window_size(screen_x, screen_y)

    print(f':: Connecting...')
    browser_handle.get('https://app.jasper.ai/docs/new')
    time.sleep(3)

    print(f':: Entering edit page...')

    try_count = 0

    while True:

        if try_count == 5:
            print(f'** E: Aborting script. Too many failed attempts to enter ql-editor !')
            sys.exit(1)

        try:
            print(f':: Trying to enter ql-editor...')

            WebDriverWait(browser_handle, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[3]/article/div/div[2]/button'))).click()
            time.sleep(5)

            break

        except:
            print(f'** W: Failed to enter ql-editor ! (attempt { try_count })')
            print('** W: Re-connecting...')
            browser_handle.get('https://app.jasper.ai/docs/new')
            time.sleep(30)

            try_count += 1
            continue

    composed_list = []

    print(':: Loading raw output file in memory... (if available)')

    output_present = os.path.isfile('./output/composed.csv')

    for (idx, prompt_line) in enumerate(prompts_list):
        force_skip = False

        if output_present == True:
            with open('./output/composed.csv', 'r', encoding='utf8') as fp_generated:
                raw_generated = csv.reader(fp_generated, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

                for raw_line in raw_generated:
                    if ((prompt_line in raw_line[0]) and (raw_line[1] != "LINE_SKIPPED")):
                        # Prompt already generated
                        force_skip = True
                        break

        if force_skip == True:
            print(f'** Skipping already generated line at idx { idx+1 }')
            continue

        logger = Logger(group_id, idx+1, max_group_id, len(prompts_list))

        try_count = 0

        while True:
            if try_count == 20:
                print('** E: Aborting script. Too many failed attempts to clear ql-editor ! (Check internet connection ?)')
                sys.exit(1)

            try:
                logger.print_full('Clearing ql-editor...')
                input_editor = WebDriverWait(browser_handle, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ql-editor')))
                time.sleep(6)
                input_editor.clear()
                break

            except:
                print(f'** W: Failed to clear ql-editor ! (attempt { try_count })')
                try_count += 1
                continue

        time.sleep(2)
        logger.print_full('Sending prompt keys...')
        input_editor.send_keys(prompt_line)
        time.sleep(2)

        logger.print_full('Highlighting the prompt and generating...')
        actions = ActionChains(browser_handle)

        actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()

        logger.print_full('Waiting for Jasper to finish...')

        try_count = 0
        skip_prompt = False

        composed_prompt = ""

        while True:
            if try_count == 12:
                # Check if the editor is stuck on loading / waiting

                try:
                    WebDriverWait(browser_handle, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div/div[1]/div[4]/div/div[2]/div/div/button/div[3]')))

                    # Skip prompt
                    print(f'** W: Too many failed attempts to find composed prompt ! (paragraph 3 not found after { try_count } attempts)')
                    print('** W: Skipping this prompt - perhaps this input contains sensitive material ?')

                    skip_prompt = True
                    break

                except:
                    # We'll need to refresh
                    print('** W: Editor not stuck, skipping line.')
                    skip_prompt = True

                    # Re-establish a connection
                    print('** W: Editor may be stuck.')
                    print('** W: Loader still present on page - re-establishing connection...')
                    browser_handle.refresh()

                    while True:
                        if try_count == 20:
                            print('** E: Aborting script. Too many failed attempts to clear ql-editor ! (Check internet connection ?)')
                            sys.exit(1)

                        try:
                            logger.print_full('Clearing ql-editor...')
                            input_editor = WebDriverWait(browser_handle, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ql-editor')))
                            time.sleep(6)
                            input_editor.clear()
                            break

                        except:
                            print(f'** W: Failed to clear ql-editor ! (attempt { try_count })')
                            try_count += 1
                            continue

                    time.sleep(2)
                    logger.print_full('Sending prompt keys...')
                    input_editor.send_keys(prompt_line)
                    time.sleep(2)

                    logger.print_full('Highlighting the prompt and generating...')
                    actions = ActionChains(browser_handle)

                    actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()

                    logger.print_full('Waiting a minute...')
                    time.sleep(60)

                    try:
                        # Moment of truth, if we still don't have a composed prompt, there's a problem with Jasper
                        composed_prompt = browser_handle.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div/div/div[3]/div[2]/div/div[3]/div[1]/p[3]').text
                        break

                    except:
                        print('** E: Too many failed attempts to generate prompt in nested condition !')
                        print('      ... Refreshing the page and waiting again did not yield any results.')
                        sys.exit(1)

            time.sleep(15)

            try:
                logger.print_full('Saving composed prompt...')
                composed_prompt = browser_handle.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div/div/div[3]/div[2]/div/div[3]/div[1]/p[3]').text
                break

            except:
                print(f'** W: Could not find composed prompt - attempt { try_count }')
                try_count += 1
                continue

        print()

        if skip_prompt:
            composed_list.append([prompt_line, 'LINE_SKIPPED'])
            continue

        composed_list.append([prompt_line, composed_prompt])

        time.sleep(random.randint(10, 30))

    fp_generated.close()
    print(':: Closing window.')
    browser_handle.quit()

    return composed_list

def random_chunk(li, min_chunk=1, max_chunk=3):
    it = iter(li)
    while True:
        nxt = list(islice(it,randint(min_chunk,max_chunk)))
        if nxt:
            yield nxt
        else:
            break

if __name__ == '__main__':
    checkfiles()

    print(':: Jasper auto prompt script')
    print('----------------------------')

    print('\n:: Loading prompts in-memory...\n')
    prompt_list = None

    with open('query.json', 'r', encoding='utf8') as prompt_fp:
        prompt_list = json.load(prompt_fp)

    login_jasper()

    time_start = datetime.datetime.now().replace(microsecond=0)
    now = datetime.datetime.now().strftime('%Y-%m-%d')

    output_prompts = []

    split_prompts_blocks = list(random_chunk(prompt_list, 90, 150))

    for (block_idx, prompts_block) in enumerate(split_prompts_blocks):
        composed_list = run_prompts(prompts_block, block_idx+1, len(split_prompts_blocks))

        print('\n:: Saving composed prompts to filesystem...\n')
        os.makedirs('./output/', exist_ok=True)

        with open(f'./output/composed.csv', 'a', encoding='utf8') as f_composed:
            f_composed_writer = csv.writer(f_composed, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            for composed_line in composed_list:
                f_composed_writer.writerow(composed_line)

        if len(split_prompts_blocks) > block_idx+1:
            # If not finished
            minutes_waiting = random.randint(30,120)
            print(f':: Waiting for { minutes_waiting } minutes...\n')
            time.sleep(60 * minutes_waiting)

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start

    print('\n:: Script done !')
    print(':: Stats -------------------------')
    print(f':: Script runtime : { runtime }')
    print(f':: Composed prompts : { len(prompt_list) }\n')
