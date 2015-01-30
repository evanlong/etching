#!/usr/bin/env python

import matplotlib.pyplot as plt

from skimage.data import camera
from skimage.filter import roberts, sobel, canny
from skimage import data
from skimage import transform as tf
from skimage.feature import CENSURE
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
from scipy import misc
import sys
from skimage.exposure import rescale_intensity

image = rescale_intensity(misc.imread(sys.argv[1], True))

edge_roberts = roberts(image)
edge_sobel = sobel(image)
edge_canny_2 = canny(image, sigma=2)
edge_canny_3 = canny(image, sigma=3)

fig, (ax0, ax1, ax2, ax3) = plt.subplots(ncols=4)

ax0.imshow(edge_roberts, cmap=plt.cm.gray)
ax0.set_title('Roberts Edge Detection')
ax0.axis('off')

ax1.imshow(edge_sobel, cmap=plt.cm.gray)
ax1.set_title('Sobel Edge Detection')
ax1.axis('off')

ax2.imshow(edge_canny_2, cmap=plt.cm.gray)
ax2.set_title('Canny Edge Detection sigma=2')
ax2.axis('off')

ax3.imshow(edge_canny_3, cmap=plt.cm.gray)
ax3.set_title('Canny Edge Detection sigma=3')
ax3.axis('off')

plt.show()
