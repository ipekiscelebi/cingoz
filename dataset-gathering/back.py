def get_bndbox(element):
    w, h = element.size['width'], element.size['height']
    x, y = element.location['x'], element.location['y']
    px = py = 2
    bndbox = {
        'xmin': str(x-px),
        'xmax': str(x+w+px),
        'ymin': str(y-py),
        'ymax': str(y+h+py)
    }
    return bndbox


objs = [
    {
        'name': 'button',
        'bndbox': {
            'xmin': '327',
            'xmax': '390',
            'ymin': '303',
            'ymax': '348'
        }
    },
    {
        'name': 'input',
        'bndbox': {
            'xmin': '327',
            'xmax': '390',
            'ymin': '303',
            'ymax': '348'
        }
    }
]
# xml_gen('test', 320, 320, objs)

# for link in links:
#     try:
#         driver.get(link)

#         time.sleep(5)
#     except exceptions.StaleElementReferenceException as e:
#         print(e)
#         pass


driver.get('https://www.google.com')
driver.save_screenshot('f.png')
button = driver.find_element_by_xpath(
    '/html/body/div[1]/div[1]/div/div/div/div[2]/a')
img = Image.open('f.png')
img_w, img_h = img.size
wsize = driver.get_window_size()
win_w, win_h = wsize['width'], wsize['height']
w_ratio, h_ratio = img_w / win_w, img_h / win_h
bndbox = get_bndbox(button)
img = cv2.imread('f.png')

xmin, xmax = math.floor(
    int(bndbox['xmin'])*w_ratio), math.ceil(int(bndbox['xmax'])*w_ratio)
ymin, ymax = math.floor(
    int(bndbox['ymin'])*w_ratio), math.ceil(int(bndbox['ymax'])*w_ratio)
print(xmin, xmax, ymin, ymax)
img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
cv2.imwrite('b.png', img)
print(img.size)

driver.quit()
