import numpy as np
from .common import TEXTURE_SIZE,BLACK_COLOR


def draw_circle(image_data, coord_x, coord_y, radius)->np.ndarray:

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


def draw_circle_optimized(image_data, coord_x, coord_y, radius)->np.ndarray:

    # Determine the bounding box of the circle.
    box_left = max(0, coord_x - radius)
    box_right = min(TEXTURE_SIZE, coord_x + radius)
    box_top = max(0, coord_y - radius)
    box_bottom = min(TEXTURE_SIZE, coord_y + radius)
    
    # Create a coordinate grid for the bounding box.
    y, x = np.ogrid[box_top:box_bottom, box_left:box_right]

    # Use the circle equation to create a mask for that region.
    circle_mask = (x - coord_x)**2 + (y - coord_y)**2 <= radius**2

    # Update only the pixels in that region where the mask is True.
    image_data[box_top:box_bottom, box_left:box_right][circle_mask] = BLACK_COLOR

    return image_data