import pygame
import os
import spritesheets

def load_images(path, colorkey=-1):
    """
    Loads all images in directory. The directory must only contain images.

    Args:
        path: The relative or absolute path to the directory to load images from.

    Returns:
        List of images.
    """
    images = []
    for file_name in os.listdir(path):
        image = pygame.image.load(path + os.sep + file_name).convert()
        image.set_colorkey(colorkey)
        images.append(image)
    return images

