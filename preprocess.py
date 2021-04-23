'''
Put images in 'dataset/images/im0.jpg
Put labels in 'dataset/labels/im0.txt
'''

import numpy as np
import os, sys
import cv2
sys.path.append('prophesee-automotive-dataset-toolbox')
from src.io.psee_loader import PSEELoader
import src.visualize.vis_utils as vis

x_res = 304
y_res = 240

DATA_IN_DIR = 'data_in_lowres'
IMG_DIR = 'dataset_lowres/images'
LABELS_DIR = 'dataset_lowres/labels'

win_before = 0 # microseconds
win_after = 50000

classes_index = ['cars', 'pedestrians']

def process(df, psee, bboxes):
    unique_times = np.unique(bboxes['ts'])
    # Loop over the labeled times in AER stream
    for framenum, bboxtime in enumerate(unique_times):
        '''
        YOLO bounding box format: class x_center y_center width height
        '''

        YOLO_label = ''
        frame = np.zeros((y_res, x_res, 3), dtype=np.uint8)
        # frame[:] = 127
        psee.seek_time(bboxtime-win_before)
        win_events = psee.load_delta_t(win_before+win_after)
        # frame[win_events['y'], win_events['x'], win_events['p']] += 255
        # for event in win_events:
        #     frame[event['y'], event['x'], :] += 1
        # frame[win_events['y'], win_events['x'], :] = 255 * win_events['p'][:, None]
        frame = vis.make_binary_histo(win_events, img=frame, width=x_res, height=y_res)

        objs = bboxes[bboxes['ts'] == bboxtime]

        # Loop over bounding boxes at a labeled time
        for bbox in objs:
            x = bbox['x'] # top left x coord
            y = bbox['y'] # top left y coord
            w = bbox['w'] # box width
            h = bbox['h'] # box height
            ts = bbox['ts']
            class_id = bbox['class_id']

            # frame = cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), (0,0,255), 2)

            x_center = (x + w//2) / x_res
            y_center = (y + h//2) / y_res
            width = w / x_res
            height = h / y_res

            YOLO_label += f'{class_id} {x_center} {y_center} {width} {height}\n'
        # cv2.imshow('frame', frame)
        # cv2.waitKey(5000)
        # continue
        cv2.imwrite(os.path.join(IMG_DIR, df+f'_{framenum}.jpg'), frame)

        with open(os.path.join(LABELS_DIR, f'{df}_{framenum}.txt'), 'w') as labelfile:
            labelfile.write(YOLO_label)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

# cv2.destroyAllWindows()

if __name__ == '__main__':

    files = os.listdir(DATA_IN_DIR)
    datafiles = [f.split('_td.dat')[0] for f in files if '_td.dat' in f]

    for df in datafiles:
        psee = PSEELoader(os.path.join(DATA_IN_DIR, df+'_td.dat'))
        bboxes = np.load(os.path.join(DATA_IN_DIR, df+'_bbox.npy'))

        process(df, psee, bboxes)