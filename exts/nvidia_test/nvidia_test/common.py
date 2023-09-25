
import os
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(root_path, "data", "mnist_cnn.pt")
OUTPUT_PATH = os.path.join(root_path, "data", "predicted_label_image.png")

TEXTURE_SIZE = 256
TXT_SIZE = 180

BLACK_COLOR = [0, 0, 0, 255]