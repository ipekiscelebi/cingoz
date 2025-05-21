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


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return ElementTree.fromstring(reparsed.toprettyxml(indent="\t"))


def xml_gen(filename, w, h, objects):
    root = ElementTree.Element("annotation")

    fname = ElementTree.Element("filename")
    fname.text = filename
    root.append(fname)

    path = ElementTree.Element("path")
    path.text = filename
    root.append(path)

    size = ElementTree.Element("size")
    width = ElementTree.SubElement(size, 'width')
    width.text = str(w)
    height = ElementTree.SubElement(size, 'height')
    height.text = str(h)
    depth = ElementTree.SubElement(size, 'depth')
    depth.text = '3'
    root.append(size)
    for i, item in enumerate(objects):
        obj = ElementTree.Element("object")
        name = ElementTree.SubElement(obj, 'name')
        name.text = item['name']
        item_id = ElementTree.SubElement(obj, 'id')
        item_id.text = f"{item['name']}-{i}"
        bndbox = ElementTree.SubElement(obj, 'bndbox')
        xmin = ElementTree.SubElement(bndbox, 'xmin')
        xmin.text = item['bndbox']['xmin']
        xmax = ElementTree.SubElement(bndbox, 'xmax')
        xmax.text = item['bndbox']['xmax']
        ymin = ElementTree.SubElement(bndbox, 'ymin')
        ymin.text = item['bndbox']['ymin']
        ymax = ElementTree.SubElement(bndbox, 'ymax')
        ymax.text = item['bndbox']['ymax']
        root.append(obj)

    tree = ElementTree.ElementTree(prettify(root))
    fname = filename.replace('.', '_')
    with open(f"{fname}.xml", "wb") as files:
        tree.write(files)


def get_bndbox(element, file_name):
    img = Image.open(file_name)
    img_w = img.size[0]
    wsize = driver.get_window_size()
    win_w = wsize['width']
    w_ratio = img_w / win_w
    w, h = element.size['width'], element.size['height']
    x, y = element.location['x'], element.location['y']
    px = py = 2
    xmin, xmax = math.floor(
        (x-px)*w_ratio), math.ceil((x+w+px)*w_ratio)
    ymin, ymax = math.floor(
        (y-py)*w_ratio), math.ceil((y+h+py)*w_ratio)
    bndbox = {
        'xmin': str(xmin),
        'xmax': str(xmax),
        'ymin': str(ymin),
        'ymax': str(ymax)
    }
    return bndbox


