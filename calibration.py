# calibration.py
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import cv2
import numpy as np

class CalibrationDataset(Dataset):
    """Dataset for INT8 calibration."""
    def __init__(self, data_dir, transform=None, num_images=100):
        self.data_dir = Path(data_dir)
        self.images = sorted(list(self.data_dir.glob("*.jpg")))[:num_images]
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.transform:
            img = self.transform(img)

        return img

def get_calibration_loader(data_dir="data/nyu_data/data", batch_size=1, num_images=100):
    """
    Returns a DataLoader for calibration.
    """
    def preprocess(img):
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        return torch.from_numpy(img)

    dataset = CalibrationDataset(data_dir, transform=preprocess, num_images=num_images)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    return loader
