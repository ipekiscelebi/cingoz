import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager
import os
from tqdm.auto import tqdm
import random
import string
import uuid
from xml.etree import ElementTree
from xml.dom import minidom
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import argparse

arg_parser = argparse.ArgumentParser(
    description="Generates a synthetic dataset from present elements")

arg_parser.add_argument("-n",
                        "--number",
                        help="Number of images to be generated",
                        required=True,
                        type=int)
arg_parser.add_argument("-s",
                        "--source",
                        help="Path of source directory",
                        required=True,
                        type=str)

arg_parser.add_argument("-t",
                        "--target",
                        help="Path of target directory",
                        required=True,
                        type=str)

args = vars(arg_parser.parse_args())

if args['number'] < 0:
    print("n must be greater than zero")
    exit()


def get_text_dimensions(text_string, draw, font):

    text_width, text_height = draw.textsize(text_string, font)

    return (text_width, text_height)


def random_string(length):

    text_length = random.randint(1, length)

    random_str = ''.join((random.choice(string.ascii_lowercase + " " + "\t" + "\n")
                         for x in range(text_length)))

    index = 0

    while index < len(random_str):
        newline_offset = random.randint(0, 45)
        random_str = random_str[0:index+newline_offset] + \
            '\n' + random_str[index+newline_offset:]
        index = index + newline_offset

    return random_str


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


font_list = font_manager.findSystemFonts()

max_width, max_height = 1920, 1080

directory_path = args['source']

target_path = args["target"]

if not os.path.exists(target_path):
    os.mkdir(target_path)

space_max_width, space_max_height = 600, 250

labels = {
    0: 'button',
    1: 'checkbox',
    2: 'input',
    3: 'switch',
    4: 'text',
    5: 'space',
    6: 'space',
    7: 'space',
    8: 'space',
    9: 'space',
    10: 'space',
    11: 'text',
    12: 'text',
    13: 'text'

}


folder_list = []

element_counts = {
    0: 0,
    1: 0,
    2: 0,
    3: 0
}


for i in range(4):
    folder_list.append([os.path.join(directory_path, labels[i], file)
                       for file in os.listdir(os.path.join(directory_path, labels[i]))])


image_number = args['number']

for generated_i in tqdm(range(image_number)):

    top_left_x = 2
    bottom = 4
    top_left_y = 4

    random_color = (random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255))
    background_rgb = Image.new('RGB', (max_width, max_height), random_color)
    annotations = []

    for element_i in range(60):

        i = int(random.random() * 14)

        if labels[i] == 'space':
            space_width = int(random.random() * space_max_width)
            space_height = int(random.random() * space_max_height)

            if top_left_x + space_width + 1 > max_width:
                top_left_x = 2
                top_left_y = bottom + 2
                bottom = top_left_y

            if top_left_y + space_height > max_height:
                continue

            top_left_x = top_left_x + space_width
            bottom = max(bottom, top_left_y + space_height)
            continue

        if labels[i] == 'text':

            text_to_be_added = random_string(120)

            Im = ImageDraw.Draw(background_rgb)
            
            mf = ImageFont.truetype(font_list[random.randint(0, len(font_list)-1)], random.randint(12, 20))

            random_color = (0, 0, 0)

            (text_width, text_height) = get_text_dimensions(
                text_to_be_added, Im, mf)

            if top_left_x + text_width > max_width:
                top_left_x = 0
                top_left_y = bottom + 5
                bottom = top_left_y

            if top_left_y + text_height > max_height or top_left_x + text_width > max_width:
                continue

            Im.text((top_left_x, top_left_y), text_to_be_added,
                    fill=random_color, font=mf)
            
            """Im.rectangle([(top_left_x, top_left_y), (top_left_x +
                         text_width, top_left_y + text_height)], outline="red")"""

            annotations.append({
                'name': labels[i],
                'bndbox': {
                    'xmin': str(top_left_x),
                    'ymin': str(top_left_y),
                    'xmax': str(top_left_x + text_width),
                    'ymax': str(top_left_y + text_height)
                }
            })

            top_left_x = top_left_x + text_width + 10
            bottom = max(bottom, top_left_y + text_height + 2)
            continue

        file_index = int(random.random() * len(folder_list[i]))

        element_counts[i] = element_counts[i] + 1

        image_to_be_added = Image.open(folder_list[i][file_index])

        pasted_width, pasted_height = image_to_be_added.size

        if top_left_x + pasted_width + 1 > max_width:
            top_left_x = 2
            top_left_y = bottom + 2
            bottom = top_left_y

        if top_left_y + pasted_height + 1 > max_height:
            continue

        bottom_right_x = top_left_x + pasted_width
        bottom_right_y = top_left_y + pasted_height

        background_rgb.paste(image_to_be_added, (top_left_x, top_left_y))

        annotations.append({
            'name': labels[i],
            'bndbox': {
                'xmin': str(top_left_x),
                'ymin': str(top_left_y),
                'xmax': str(bottom_right_x),
                'ymax': str(bottom_right_y)
            }
        })

        top_left_x = top_left_x + pasted_width + 10

        bottom = max(bottom, bottom_right_y + 1)

    image_name = uuid.uuid1()

    xml_gen(os.path.join(target_path, str(image_name)),
            max_width, max_height, annotations)

    background_rgb.save(os.path.join(target_path, str(image_name)) + ".jpg")

print(f"Element counts in {image_number} images:\n")

for i in range(4):
    print(labels[i], ":", element_counts[i])
