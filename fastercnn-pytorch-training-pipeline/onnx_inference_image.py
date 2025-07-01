"""
Script to run inference on images using ONNX models.
`--input` can take the path either an image or a directory containing images.

USAGE:
python onnx_inference_image.py --input ../inference_data/ --weights weights/fasterrcnn_resnet18.onnx --data data_configs/voc.yaml --show --imgsz 640
"""

import torch
import onnxruntime
import cv2
import numpy as np
import pandas as pd
import os
import glob
import argparse
import yaml
import time
import matplotlib.pyplot as plt

from utils.transforms import infer_transforms, resize
from utils.general import set_infer_dir
from utils.annotations import inference_annotations

def collect_all_images(dir_test):
    """
    Function to return a list of image paths.

    :param dir_test: Directory containing images or single image path.

    Returns:
        test_images: List containing all image paths.
    """
    test_images = []
    if os.path.isdir(dir_test):
        image_file_types = ['*.jpg', '*.jpeg', '*.png', '*.ppm', "*.JPG", "*.PNG"]
        for file_type in image_file_types:
            test_images.extend(glob.glob(f"{dir_test}/{file_type}"))
    else:
        test_images.append(dir_test)
    return test_images

def to_numpy(tensor):
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

def to_df(test_pred,outputs,image_path,width,height,image_resized,threshold):
    for output in outputs:
        for i in range(len(output['boxes'])):
            ll = []
            ll.append(image_path)
            ll.append(width)
            ll.append(height)
            ll.append(output['boxes'].data.numpy()[i].tolist())
            ll.append(output['labels'].data.numpy()[i])
            ll.append(output['scores'].data.numpy()[i])
            label_dict = {}
            label_list = yaml.load(open('custom_data.yaml'),Loader=yaml.FullLoader)['CLASSES']
            label_list = label_list[1:]
            for i,label in enumerate(label_list):
                label_dict[label] = i+1
            for int in label_dict.values():
                if ll[4] == int:
                    ll[4] = list(label_dict.keys())[list(label_dict.values()).index(int)]

            pre_df =pd.DataFrame([{'filename':ll[0].split("/")[-1],
                                    'width':ll[1],
                                    'height':ll[2],
                                    'class':ll[4],
                                    'xmin':ll[3][0]/image_resized.shape[1]*width,
                                    'ymin':ll[3][1]/image_resized.shape[0]*height,
                                    'xmax':ll[3][2]/image_resized.shape[1]*width,
                                    'ymax':ll[3][3]/image_resized.shape[0]*height,
                                    'score':ll[5]}])
            if ll[5] >= threshold:
                test_pred = pd.concat([test_pred,pre_df],axis=0)
    return test_pred

def parse_opt():
    # Construct the argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', 
        help='folder path to input input image (one image or a folder path)',
    )
    parser.add_argument(
        '--data', 
        default=None,
        help='path to the data config file'
    )
    parser.add_argument(
        '-w', '--weights', 
        default=None,
        help='path to trained checkpoint weights if providing custom YAML file'
    )
    parser.add_argument(
        '-th', '--threshold', 
        default=0.3, 
        type=float,
        help='detection threshold'
    )
    parser.add_argument(
        '-si', '--show',  
        action='store_true',
        help='visualize output only if this argument is passed'
    )
    parser.add_argument(
        '-mpl', '--mpl-show', 
        dest='mpl_show', 
        action='store_true',
        help='visualize using matplotlib, helpful in notebooks'
    )
    parser.add_argument(
        '-ims', '--imgsz', 
        default=1024,
        type=int,
        help='resize image to, by default use the original frame/image size'
    )
    parser.add_argument(
        '-nlb', '--no-labels',
        dest='no_labels',
        action='store_true',
        help='do not show labels during on top of bounding boxes'
    )
    parser.add_argument(
        '-ncsv', '--no-csv', 
        dest='csv', 
        action='store_true',
        help='do not save predictions to csv'
    )

    args = vars(parser.parse_args())
    return args

def main(args):
    np.random.seed(42)
    # Load model.
    ort_session = onnxruntime.InferenceSession(
        args['weights'], providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
    )
    with open(args['data']) as file:
        data_configs = yaml.safe_load(file)
        NUM_CLASSES = data_configs['NC']
        CLASSES = data_configs['CLASSES']

    OUT_DIR = set_infer_dir(args['weights'].split('/')[-2],args['threshold'])
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    if args['input'] == None:
        DIR_TEST = data_configs['image_path']
        test_images = collect_all_images(DIR_TEST)
    else:
        DIR_TEST = args['input']
        test_images = collect_all_images(DIR_TEST)
        print("DIR TEST:", DIR_TEST)
    print(f"Test instances: {len(test_images)}")

    # Define the detection threshold any detection having
    # score below this will be discarded.
    detection_threshold = args['threshold']


    # To count the total number of frames iterated through.
    frame_count = 0
    # To keep adding the frames' FPS.
    total_fps = 0
    # To store the predictions in a dataframe.
    tensor_df = pd.DataFrame()
    for i in range(len(test_images)):
        # Get the image file name for saving output later on.
        image_name = test_images[i].split(os.path.sep)[-1].split('.')[0]
        orig_image = cv2.imread(test_images[i])
        frame_height, frame_width, _ = orig_image.shape
        if args['imgsz'] != None:
            RESIZE_TO = args['imgsz']
        else:
            RESIZE_TO = frame_width
        # orig_image = image.copy()
        image_resized = resize(orig_image, RESIZE_TO, square=True)
        image = image_resized.copy()
        # BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = infer_transforms(image)
        # Add batch dimension.
        image = torch.unsqueeze(image, 0)
        print(image.shape)
        start_time = time.time()
        preds = ort_session.run(
            None, {ort_session.get_inputs()[0].name: to_numpy(image)}
        )
        end_time = time.time()
        # Get the current fps.
        fps = 1 / (end_time - start_time)
        # Add `fps` to `total_fps`.
        total_fps += fps
        # Increment frame count.
        frame_count += 1
        outputs = {}
        outputs['boxes'] = torch.tensor(preds[0])
        outputs['labels'] = torch.tensor(preds[1])
        outputs['scores'] = torch.tensor(preds[2])
        outputs = [outputs]

        # Carry further only if there are detected boxes.
        if len(outputs[0]['boxes']) != 0:
            orig_image = inference_annotations(
                outputs, 
                detection_threshold, 
                CLASSES,
                COLORS, 
                orig_image, 
                image_resized,
                args
            )
            if not args['csv']:
                tensor_df = to_df(tensor_df,outputs,image_name,frame_width,frame_height,image_resized,detection_threshold)
            if args['show']:
                cv2.imshow('Prediction', orig_image)
                cv2.waitKey(1)
            if args['mpl_show']:
                plt.imshow(orig_image[:, :, ::-1])
                plt.axis('off')
                plt.show()
        cv2.imwrite(f"{OUT_DIR}/{image_name}.jpg", orig_image)
        print(f"Image {i+1} done...")
        print('-'*50)
    if not args['csv']:
        tensor_df.to_csv(f"{OUT_DIR}/predictions.csv",index=False)
    print('TEST PREDICTIONS COMPLETE')
    cv2.destroyAllWindows()
    # Calculate and print the average FPS.
    avg_fps = total_fps / frame_count
    print(f"Average FPS: {avg_fps:.3f}")

if __name__ == '__main__':
    args = parse_opt()
    main(args)
