import os
import shutil
import xml.etree.ElementTree as ET
import random
from collections import defaultdict

splits = ['train', 'valid', 'test']
base_path = '../dataset'
output_base = './modified_dataset'
max_per_class = 3000

class_to_boxes = defaultdict(list)

# Step 1: Collect objects from XML files
for split in splits:
    split_dir = os.path.join(base_path, split)
    if not os.path.exists(split_dir):
        print(f"Split directory not found: {split_dir}")
        continue
    for file in os.listdir(split_dir):
        if not file.endswith('.xml'):
            continue
        xml_path = os.path.join(split_dir, file)
        if not os.path.exists(xml_path):
            print(f"File not found: {xml_path}")
            continue
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for obj in root.findall('object'):
            cls = obj.find('name').text
            bbox = obj.find('bndbox')
            bbox_tuple = (
                int(bbox.find('xmin').text),
                int(bbox.find('ymin').text),
                int(bbox.find('xmax').text),
                int(bbox.find('ymax').text)
            )
            class_to_boxes[cls].append((split, file, cls, bbox_tuple))

# Step 2: Filter objects based on max_per_class
selected = defaultdict(list)
for cls, boxes in class_to_boxes.items():
    print(f"Class: {cls}, Total Boxes: {len(boxes)}")
    if len(boxes) > max_per_class:
        boxes = random.sample(boxes, max_per_class)
    selected[cls] = boxes

# Step 3: Prepare kept objects (by file, using class and bbox)
kept_objects = defaultdict(lambda: defaultdict(list))
for cls, items in selected.items():
    for split, file, cls, bbox_tuple in items:
        kept_objects[split][file].append((cls, bbox_tuple))

# Step 4: Write filtered annotations and copy images
for split in splits:
    split_dir = os.path.join(base_path, split)
    out_dir = os.path.join(output_base, split)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    for file in os.listdir(split_dir):
        if not file.endswith('.xml'):
            continue
        xml_path = os.path.join(split_dir, file)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        keep_list = kept_objects[split].get(file, [])
        to_remove = []
        for obj in root.findall('object'):
            cls = obj.find('name').text
            bbox = obj.find('bndbox')
            bbox_tuple = (
                int(bbox.find('xmin').text),
                int(bbox.find('ymin').text),
                int(bbox.find('xmax').text),
                int(bbox.find('ymax').text)
            )
            if (cls, bbox_tuple) not in keep_list:
                to_remove.append(obj)
        for obj in to_remove:
            root.remove(obj)
        if len(root.findall('object')) == 0:
            print(f"No objects left in file: {file}")
            continue
        out_xml_path = os.path.join(out_dir, file)
        tree.write(out_xml_path, encoding='utf-8', xml_declaration=False)
        # Reformat output to match input (remove xml declaration, use tabs, no extra newlines)
        import xml.dom.minidom
        with open(out_xml_path, 'r', encoding='utf-8') as f:
            xml_str = f.read()
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_as_string = dom.toprettyxml(indent='\t')
        # Remove xml declaration and extra blank lines
        pretty_xml_as_string = '\n'.join([line for line in pretty_xml_as_string.split('\n') if line.strip() and not line.strip().startswith('<?xml')])
        with open(out_xml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml_as_string)
        print(f"Written annotation: {out_xml_path}")
        img_name = file.replace('.xml', '.jpg')
        src_img_path = os.path.join(split_dir, img_name)
        dst_img_path = os.path.join(out_dir, img_name)
        if os.path.exists(src_img_path):
            shutil.copy(src_img_path, dst_img_path)
            print(f"Copied image: {dst_img_path}")
        else:
            print(f"Image not found: {src_img_path}")