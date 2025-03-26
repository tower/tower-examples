
import torch
from torch.utils.data import Dataset
from torchvision import datasets, models, transforms
from torchvision.datasets.folder import default_loader  # private API
import torch.nn.functional as F

from PIL import Image
import pandas as pd
import numpy as np
import json

from typing import (
    Any)
from core.actions import Action

class LocalFileDataset(Dataset):
    def __init__(self, paths, transform=None):
        self.paths = paths
        self.transform = transform
    def __len__(self):
        return len(self.paths)
    def __getitem__(self, index):
        object = default_loader(self.paths[index])
        if self.transform is not None:
            transformed_object = self.transform(object)
        return transformed_object

class ImagenetLabeler:
    def __init__(self, path):
        self.path = path
        # https://github.com/anishathalye/imagenet-simple-labels/tree/master
        with open(path) as f:
            self.labels = json.load(f)

    def labels_of_classes(self,classes:np.ndarray, probs:np.ndarray=None):
        l_out = []
        numrows = classes.shape[0]
        numclasses = classes.shape[1]
        r_labels = np.empty(numrows)
        for i in range(numrows):
            c_row = classes[i]
            p_row = probs[i] if probs is not None else None
            l_row = [self.labels[j] for j in c_row]
            s = '[{}], '.join(l_row) + '[{}]'
            p_list = list(p_row)
            s = s.format(*p_list)
            l_out.append(s)
        return l_out

    def top_n_classes(self, n, probs: np.ndarray):
        numrows = probs.shape[0]
        r_classes = np.zeros((numrows,n),int)
        r_probs = np.zeros((numrows,n),float)
        for i in range(numrows):
            prob = probs[i]
            sorted = np.argsort(prob)
            top_n_idx = sorted[-n:]
            prob_of_top_n = prob[top_n_idx]
            top_n_idx_desc = top_n_idx[::-1]
            prob_of_top_n_desc = prob_of_top_n[::-1]
            r_classes[i]=top_n_idx_desc
            r_probs[i]=prob_of_top_n_desc
        return r_classes, r_probs


class InferWithPytorch(Action):

    device_type: str = ""

    def __init__(self, actionname: str = None, device_type: str = None):
        super().__init__(actionname)

        if device_type is None:
            device_type = "cpu"

        self.device_type = device_type
        self.device = torch.device(self.device_type)

        # First prepare the transformations: resize the image to what the model was trained on and convert it to a tensor
        # transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])

        self.data_transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])


        # Download the model if it's not there already. It will take a bit on the first run, after that it's fast
        self.model = models.resnet50(pretrained=True)

        # Send the model to the GPU
        self.model.to(self.device)

        # Set layers such as dropout and batchnorm in evaluation mode
        self.model.eval()

    def do(self, *args:Any, **kwargs: Any):

        out = self.batch_inference(kwargs['paths'])
        return out

    def single_inference(self,image_path):
        # Load the image
        image = Image.open(image_path)
        # Now apply the transformation, and create a batch of size 1
        image = self.data_transform(image).unsqueeze(0)

        with torch.no_grad():
            # send the image to the GPU
            image = image.to(self.device)
            # Get the 1000-dimensional model output
            predictions = self.model(image)
            # Create probabilities
            probs = F.softmax(predictions, dim=1)
            probs = probs.cpu().numpy()

        return probs


    def batch_inference(self, paths):
        images = LocalFileDataset(paths, transform=self.data_transform)
        loader = torch.utils.data.DataLoader(images, batch_size=50, num_workers=0)

        all_probs = []
        with torch.no_grad():
            for batch in loader:
                batch = batch.to(self.device)
                predictions = self.model(batch)
                # Create probabilities
                probs = F.softmax(predictions, dim=1)
                probs = probs.cpu().numpy()
                all_probs.extend(list(probs))

        out = np.array(all_probs)
        return out



