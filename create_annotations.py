from PIL import Image 					# (pip install Pillow)
import numpy as np                                 	# (pip install numpy)
from skimage import measure                        	# (pip install scikit-image)
from shapely.geometry import Polygon, MultiPolygon 	# (pip install Shapely)
import os
import json

def create_sub_masks(mask_image, width, height):
    # Initialize a dictionary of sub-masks indexed by RGB colors
    sub_masks = {}
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            pixel = mask_image.getpixel((x,y))[:3]

            # If the pixel is not black...
            if pixel != (0, 0, 0):
                # Check to see if we've created a sub-mask...
                pixel_str = str(pixel)
                sub_mask = sub_masks.get(pixel_str)
                if sub_mask is None:
                   # Create a sub-mask (one bit per pixel) and add to the dictionary
                    # Note: we add 1 pixel of padding in each direction
                    # because the contours module doesn't handle cases
                    # where pixels bleed to the edge of the image
                    sub_masks[pixel_str] = Image.new('1', (width+2, height+2))

                # Set the pixel value to 1 (default is 0), accounting for padding
                sub_masks[pixel_str].putpixel((x+1, y+1), 1)

    return sub_masks

def create_sub_mask_annotation(sub_mask):
    # Find contours (boundary lines) around each sub-mask
    # Note: there could be multiple contours if the object
    # is partially occluded. (E.g. an elephant behind a tree)
    contours = measure.find_contours(sub_mask, 0.5, positive_orientation='low')

    polygons = []
    segmentations = []
    j = 0
    for contour in contours:
        # Flip from (row, col) representation to (x, y)
        # and subtract the padding pixel
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        # Make a polygon and simplify it
        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        
        if(poly.is_empty):
            # Go to next iteration, dont save empty values in list
            continue

        polygons.append(poly)

        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        segmentations.append(segmentation)
    
    return polygons, segmentations

def create_image_annotation(file_name, width, height, image_id):
    images = {
        'file_name': file_name,
        'height': height,
        'width': width,
        'id': image_id
    }

    return images

# Helper function to get absolute paths of all files in a directory
def absolute_file_paths(directory):
    mask_images = []

    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for file in files:
            # Filter only for images in folder         
            if '.png' or '.jpg' in file: 
                mask_images.append(os.path.join(root, file))
    return mask_images

def create_annotation_format(polygon, segmentation, image_id, category_id, annotation_id):
    min_x, min_y, max_x, max_y = polygon.bounds
    width = max_x - min_x
    height = max_y - min_y
    bbox = (min_x, min_y, width, height)
    area = polygon.area

    annotation = {
        'segmentation': segmentation,
        'area': area,
        'iscrowd': 0,
         'image_id': image_id,
        'bbox': bbox,
        'category_id': category_id,
        'id': annotation_id
    }

    return annotation

# Create the annotations of the ECP dataset (Coco format) 
coco_format = {
    "images": [
        {
        }
    ],
    "categories": [
        {
            "supercategory": "window",
            "id": 1,
            "name": 'window'
        },
        {
            "supercategory": "wall",
            "id": 2,
            "name": 'wall'
        },
        {
            "supercategory": "balcony",
            "id": 3,
            "name": 'balcony'
        },
        {
            "supercategory": "door",
            "id": 4,
            "name": 'door'
        },
        {
            "supercategory": "roof",
            "id": 5,
            "name": 'roof'
        },
        {
            "supercategory": "sky",
            "id": 6,
            "name": 'sky'
        },
        {
            "supercategory": "shop",
            "id": 7,
            "name": 'shop'
        },
        {
            "supercategory": "chimney",
            "id": 8,
            "name": 'chimney'
        },
        {
            "supercategory": "outlier",
            "id": 0,
            "name": 'outlier'
        },
        
    ],
    "annotations": [
        {
        }
    ]
}
