from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time
import uuid
import shutil
import os
import io
import cv2
from PIL import Image
from xml.etree import ElementTree
from xml.dom import minidom
import math

if not os.path.isdir('./screenshots'):
    os.mkdir('./screenshots')


def is_visible(elm):
    isv = driver.execute_script("""
    function isInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    return isInViewport(arguments[0])
    """, elm)
    return isv


def not_visible_scroll(elm):
    if not is_visible(elm):
        driver.execute_script("arguments[0].scrollIntoView();", elm)


def get_cssscan_elm(driver):
    section = driver.find_element_by_css_selector(
        'body > ul')
    elements = section.find_elements_by_xpath(
        'li/div')
    for elm in elements:
        w, h = elm.size["width"], elm.size["height"]
        if(w > 5 and h > 5):
            image = elm.screenshot_as_png
            img = Image.open(io.BytesIO(image))
            img.save("ss.png")
            file_name = uuid.uuid4()
            os.rename("ss.png", f"{file_name}.png")
            shutil.move(f"./{file_name}.png", "./screenshots/")
            elm.click()
            time.sleep(1.5)
            image = elm.screenshot_as_png
            img = Image.open(io.BytesIO(image))
            img.save("ss.png")
            os.rename("ss.png", f"{file_name}-clicked.png")
            shutil.move(f"./{file_name}-clicked.png", "./screenshots/")

driver = webdriver.Chrome()




driver.get(f'https://getcssscan.com/css-checkboxes-examples')
get_cssscan_elm(driver)

driver.quit()
