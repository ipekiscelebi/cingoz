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
import urllib
from base64 import b64decode
import requests
from cairosvg import svg2png


def is_visible(elm):
    isv = driver.execute_script(
        """
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
    """,
        elm,
    )
    return isv


def not_visible_scroll(elm):
    if not is_visible(elm):
        driver.execute_script("arguments[0].scrollIntoView();", elm)


folder_name = "radio"

if not os.path.isdir(f"./screenshots/{folder_name}"):
    os.makedirs(f"./screenshots/{folder_name}")

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
link = "https://www.google.com/search?q=radio+button&sca_esv=557344174&bih=797&biw=1425&hl=en-GB&tbm=isch&sxsrf=\
    AB5stBizLKngeECOGhUNzUFPTUy6f-0T4g:1692164733796&source=lnms&sa=X&ved=2ahUKEwiXze_uvOCAAxVUbPEDHcLwAPwQ_AUoAXoECAIQAw"

loaded_i = 0
driver.get(f"{link}")
container = driver.find_element(
    By.CSS_SELECTOR, "body > div.T1diZc.KWE8qe > c-wiz > div.mJxzWe"
)
imgs = container.find_elements(
    By.XPATH,
    "//*[@id='islrg']/div[1]/div[contains(@class, 'isv-r') and contains(@class, 'PNCib') and contains(@class, 'ViTmJb') and contains(@class, 'BUooTd')]/a[1]/div[1]/img",
)
time.sleep(2)
i = 0

for j in range(0, 4500):
    try:
    
        not_visible_scroll(imgs[i])
        time.sleep(0.7)
        imgs[i].click()
        time.sleep(0.7)
        src = imgs[i].get_attribute("src")
        fname = f"{uuid.uuid4()}"
        r = requests.get(src)
        r.raise_for_status()
        if r.status_code == 200:
            if src.endswith(".svg"):
                svg2png(
                    bytestring=r.content,
                    write_to=f"./screenshots/{folder_name}/{fname}.png",
                )
            else:
                r.raw.decode_content = True
                dataBytesIO = io.BytesIO(r.content)
                with Image.open(dataBytesIO) as img:
                    img.save(f"./screenshots/{folder_name}/{fname}.png")

    except IndexError:
        divs = container.find_elements(By.CSS_SELECTOR, ".isnpr")
        imgs = divs[loaded_i].find_elements(
            By.XPATH,
            f".//div[contains(@class, 'isv-r') and contains(@class, 'PNCib') and contains(@class, 'ViTmJb') and contains(@class, 'BUooTd')]/a[1]/div[1]/img",
        )
        loaded_i += 1
        i = 0
    except Exception as error:
        time.sleep(0.3)
        print(error)
    i += 1
    if (j-1) > 0 and (j-1) % 100 == 0:
        print(j-1)


driver.quit()
