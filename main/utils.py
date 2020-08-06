import os
import io
import re
import cv2
import json
import base64
import requests
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pylatexenc.latex2text import LatexNodes2Text
from .for_test_V20 import *


def preprocess_img(image):
    new_img = np.copy(image)
    new_img = new_img / 255.0
    return torch.from_numpy(new_img)


def preprocess(image):
    kernel = np.ones((3, 3))
    img = (255 - image) / 255
    img = cv2.dilate(img, kernel, iterations=2)
    # img = cv2.resize(img, (45, 45))
    return img


def get_expn_from_image(image_arr):
    image_arr = np.copy(image_arr)
    print(image_arr.shape)
    if len(image_arr.shape) == 2:
        image_arr = np.expand_dims(image_arr, axis=-1)
    image_arr = np.rollaxis(image_arr, axis=-1) # changing to channels first
    image_arr = np.expand_dims(image_arr, axis=0) # for batch_size dimension
    image_arr = torch.FloatTensor(image_arr)
    return for_test(image_arr)


def model_pipeline_api(base64String):
    # decode image from base64 string
    img = getImageFromString(base64String)
    # collapse channels
    if len(img.shape) == 3 and img.shape[-1] >= 3:
        img = 0.2989 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
    # preprocess image
    img = preprocess_img(img)
    print(img.shape)
    # send image to model
    _, expn = get_expn_from_image(img)
    expn = ''.join(expn[:-1])
    # get solution
    parsed_expn, steps_page = get_solution(expn)
    # get steps
    steps = parse_steps(steps_page)
    steps = [s for s in steps if '<' not in s]
    # return everything
    return {
        'expression': parsed_expn,
        'latex_expression': expn,
        'solution': steps[-1],
        'steps': steps
    }


def getImageFromString(base64String):
    try:
        assert type(base64String) == bytes
    except:
        base64String = bytes(base64String, 'utf-8')

    decoded = base64.decodestring(base64String)
    file_like = io.BytesIO(decoded)
    img = np.array(Image.open(file_like))
    print(img.shape)
    return img


def getStringFromImage(image):
    plt.imsave('res.png', image, format='png')
    with open('res.png', mode='rb') as f:
        enc = base64.encodestring(f.read())
    os.remove('res.png')
    return enc


def get_solution(expn):
    # expn = '4x - 1 = 0'
    print(f"pre: {expn}")
    expn = LatexNodes2Text().latex_to_text(expn)
    print(f"Expression: {expn}")
    try:
        # options for the child browser used by selenium
        options = Options()
        # options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        url = 'https://www.symbolab.com/solver' # the url about to be scraped
        print(os.path.join(os.path.dirname(os.path.abspath('chromedriver')), 'main', 'chromedriver'))
        driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.abspath('chromedriver')), 'main', 'chromedriver'),
            chrome_options=options
        ) # instantiating the webdriver instance

        driver.get(url) # making a GET request ti the URL
        driver.implicitly_wait(100) # some deliberate waiting
        try:
            input_field = driver.find_element_by_xpath('//*[@id="main-input"]/span/textarea')
            print('hello')
        except:
            pass

        input_field.send_keys(expn) # inputting the expression
        driver.find_element_by_xpath('//*[@id="Codepad"]/div[4]/button').click() # clicking the solve button

    except requests.exceptions.RequestException:
        pass

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "solution_step_result"))) # waiting for the result

    soup = BeautifulSoup(driver.page_source, 'lxml')
    page = soup.find_all('div', class_='solution_step_result') # findng all the elements with the steps to solve the expression
    return expn, page


def parse_steps(steps_page_source):
    """
    Go through all the children of the steps and extract the text
    """
    main_list = ["Steps"]
    # print(f"Page: *{steps_page_source}", sep='\n')
    # print("Page: ")
    # print(*steps_page_source, sep='\n')
    for child in steps_page_source:
        if main_list[-1] == "Plotting:":
            main_list = main_list[:-1]
            break
        try:
            if 'solution_step_result' in child['class']:
                text = child.find('span', class_='selectable').text
                req_text = LatexNodes2Text().latex_to_text(text)
                main_list.append(req_text)
                continue
        except Exception as e:
            print(e)

        try:
            if 'mathquill-embedded-latex' in child['class']:
                text = child.find('span', class_='selectable').text
                req_text = LatexNodes2Text().latex_to_text(text)
                main_list.append(req_text)
                continue
        except:
            pass

        try:
            if child['class'] == 'solution_step_list_item':
                text = child.find('span', class_='selectable').text
                req_text = LatexNodes2Text().latex_to_text(text)
                main_list.append(req_text)
                continue
        except:
            pass

        try:
            if child['class'] == 'solution_step_list_item':
                text = child.find('span', class_='selectable').text
                req_text = LatexNodes2Text().latex_to_text(text)
                main_list.append(req_text)
                continue
        except:
            pass

        try:
            if child['class'] == 'solution_step_explanation':
                text = child.find('span', class_='selectable').text
                req_text = LatexNodes2Text().latex_to_text(text)
                main_list.append(req_text)
                continue
        except:
            pass

    return main_list
