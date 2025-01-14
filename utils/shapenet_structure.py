import os
import sys
import glob
import json
import shutil
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
        
    # Prepare new structure directory
    SRC_PATH = BASE_DIR
    
    DST_PATH = os.path.join(SRC_PATH, '../shapenet_new_structure_v2')
    if not os.path.exists(DST_PATH):
        os.makedirs(DST_PATH)
        
    class_dir = [f.name for f in os.scandir(SRC_PATH) if f.is_dir()]
    for c in class_dir:
        print(c)
        if not os.path.exists(os.path.join(DST_PATH, c)):
            os.makedirs(os.path.join(DST_PATH, c))
            os.makedirs(os.path.join(DST_PATH, c, 'train'))
            os.makedirs(os.path.join(DST_PATH, c, 'test'))
            os.makedirs(os.path.join(DST_PATH, c, 'val'))
    
    # Read train/test split file        
    csv_path = os.path.join(SRC_PATH, 'train_test_split.csv')
    csv_data = pd.read_csv(csv_path, dtype={"synsetId": str, "modelId": str})
    
    # Copy original models to new structure directory
    for row in range(len(csv_data)):
        class_name = csv_data["synsetId"][row]
        file_name = csv_data["modelId"][row]
        split = csv_data["split"][row]
        print(class_name+", "+file_name+", "+split)
        
        src_file_json = os.path.join(SRC_PATH, class_name, file_name, 'models', 'model_normalized.json')
        src_file_mtl = os.path.join(SRC_PATH, class_name, file_name, 'models', 'model_normalized.mtl')
        src_file_obj = os.path.join(SRC_PATH, class_name, file_name, 'models', 'model_normalized.obj')
        src_file_solid = os.path.join(SRC_PATH, class_name, file_name, 'models', 'model_normalized.solid.binvox')
        src_file_surface = os.path.join(SRC_PATH, class_name, file_name, 'models', 'model_normalized.surface.binvox')
        dst_path = os.path.join(DST_PATH, class_name, split, file_name)
        
        if os.path.exists(src_file_mtl) and os.path.exists(src_file_obj) and os.path.exists(src_file_json) and os.path.exists(src_file_solid) and os.path.exists(src_file_surface):
            src_dir = os.path.join(SRC_PATH, class_name, file_name)
            shutil.copytree(src_dir, dst_path)
            
            cur_dst_filename_mtl = os.path.join(dst_path, 'models', 'model_normalized.mtl')
            cur_dst_filename_obj = os.path.join(dst_path, 'models', 'model_normalized.obj')
            cur_dst_filename_json = os.path.join(dst_path, 'models', 'model_normalized.json')
            cur_dst_filename_solid = os.path.join(dst_path, 'models', 'model_normalized.solid.binvox')
            cur_dst_filename_surface = os.path.join(dst_path, 'models', 'model_normalized.surface.binvox')
            new_dst_filename_mtl = os.path.join(dst_path, 'models', file_name+'.mtl')
            new_dst_filename_obj = os.path.join(dst_path, 'models', file_name+'.obj')
            new_dst_filename_json = os.path.join(dst_path, 'models', file_name+'.json')
            new_dst_filename_solid = os.path.join(dst_path, 'models', file_name+'.solid.binvox')
            new_dst_filename_surface = os.path.join(dst_path, 'models', file_name+'.surface.binvox')
            os.rename(cur_dst_filename_mtl, new_dst_filename_mtl)
            os.rename(cur_dst_filename_obj, new_dst_filename_obj)
            os.rename(cur_dst_filename_json, new_dst_filename_json)
            os.rename(cur_dst_filename_solid, new_dst_filename_solid)
            os.rename(cur_dst_filename_surface, new_dst_filename_surface)
            
            # Modify mtl filename in model_normalized.obj
            fin = open(new_dst_filename_obj, 'r', encoding='utf-8', errors='ignore')
            data = fin.read()
            data = data.replace('model_normalized.mtl', file_name+'.mtl')
            fin.close()
            fin = open(new_dst_filename_obj, 'wt', encoding='utf-8', errors='ignore')
            fin.write(data)
            fin.close()
