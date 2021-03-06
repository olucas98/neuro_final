'''
Put images in 'dataset/images/im0.jpg
Put labels in 'dataset/labels/im0.txt
'''

import numpy as np
import os, sys
import argparse
import cv2
sys.path.append('prophesee-automotive-dataset-toolbox')
from src.io.psee_loader import PSEELoader
import src.visualize.vis_utils as vis

x_res = 1280
y_res = 720

GRAY_THRESH = 800_000 # max number of gray pixels to consider frame

SKIP_SIZE = 30 # How many subsequent frames to 'skip' to reduce redundancy

win_before = 0 # microseconds
win_after = 50000

def process(df, psee, bboxes):
    '''
    df: name of data file
    psee: DVS recording object
    bboxes: list of bounding boxes
    '''

    unique_times = np.unique(bboxes['t'])

    countdown = 0
    image_num = 0
    # Loop over the labeled times in AER stream
    for framenum, bboxtime in enumerate(unique_times):
        '''
        YOLO bounding box format: class x_center y_center width height
        '''
        countdown -= 1
        if countdown > 0:
            continue

        # Don't try to process this bounding box if the window we consider
        # ends after the end of the DVS video
        if (psee.total_time() < bboxtime + win_after):
            continue

        YOLO_label = ''
        frame = np.zeros((y_res, x_res, 3), dtype=np.uint8)

        try:
            psee.seek_time(bboxtime-win_before)
            win_events = psee.load_delta_t(win_before+win_after)
            
            frame = vis.make_binary_histo(win_events, img=frame, width=x_res, height=y_res)

            grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_count = np.count_nonzero(grayframe == 127)
            # skip this frame
            if gray_count > GRAY_THRESH:
                continue

            objs = bboxes[bboxes['t'] == bboxtime]

            # Loop over bounding boxes at a labeled time
            for bbox in objs:
                x = bbox['x'] # top left x coord
                y = bbox['y'] # top left y coord
                w = bbox['w'] # box width
                h = bbox['h'] # box height
                ts = bbox['t']
                class_id = bbox['class_id']

                # frame = cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), (0,0,255), 2)

                # Create YOLO labels: must be normalized and between 1 and 0
                x_center = (x + w/2) / x_res
                x_center = np.clip(x_center, 0, 1)
                y_center = (y + h/2) / y_res
                y_center = np.clip(y_center, 0, 1)
                width = w / x_res
                width = np.clip(width, 0, 1)
                height = h / y_res
                height = np.clip(height, 0, 1)

                YOLO_label += f'{class_id} {x_center} {y_center} {width} {height}\n'

            cv2.imwrite(os.path.join(IMG_DIR, df+f'_{image_num}.jpg'), frame)

            with open(os.path.join(LABELS_DIR, f'{df}_{image_num}.txt'), 'w+') as labelfile:
                labelfile.write(YOLO_label)

            image_num += 1

            # After successfully creating a valid frame, skip the next 30 timestamps
            countdown = SKIP_SIZE

        except:
            print(f'Error when processing {df} with bounding box at time {bboxtime}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Turn DVS data into event frames')
    parser.add_argument('--in_dir', help='Point to where all the .dat and .npy files are.')
    parser.add_argument('--out_dir', help='Where to put the images/ and labels/ outputs')
    args = parser.parse_args()

    DATA_IN_DIR = args.in_dir
    IMG_DIR = args.out_dir
    LABELS_DIR = IMG_DIR.replace('images', 'labels')
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(LABELS_DIR, exist_ok=True)

    files = os.listdir(DATA_IN_DIR)
    datafiles = [f.split('_td.dat')[0] for f in files if '_td.dat' in f]

    for df in datafiles:
        psee = PSEELoader(os.path.join(DATA_IN_DIR, df+'_td.dat'))
        bboxes = np.load(os.path.join(DATA_IN_DIR, df+'_bbox.npy'))

        process(df, psee, bboxes)
        print('Done with ',df)

        with open('to_delete.txt', 'a+') as to_delete:
            to_delete.write(os.path.join(DATA_IN_DIR, df+'*'))
