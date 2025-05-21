from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time
import uuid
import shutil
import os
import io
from PIL import Image

if not os.path.isdir('./screenshots'):
    os.mkdir('./screenshots')


base_urls = [
    'https://www.google.com',
            'https://www.facebook.com',
            'https://www.twitter.com',
            'https://www.github.com',
    'https://www.beyazperde.com',
    'https://www.imdb.com',
    'https://www.sahibinden.com',
    'https://stackoverflow.com'
]

driver = webdriver.Chrome()

links = []

#crawl base urls to collect more urls
for base in base_urls:
    links.append(base)
    driver.get(base)
    for link in driver.find_elements(By.TAG_NAME, 'a'):
        links.append(link.get_attribute('href'))


print(links)



def get_buttons(driver):
    btn_classes = ['btn', 'button']
    for btn_class in btn_classes:
        elements = driver.find_elements(By.CLASS_NAME, btn_class)
        if(len(elements) != 0):
            try:
                for inp in elements:
                    w, h = inp.size["width"], inp.size["height"]
                    if(w != 0 and h != 0):
                        driver.execute_script(
                            "arguments[0].scrollIntoView();", inp)
                        image = inp.screenshot_as_png
                        img = Image.open(io.BytesIO(image))
                        result = Image.new(
                            img.mode, (w+10, h+10), (255, 255, 255))
                        result.paste(img, (5, 5))
                        result.save("ss.png")
                        file_name = uuid.uuid4()
                        os.rename("ss.png", f"{file_name}.png")
                        shutil.move(f"./{file_name}.png", "./screenshots/")
                        print(f"Screenshot taken: {file_name}")
            except exceptions.StaleElementReferenceException as e:
                print(e)
                pass

    elements = driver.find_elements(By.TAG_NAME, 'button')
    if(len(elements) != 0):
        try:
            for inp in elements:
                w, h = inp.size["width"], inp.size["height"]
                if(w != 0 and h != 0):
                    image = inp.screenshot_as_png
                    img = Image.open(io.BytesIO(image))
                    result = Image.new(
                        img.mode, (w+10, h+10), (255, 255, 255))
                    result.paste(img, (5, 5))
                    result.save("ss.png")
                    file_name = uuid.uuid4()
                    os.rename("ss.png", f"{file_name}.png")
                    shutil.move(f"./{file_name}.png", "./screenshots/")
                    print(f"Screenshot taken: {file_name}")
        except exceptions.StaleElementReferenceException as e:
            print(e)
            pass


for link in links:
    try:
        driver.get(link)
        get_text(driver)
        time.sleep(5)
    except exceptions.StaleElementReferenceException as e:
        print(e)
        pass

driver.quit()
