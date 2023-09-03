import os
import torch
import torch.nn as nn
import torch.nn.functional as F


from PIL import Image, ImageDraw, ImageFont
import torchvision.transforms as transforms


MODEL_PATH = r"C:\temp\mnist_cnn.pt"
IMAGE_PATH = r"C:\temp\MNIST\testSet\testSet\img_1719.jpg"
PREDICTED_TEXT_IMAGE_PATH = r"C:\temp\predicted_label_image.png"
# WROTE THIS CODE WITH THE HELP OF CHAT GPT 4

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output

def img2txt2img(model_path:str,image_path:str,output_path:str):
    
    # Initialize the model
    model = Net()

    # Load the model
    model.load_state_dict(torch.load(model_path))

    # Set the model to evaluation mode
    model.eval()

    #input image
    input_image = Image.open(image_path).convert('L')
    #input_image.show()

    # Define the transformation
    transform = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # Normalization values used during training
    ])

    # Apply the transformations to the image
    input_image = transform(input_image)

    # Add a batch dimension
    input_image = input_image.unsqueeze(0)  # shape becomes [1, 1, 28, 28]


    # Perform inference
    with torch.no_grad():  # Deactivate gradients for the following block
        output = model(input_image)

    # Print the output
    print(output)

    # Get the predicted label
    _, predicted_label = torch.max(output, 1)
    predicted_txt = predicted_label.item()
    print("Predicted label:", predicted_txt)

    # Create an image with white background
    width, height = 128, 128
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load a font
    # You might have to download a specific font or use one that's available on your system
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size to center it
    text = str(predicted_txt)  # Assuming `predicted_label` is a PyTorch tensor containing the label
    text_width, text_height = draw.textsize(text, font=font)

    text_x = width / 2 - text_width / 2
    text_y = height / 2 - text_height / 2

    # Add text to image
    draw.text((text_x, text_y), text, font=font, fill="black")

    # Save or show image
    image.save(output_path)

#img2txt2img(MODEL_PATH,IMAGE_PATH,PREDICTED_TEXT_IMAGE_PATH)