def draw_bndbox(file_name):
    img = cv2.imread(file_name)
    fname = file_name.replace('.', '_')
    tree = ElementTree.parse(f'{fname}.xml')
    root = tree.getroot()
    for member in root.findall('object'):
        item_id = member.find('id').text
        bndbox = member.find('bndbox')
        xmin, ymin, xmax, ymax = int(bndbox.find('xmin').text), int(bndbox.find(
            'ymin').text), int(bndbox.find('xmax').text), int(bndbox.find('ymax').text),
        img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
        text = cv2.putText(img, item_id, (xmin, ymin-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
    folder_name = file_name.split('.')[0]
    cv2.imwrite(f'bndbox-{folder_name}.png', img)
    shutil.move(f'bndbox-{folder_name}.png', f"./screenshots/{folder_name}")


def get_buttons(driver):
    btn_classes = ['btn', 'button']
    objs = []
    class_name = 'button'
    file_name = f'{uuid.uuid4()}'
    file_name_png = f'{file_name}.png'
    driver.save_screenshot(file_name_png)
    for btn_class in btn_classes:
        elements = driver.find_elements(By.CLASS_NAME, btn_class)
        if(len(elements) != 0):
            try:

                for elm in elements:
                    if(elm.is_displayed()):
                        w, h = elm.size["width"], elm.size["height"]
                        if(w > 25 and h > 25):
                            bndbox = get_bndbox(elm, file_name_png)
                            obj = {
                                'name': class_name,
                                'bndbox': bndbox
                            }
                            objs.append(obj)

            except exceptions.StaleElementReferenceException as e:
                print(e)
                pass
    tags = ['button', 'a']
    for t in tags:
        elements = driver.find_elements(By.TAG_NAME, t)
        if(len(elements) != 0):
            try:

                for elm in elements:
                    if(elm.is_displayed()):
                        w, h = elm.size["width"], elm.size["height"]
                        if(w > 25 and h > 25):
                            bndbox = get_bndbox(elm, file_name_png)
                            obj = {
                                'name': class_name,
                                'bndbox': bndbox
                            }
                            objs.append(obj)

            except exceptions.StaleElementReferenceException as e:
                print(e)
                pass
    elements = driver.find_elements(By.XPATH, "//input[@type='submit']")
    if(len(elements) != 0):
        try:

            for elm in elements:
                if(elm.is_displayed()):
                    w, h = elm.size["width"], elm.size["height"]
                    if(w > 25 and h > 25):
                        bndbox = get_bndbox(elm, file_name_png)
                        obj = {
                            'name': class_name,
                            'bndbox': bndbox
                        }
                        objs.append(obj)

        except exceptions.StaleElementReferenceException as e:
            print(e)
            pass
    if(len(objs)):
        screen_w, screen_h = Image.open(file_name_png).size
        xml_gen(file_name_png, screen_w, screen_h, objs)
        if not os.path.isdir(f"./screenshots/{file_name}"):
            os.mkdir(f"./screenshots/{file_name}")
        draw_bndbox(file_name_png)
        shutil.move(f"./{file_name}.png", f"./screenshots/{file_name}")
        fname = file_name_png.replace('.', '_')
        shutil.move(f"./{fname}.xml", f"./screenshots/{file_name}")

def get_inputs(driver):
    # btn_classes = ['input', 'inp']
    # objs = []
    # class_name = 'input'
    # file_name = f'{uuid.uuid4()}'
    # file_name_png = f'{file_name}.png'
    # driver.save_screenshot(file_name_png)
    # for btn_class in btn_classes:
    #     elements = driver.find_elements(By.CLASS_NAME, btn_class)
    #     if(len(elements) != 0):
    #         try:

    #             for elm in elements:
    #                 elm = elm.find_element(By.XPATH, '//../')
    #                 not_visible_scroll(elm)
    #                 w, h = elm.size["width"], elm.size["height"]
    #                 if(w > 25 and h > 25):
    #                     bndbox = get_bndbox(elm, file_name_png)
    #                     obj = {
    #                         'name': class_name,
    #                         'bndbox': bndbox
    #                     }
    #                     objs.append(obj)

    #         except exceptions.StaleElementReferenceException as e:
    #             print(e)
    #             pass
    xpaths = ["//input[@type='text']", "//input[@type='password']"]
    for t in xpaths:
        elements = driver.find_elements(By.XPATH, t)
        print(elements)
    #     if(len(elements) != 0):
    #         try:
    #             for elm in elements:
    #                 elm = elm.find_element(By.XPATH, '..')
    #                 not_visible_scroll(elm)
    #                 w, h = elm.size["width"], elm.size["height"]
    #                 if(w > 25 and h > 25):
    #                     bndbox = get_bndbox(elm, file_name_png)
    #                     obj = {
    #                         'name': class_name,
    #                         'bndbox': bndbox
    #                     }
    #                     objs.append(obj)

    #         except exceptions.StaleElementReferenceException as e:
    #             print(e)
    #             pass
    # if(len(objs)):
    #     screen_w, screen_h = Image.open(file_name_png).size
    #     xml_gen(file_name_png, screen_w, screen_h, objs)
    #     if not os.path.isdir(f"./screenshots/{file_name}"):
    #         os.mkdir(f"./screenshots/{file_name}")
    #     draw_bndbox(file_name_png)
    #     shutil.move(f"./{file_name}.png", f"./screenshots/{file_name}")
    #     fname = file_name_png.replace('.', '_')
    #     shutil.move(f"./{fname}.xml", f"./screenshots/{file_name}")


def get_elements_scrennshot(driver, typ):
    elements = driver.find_elements(By.TAG_NAME, typ)
    if(len(elements) != 0):
        for inp in elements:
            w, h = inp.size["width"], inp.size["height"]
            if(w != 0 and h != 0):
                image = inp.screenshot_as_png
                img = Image.open(io.BytesIO(image))
                img.save("ss.png")
                file_name = uuid.uuid4()
                os.rename("ss.png", f"{file_name}.png")
                shutil.move(f"./{file_name}.png", "./screenshots/")
                print(f"Screenshot taken: {file_name}")

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

def get_all_elements(driver):
    all_elements = []

    btn_classes = ['btn', 'button']
    for i in btn_classes:
        elements = driver.find_elements(By.CLASS_NAME, i)
        for elm in elements:
            all_elements.append(('button',elm))
    
    input_classes = ['input', 'inp']
    for i in input_classes:
        elements = driver.find_elements(By.CLASS_NAME, i)
        for elm in elements:
            all_elements.append(('input',elm))
    
    button_xpaths = ["//input[@type='submit']"]
    for i in button_xpaths:
        elements = driver.find_elements(By.XPATH, i)
        for elm in elements:
            all_elements.append(('button',elm))

    input_xpaths = ["//input[@type='text']", "//input[@type='password']"]
    for i in input_xpaths:
        elements = driver.find_elements(By.XPATH, i)
        for elm in elements:
            all_elements.append(('input',elm))
    tags = ['button']
    for i in tags:
        elements = driver.find_elements(By.TAG_NAME, i)
        for elm in elements:
            all_elements.append(('button',elm))
    tags = ['textarea']
    for i in tags:
        elements = driver.find_elements(By.TAG_NAME, i)
        for elm in elements:
            all_elements.append(('input',elm))

    return all_elements


def take_screenshots(driver, elements):
    while len(elements) != 0:
        objs = []
        file_name = f'{uuid.uuid4()}'
        file_name_png = f'{file_name}.png'
        not_visible_scroll(elements[0][1])
        vis_elements = list(filter(lambda x: is_visible(x[1]), elements))
        if len(vis_elements) != 0:        
            driver.save_screenshot(file_name_png)
        elements = list(set(elements)-set(vis_elements))
        try:
            for elm in vis_elements:
                current_elm = elm[1]
                if elm[0] == 'input':
                    current_elm = current_elm.find_element(By.XPATH, '..')       
                w, h = current_elm.size["width"], current_elm.size["height"]
                if(w > 25 and h > 25):
                    bndbox = get_bndbox(current_elm, file_name_png)
                    obj = {
                        'name': elm[0],
                        'bndbox': bndbox
                    }
                    objs.append(obj)

        except exceptions.StaleElementReferenceException as e:
            print(e)
            pass
        if(len(objs)):
            screen_w, screen_h = Image.open(file_name_png).size
            xml_gen(file_name_png, screen_w, screen_h, objs)
            if not os.path.isdir(f"./screenshots/{file_name}"):
                os.mkdir(f"./screenshots/{file_name}")
            draw_bndbox(file_name_png)
            shutil.move(f"./{file_name}.png", f"./screenshots/{file_name}")
            fname = file_name_png.replace('.', '_')
            shutil.move(f"./{fname}.xml", f"./screenshots/{file_name}")




base_urls = [
    'https://www.google.com',
    'https://www.facebook.com',
    'https://www.twitter.com',
    'https://www.github.com',
    'https://www.imdb.com',
    'https://stackoverflow.com',
    'https://www.glassdoor.com',
    'https://www.walmart.com',
    'https://www.ebay.co.uk',
    'https://www.yelp.com'
]

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920,1080)
links = []

for base in base_urls:
    links.append(base)
    driver.get(base)
    for link in driver.find_elements(By.TAG_NAME, 'a'):
        links.append(link.get_attribute('href'))

links.append('https://www.trendyol.com')
links.append('https://www.hepsiburada.com')
links.append('https://www.amazon.com.tr')
links.append('https://www.cimri.com')

# print(links)



for link in base_urls:
    try:
        driver.get(link)
        time.sleep(2)
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1000, total_height)
        elements = get_all_elements(driver)
        # elements = []
        take_screenshots(driver, elements)
        time.sleep(2)
    except exceptions.StaleElementReferenceException as e:
        print(e)
        pass


driver.quit()
