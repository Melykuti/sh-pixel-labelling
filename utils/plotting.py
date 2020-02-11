import matplotlib.pyplot as plt
import numpy as np
from utils.utils import pairs_to_rows

def plot_image(rgb_image, factor=1./255, figsize=(15,30)):
    plt.figure(figsize=figsize)
    plt.imshow(rgb_image * factor)

def plot_image_pair(rgb_image, px, colour_for_selection, factor=1./255, figsize=(30,30)):
    """
    Utility function for plotting an RGB image with 1. selected pixels coloured
    and 2. in original form, over each other.
    px is an np.array with 2 rows and n columns. 1st row is img row index (1st index
    of img array), that is, y index. It can also be a list of pairs.
    """
    if not isinstance(px, np.ndarray):
        ll = pairs_to_rows(px)
        px = np.array(ll)
    plt.figure(figsize=figsize)
    plot = plt.subplot(2, 1, 2)
    plt.imshow(rgb_image * factor)
    plot = plt.subplot(2, 1, 1)
    if px.shape[1]>0:
        rgb_image_copy = rgb_image.copy()
        #rgb_image_copy[px[0], px[1], :] = 0
        rgb_image_copy[px[0], px[1], 0] = colour_for_selection[0]
        rgb_image_copy[px[0], px[1], 1] = colour_for_selection[1]
        rgb_image_copy[px[0], px[1], 2] = colour_for_selection[2]
        plt.imshow(rgb_image_copy * factor)
    else:
        plt.imshow(rgb_image * factor)
    plt.xticks(range(0, rgb_image.shape[1], 5))
    plt.yticks(range(0, rgb_image.shape[0], 5))

def plot_previews(data, dates, cols = 4, figsize=(15,15)):
    """
    Utility to plot small "true color" previews.
    """
    width = data[-1].shape[1]
    height = data[-1].shape[0]
    
    rows = data.shape[0] // cols + (1 if data.shape[0] % cols else 0)
    fig, axs = plt.subplots(nrows=rows, ncols=cols, figsize=figsize)
    for index, ax in enumerate(axs.flatten()):
        if index < data.shape[0]:
            caption = str(index)+': '+dates[index].strftime('%Y-%m-%d')
            ax.set_axis_off()
            ax.imshow(data[index] / 255., vmin=0.0, vmax=1.0)
            ax.text(0, -2, caption, fontsize=12, color='g')
        else:
            ax.set_axis_off()
