import os
import shutil
import random
import time
import argparse

arg_parser = argparse.ArgumentParser(
    description="Partitions files into folders")


arg_parser.add_argument("-s",
                        "--source",
                        help="Path of source directory",
                        required=True,
                        type=str)

arg_parser.add_argument("-tr",
                        "--train",
                        help="Path of train directory",
                        required=True,
                        type=str)

arg_parser.add_argument("-ts",
                        "--test",
                        help="Path of target directory",
                        required=True,
                        type=str)
arg_parser.add_argument("-v",
                        "--valid",
                        help="Path of valid directory",
                        required=True,
                        type=str)
arg_parser.add_argument("-e",
                        "--extension",
                        help="Extension of annotation files",
                        required=True,
                        type=str)

args = vars(arg_parser.parse_args())


def partition_and_move_files():
    annot_file_ext = args['extension']

    source_directory = args['source']  # source directory

    train_target_directory = args['train']  # train directory
    # Target directory where files will be moved
    test_target_directory = args['test']
    # Target directory where files will be moved
    valid_target_directory = args['valid']

    image_files = []
    for filename in os.listdir(source_directory):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
            image_files.append(filename)

    print("Length of image files:", len(image_files))

    train_files_partition = image_files[0: int(0.7 * len(image_files))]
    test_files_partition = image_files[int(
        0.7 * len(image_files)): int(0.9 * len(image_files)) + 1]
    valid_files_partition = image_files[int(0.9 * len(image_files)) + 1:]

    print("Length of test files partition:", len(test_files_partition))
    print("Length of validation files partition:", len(valid_files_partition))

    random.seed((time.time() * 1000) % 42)
    random.shuffle(test_files_partition)
    random.shuffle(valid_files_partition)

    if not os.path.exists(train_target_directory):
        os.makedirs(train_target_directory)

    if not os.path.exists(test_target_directory):
        os.makedirs(test_target_directory)

    if not os.path.exists(valid_target_directory):
        os.makedirs(valid_target_directory)

    # Get a list of all files in the source directory
    files = os.listdir(source_directory)
    print("Number of files in source dir: ", len(files))

    for file in train_files_partition:

        source_path = os.path.join(source_directory, file)
        target_path = os.path.join(train_target_directory, file)
        # Move the image file to the target directory
        shutil.move(source_path, target_path)

        source_path = os.path.join(
            source_directory, file[0: -4] + annot_file_ext + '.xml')
        target_path = os.path.join(
            train_target_directory, file[0: -4] + annot_file_ext + '.xml')
        # Move the annotation file to the target directory
        shutil.move(source_path, target_path)

    for file in test_files_partition:

        source_path = os.path.join(source_directory, file)
        target_path = os.path.join(test_target_directory, file)
        # Move the image file to the target directory
        shutil.move(source_path, target_path)

        source_path = os.path.join(
            source_directory, file[0: -4] + annot_file_ext + '.xml')
        target_path = os.path.join(
            test_target_directory, file[0: -4] + annot_file_ext + '.xml')
        # Move the annotation file to the target directory
        shutil.move(source_path, target_path)

    for file in valid_files_partition:

        source_path = os.path.join(source_directory, file)
        target_path = os.path.join(valid_target_directory, file)
        # Move the image file to the target directory
        shutil.move(source_path, target_path)

        source_path = os.path.join(
            source_directory, file[0: -4] + annot_file_ext + '.xml')
        target_path = os.path.join(
            valid_target_directory, file[0: -4] + annot_file_ext + '.xml')
        # Move the annotation file to the target directory
        shutil.move(source_path, target_path)


if __name__ == "__main__":
    partition_and_move_files()
