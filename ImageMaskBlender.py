# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# 2024/02/16 ImageMaskBlender.py

import os
import glob
import cv2
import traceback
import shutil
import random

class ImageMaskBlender:

  def __init__(self, blended_dir, mini_dataset, blur_size=(5,5), count=20):
    self.blur_size=blur_size
    self.count    = count
    self.blended_dir = blended_dir
    if os.path.exists(self.blended_dir):
      shutil.rmtree(self.blended_dir)
    if not os.path.exists(self.blended_dir):
      os.makedirs(self.blended_dir)

    if os.path.exists(mini_dataset):
      shutil.rmtree(mini_dataset)

    if not os.path.exists(mini_dataset):
      os.makedirs(mini_dataset)

    self.images_mini_dataset = os.path.join(mini_dataset, "images")  
    if not os.path.exists(self.images_mini_dataset):
      os.makedirs(self.images_mini_dataset)

    self.masks_mini_dataset  = os.path.join(mini_dataset, "masks")
    if not os.path.exists(self.masks_mini_dataset):
      os.makedirs(self.masks_mini_dataset)


  def blend(self, images_dir, masks_dir):
    
    image_files  = glob.glob(images_dir + "/*.jpg")
    image_files  = sorted(image_files)

    random.seed(314)
    sample_images = random.sample(image_files, self.count)
    print("--- sample_image_files {}".format(sample_images))
    for image_file in sample_images:
      basename  = os.path.basename(image_file)
      mask_file = os.path.join(masks_dir, basename)

      shutil.copy2(image_file, self.images_mini_dataset)
      shutil.copy2(mask_file,  self.masks_mini_dataset)
      
      name     = basename.split(".")[0]
    
      img      = cv2.imread(image_file)
      mask     = cv2.imread(mask_file)
      mask     = cv2.blur(mask, self.blur_size)
      img += mask
      merged_file = os.path.join(self.blended_dir, basename)
      cv2.imwrite(merged_file, img)
      print("=== Blended {}".format(merged_file))

if __name__ == "__main__":
  try:
    images_dir   = "./BraTS21-ImageMask-Dataset/train/images"
    masks_dir    = "./BraTS21-ImageMask-Dataset/train/masks"
    blended_dir  = "./Blended_mini_train_dataset"
    mini_dataset = "./Mini_train_dataset"

    blender = ImageMaskBlender(blended_dir, mini_dataset)
    blender.blend(images_dir, masks_dir)

  except:
    traceback.print_exc()
