# Copyright 2023 antillia.com Toshiyuki Arai
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

# ImageMaskDatasetGenerator.py
# 2023/06/28 to-arai

import os

import shutil
import glob
import nibabel as nib
import numpy as np
from PIL import Image, ImageOps
import traceback
import matplotlib.pyplot as plt
import SimpleITK as sitk
import cv2

RESIZE = 256

class ImageMaskDatasetGenerator:

  def __init__(self, input_dir="./BraTS21/", output_dir="./BraTS21-master", angle=90):
    self.input_dir = input_dir 

    self.output_images_dir = os.path.join(output_dir, "images")
    self.output_masks_dir  = os.path.join(output_dir, "masks")

    if not os.path.exists(self.output_images_dir):
      os.makedirs(self.output_images_dir)

    if not os.path.exists(self.output_masks_dir):
      os.makedirs(self.output_masks_dir)

    self.angle = angle
    self.BASE_INDEX = 1000
    self.SEG_EXT   = "_seg.nii.gz"
    self.FLAIR_EXT = "_flair.nii.gz"

  def generate(self):
    subdirs = os.listdir(self.input_dir)
    for subdir in subdirs:
      subdir_fullpath = os.path.join(self.input_dir, subdir)
      print("=== subdir {}".format(subdir))
      seg_file   = glob.glob(subdir_fullpath + "/*" + self.SEG_EXT)[0]
      flair_file = glob.glob(subdir_fullpath + "/*" + self.FLAIR_EXT)[0]
      self.generate_mask_files(seg_file    ) 
      self.generate_image_files(flair_file ) 
    
  def generate_image_files(self, niigz_file):
    basename = os.path.basename(niigz_file) 
    nameonly = basename.replace(self.FLAIR_EXT, "")
    nii = nib.load(niigz_file)
    fdata  = nii.get_fdata()
    w, h, d = fdata.shape

    print("shape {}".format(fdata.shape))
    for i in range(d):
      img = fdata[:,:, i]
      filename  = nameonly + "_" + str(i+self.BASE_INDEX) + ".jpg"
      filepath  = os.path.join(self.output_images_dir, filename)
      corresponding_mask_file = os.path.join(self.output_masks_dir, filename)
      if os.path.exists(corresponding_mask_file):
        plt.xticks([])
        plt.yticks([])
        plt.imshow(img, cmap="gray")
        plt.savefig(filepath, bbox_inches='tight', pad_inches=0)
        plt.close()

        img = Image.open(filepath)
        img = img.convert("RGB")
        img = img.resize((RESIZE, RESIZE))
        if self.angle>0:
          img = img.rotate(self.angle)
        img.save(filepath)
      
        print("=== Saved {}".format(filepath))
     
  def generate_mask_files(self, niigz_file ):
    basename = os.path.basename(niigz_file) 
    nameonly = basename.replace(self.SEG_EXT, "")   

    nii = nib.load(niigz_file)
    fdata  = nii.get_fdata()
    w, h, d = fdata.shape
    print("shape {}".format(fdata.shape))
    for i in range(d):
      img = fdata[:,:, i]

      if img.any() >0:
        img = img*255.0
        img = img.astype('uint8')

        image = Image.fromarray(img)
        image = image.convert("RGB")
        image = image.resize((RESIZE, RESIZE))
        if self.angle >0:
          image = image.rotate(self.angle)
        filename  = nameonly + "_" + str(i+ self.BASE_INDEX) + ".jpg"
        filepath  = os.path.join(self.output_masks_dir, filename)
        image.save(filepath, "JPEG")
        print("--- Saved {}".format(filepath))


if __name__ == "__main__":
  try:
    input_dir  = "./BraTS21"
    output_dir = "./BraTS21-master"

    if not os.path.exists(input_dir):
      raise Exception("Not found " + input_dir)   

    if os.path.exists(output_dir):
      shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    generator = ImageMaskDatasetGenerator(input_dir=input_dir, output_dir=output_dir, angle=90)
    generator.generate()
  except:
    traceback.print_exc()

 
