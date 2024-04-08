# Import what we need to create the model and dataset
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms
import pandas as pd
import tqdm

from mutant import mutant

# We modify the MNIST Dataset class to expose some information about the source data
# to allow us to uniquely identify an input.
class CustomDataset(datasets.MNIST):
    def __getitem__(self, index):
        img, label = super().__getitem__(index) # Existing loader returns the img and the label
        resource_uri = f"{'train' if self.train else 't10k'}-images-idx3-ubyte-{index}"
        return img, label, resource_uri

# Normalizing transform for MNIST data
transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
)

# Get the MNIST training data (wrapped in our custom dataset)
train_mnist_data = CustomDataset("../data", train=True, transform=transform, download=True)

# Split the training data into equal 'training' and 'unlabeled' sets
train_size = len(train_mnist_data) // 2
unlabeled_size = len(train_mnist_data) - train_size
train_dataset, unlabeled_dataset = torch.utils.data.random_split(train_mnist_data, [train_size, unlabeled_size], generator=torch.Generator().manual_seed(42))


# A simple feed-forward CNN clasifier, with two conv. layers and two fully connected layers.
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
        x = F.log_softmax(x, dim=1)
        output = x.argmax(dim=1, keepdim=True)
        return output

# Set the device
device = 'cpu'

# Load up the pretrained model
model = Net()
model.load_state_dict(torch.load("mnist_cnn.pt"))
model.eval()
model.to(device)

# Create a forward hook class to extract and store embeddings from a supplied model layer
class EmbeddingHook:
  def __init__(self, module):
    self.hook = module.register_forward_hook(self.hook_fn)

  def hook_fn(self, module, input, output):
    self.embeddings = output.detach().tolist()

  def __del__(self):
    self.hook.remove()

# Attach the embedding hook to the last fully connected layer before softmax
embedding_hook = EmbeddingHook(model.fc2)


mutant_client = mutant.init()

# Send training data to Chroma
train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=64)

with torch.no_grad():
    for img, label, uri in train_dataloader:
        inference_class = model(img)
        mutant_client.add_training(
            embedding=embedding_hook.embeddings,
            input_uri=list(uri),
            inference_class=inference_class.detach().flatten().tolist(),
            label_class=label.detach().tolist(),
        )

# Send unlabeled data to Chroma
unlabeled_dataloader = torch.utils.data.DataLoader(unlabeled_dataset, batch_size=64)

with torch.no_grad():
    for img, label, uri in unlabeled_dataloader:
        inference_class = model(img)
        mutant_client.add_unlabeled(
            embedding=embedding_hook.embeddings,
            input_uri=list(uri),
            inference_class=inference_class.detach().flatten().tolist(),
        )

mutant_client.process()

results = mutant_client.get_results()

### Inspect the results

# These are inputs in the unlabeled dataset which Chroma has recommended for labeling to optimally improve model performance.
# Display some of the images chroma suggests to label
raw_data = datasets.mnist.read_image_file("../data/CustomDataset/raw/train-images-idx3-ubyte")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

fig, axs = plt.subplots(2, 5, figsize=(15, 6))
# fig.subplots_adjust(hspace = .5, wspace=.001)
axs = axs.ravel()

for i in range(10):
    index = int(results[i].split("-")[-1])
    img = raw_data[index,:,:]
    img = Image.fromarray(img.numpy(), mode="L")
    axs[i].imshow(img, cmap='gray')
    axs[i].axis('off')