import numpy as np
from .common import TEXTURE_SIZE


def draw_circle(image_data, coord_x, coord_y, radius)->np.ndarray:

    TEXTURE_SIZE = image_data.shape[0]

    # Create grids for x and y coordinates
    y, x = np.ogrid[0:TEXTURE_SIZE, 0:TEXTURE_SIZE]

    # Calculate the distance to the center for each point
    distance_to_center = (x - coord_x)**2 + (y - coord_y)**2

    # Identify the points within the circle
    circle_points = distance_to_center <= radius**2

    # Create the circle image with the same initial data as image_data
    circle_image = np.copy(image_data)
    
    # Draw the circle in black (setting it to [0, 0, 0, 255])
    circle_image[circle_points] = [0, 0, 0, 255]

    # Superimpose the circle onto the existing image data
    image_data = np.where(circle_image == [0, 0, 0, 255], circle_image, image_data)
    
    return image_data