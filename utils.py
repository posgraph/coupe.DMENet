import tensorflow as tf
import tensorlayer as tl
from tensorlayer.prepro import *
from config import config, log_config
from skimage import feature
from skimage import color
from scipy.ndimage.filters import gaussian_filter

import scipy
import numpy as np

def get_imgs_RGB_fn(file_name, path):
    """ Input an image path and name, return an image array """
    # return scipy.misc.imread(path + file_name).astype(np.float)
    return scipy.misc.imread(path + file_name, mode='RGB')

def get_imgs_GRAY_fn(file_name, path):
    """ Input an image path and name, return an image array """
    # return scipy.misc.imread(path + file_name).astype(np.float)
    image = scipy.misc.imread(path + file_name, mode='P')/255
    return np.expand_dims(np.asarray(image), 3)

def blur_crop_edge_sub_imgs_fn(data):
    '''
    h = config.TRAIN.height
    w = config.TRAIN.width
    cropped_image = crop(image, wrg=w, hrg=h, is_random=is_random)
    cropped_image = cropped_image / (255. / 2.) - 1
    '''
    h = config.TRAIN.height
    w = config.TRAIN.width
    r = (int)(h/2.) # 35

    image, sigma = data
    #mask = np.ones_like(mask) - mask

    image_h, image_w = np.asarray(image).shape[0:2]

    '''
    # 1. get edge image in "sharp region"
    # 1-1. elementary wise application between image and mask
    #sharp_image = np.multiply(image, mask)
    # 1-2. get edge image
    #edge_image = feature.canny(color.rgb2gray(sharp_image))
    edge_image = np.squeeze(edge)
    # 2. get points in  edge image
    coordinates = np.transpose(np.where(edge_image == 1), (1, 0))

    condition_y = np.logical_and(coordinates[:, 0] >= r, coordinates[:, 0] < image_h - r)
    condition_x = np.logical_and(coordinates[:, 1] >= r, coordinates[:, 1] < image_w - r)
    condition = np.logical_and(condition_x, condition_y)
    condition = np.transpose(np.expand_dims(condition, axis = 0), (1, 0))
    condition = np.concatenate((condition, condition), axis = 1)

    coordinates = np.reshape(np.extract(condition, coordinates), (-1, 2))

    # 3. crop image with given random edge point at center
    random_index = np.random.randint(0, coordinates.shape[0])
    center_y, center_x = coordinates[random_index, 0:2]

    cropped_image = image[center_y - r : center_y + r + 1, center_x - r : center_x + r + 1]

    # 4. Gaussian Blur
    image_blur = gaussian_filter(cropped_image, (sigma[0], sigma[0], 0))
    image_blur = image_blur + (np.mean(cropped_image) - np.mean(image_blur))
    image_blur[image_blur > 255.] = 255.

    ###
    cropped_edge = edge[center_y - r : center_y + r + 1, center_x - r : center_x + r + 1]
    cropped_edge = np.concatenate((cropped_edge, cropped_edge, cropped_edge), axis = 2)
    return image_blur, cropped_image, cropped_edge
    ###
    '''
    cropped_image = tl.prepro.crop(image, wrg=h, hrg=w, is_random=True)
    image_blur = gaussian_filter(cropped_image, (sigma[0], sigma[0], 0))
    image_blur = image_blur + (np.mean(cropped_image) - np.mean(image_blur))
    image_blur[image_blur > 255.] = 255.

    scipy.misc.imsave("/sharp_crop.png", cropped_image)
    scipy.misc.imsave("/blur_crop.png", image_blur)

    return image_blur / (255. / 2.) - 1.

def downsample_fn(x):
    # We obtained the LR images by downsampling the HR images using bicubic kernel with downsampling factor r = 4.
    x = imresize(x, size=[56, 56], interp='bicubic', mode=None)
    x = x / (255. / 2.)
    x = x - 1.
    return x

def t_or_f(arg):
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
       return True
    elif 'FALSE'.startswith(ua):
       return False
    else:
       pass 

def activation_map(gray):
    red = np.expand_dims(np.ones_like(gray), axis = 2)
    green = np.expand_dims(np.ones_like(gray), axis = 2)
    blue = np.expand_dims(np.ones_like(gray), axis = 2)
    gray = np.expand_dims(gray, axis = 2)

    red[(gray == 0.)] = 0.
    green[(gray == 0.)] = 0.
    blue[(gray == 0.)] = 0.

    red[(gray <= 1./3)&(gray > 0.)] = 1.
    green[(gray <= 1./3)&(gray > 0.)] = 3. * gray[(gray <= 1./3.)&(gray > 0.)]
    blue[(gray <= 1./3)&(gray > 0.)] = 0.

    red[(gray > 1./3)&(gray <= 2./3)] = -3. * (gray[(gray > 1./3)&(gray <= 2./3)] - 1./3.) + 1.
    green[(gray > 1./3)&(gray <= 2./3)] = 1.
    blue[(gray > 1./3)&(gray <= 2./3)] = 0.

    red[(gray > 2./3)] = 0.
    green[(gray > 2./3)] = -3. * (gray[(gray > 2./3)] - 2./3.) + 1.
    blue[(gray > 2./3)] = 3. * (gray[(gray > 2./3)] - 2./3.)

    return np.concatenate((red, green, blue), axis = 2) * 255.


