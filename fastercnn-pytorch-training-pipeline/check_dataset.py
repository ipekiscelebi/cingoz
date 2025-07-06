# import os
import xml.etree.ElementTree as ET
import glob
import pandas as pd
import json

dataset_dir = '../dataset/'
files = []
label_dict = {'button':0, 'input':0, 'checkbox':0, 'dropdown':0, 'label':0, 'icon':0, 'radio':0, 'switch':0}
total_label_dict = {'button':0, 'input':0, 'checkbox':0, 'dropdown':0, 'label':0, 'icon':0, 'radio':0, 'switch':0}
results = []

def iterate_files(path):
    file_list = glob.glob(path+'**/*.xml',recursive=True)
    for file in file_list:
        if file.endswith('.xml'):
            files.append(file)
            # print(file)

def xml_parse(files):
    for file in files:
        label_dict = {'button':0, 'input':0, 'checkbox':0, 'dropdown':0, 'label':0, 'icon':0, 'radio':0, 'switch':0}
        tree = ET.parse(file)
        root = tree.getroot()
        for obj in root.findall('object'):
            name = obj.find('name').text
            label_dict[name] += 1
            total_label_dict[name] += 1
        # print(f"{file.split('/')[-1]}'s label_dict: {label_dict}")
        results.append({'file_name':file.split('/')[-1].split('.')[0],'folder':file.split('/')[3],'button':label_dict['button'],'input':label_dict['input'],'checkbox':label_dict['checkbox'],'dropdown':label_dict['dropdown'],'label':label_dict['label'],'icon':label_dict['icon'],'radio':label_dict['radio'],'switch':label_dict['switch']})
        label_dict.clear()
    df = pd.DataFrame(results)
    df.sort_values(by=['folder','label'],inplace=True,ascending=False)
    df.to_csv(f'./dataset/dataset_{dataset_dir.split("/")[2]}.csv',index=False)
    sorted_label_dict = {k: v for k, v in sorted(total_label_dict.items(), key=lambda item: item[1],reverse=True)}
    print(f"Total Label Counts: \n{json.dumps(sorted_label_dict, indent=4)}")
    
if __name__ == '__main__':
    iterate_files(dataset_dir)
    xml_parse(files)

    