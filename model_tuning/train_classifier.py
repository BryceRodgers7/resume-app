"""
Image Classifier Training Script
Trains a model to classify images as: bird, plane, superman, or other

Dataset Structure Expected:
model_tuning/dataset/
    ├── train/
    │   ├── bird/
    │   ├── plane/
    │   └── superman/
    └── val/
        ├── bird/
        ├── plane/
        └── superman/

Note: No "other" class needed! Images with low confidence will be classified as "other" automatically.

Usage:
    python train_classifier.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os
from pathlib import Path
import json
from datetime import datetime

# Configuration
CONFIG = {
    'data_dir': Path(__file__).parent / 'dataset',
    'model_save_dir': Path(__file__).parent.parent / 'models',
    'num_epochs': 10,
    'batch_size': 32,
    'learning_rate': 0.001,
    'num_classes': 3,  # Only bird, plane, superman
    'class_names': ['bird', 'plane', 'superman'],
    'confidence_threshold': 0.6,  # Below this = "other"
    'img_size': 224,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

def get_data_transforms():
    """Define image transformations for training and validation"""
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(CONFIG['img_size']),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(CONFIG['img_size']),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    return data_transforms

def create_model(num_classes):
    """Create a ResNet18 model with custom final layer"""
    model = models.resnet18(pretrained=True)
    
    # Freeze early layers (optional - comment out to fine-tune all layers)
    for param in model.parameters():
        param.requires_grad = False
    
    # Replace final layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    
    return model

def train_model(model, dataloaders, criterion, optimizer, num_epochs, device):
    """Train the model"""
    print(f"\nTraining on {device}")
    print("=" * 60)
    
    best_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch + 1}/{num_epochs}')
        print('-' * 60)
        
        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_corrects = 0
            
            # Iterate over data
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                # Zero the parameter gradients
                optimizer.zero_grad()
                
                # Forward pass
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    
                    # Backward pass and optimize only in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                # Statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            
            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)
            
            print(f'{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            
            # Store history
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(float(epoch_acc))
            
            # Deep copy the model if it's the best so far
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
    
    print(f'\n{"=" * 60}')
    print(f'Training Complete! Best Val Acc: {best_acc:.4f}')
    
    return model, history

def save_model(model, history, config):
    """Save the trained model and metadata"""
    # Create models directory if it doesn't exist
    config['model_save_dir'].mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f'bird_plane_superman_classifier_{timestamp}.pth'
    model_path = config['model_save_dir'] / model_filename
    
    # Save model state dict
    torch.save(model.state_dict(), model_path)
    print(f'\nModel saved to: {model_path}')
    
    # Also save as 'latest' for easy loading
    latest_path = config['model_save_dir'] / 'bird_plane_superman_classifier_latest.pth'
    torch.save(model.state_dict(), latest_path)
    print(f'Latest model saved to: {latest_path}')
    
    # Save metadata
    metadata = {
        'class_names': config['class_names'],
        'num_classes': config['num_classes'],
        'confidence_threshold': config['confidence_threshold'],
        'img_size': config['img_size'],
        'model_architecture': 'resnet18',
        'timestamp': timestamp,
        'training_history': history
    }
    
    metadata_path = config['model_save_dir'] / 'classifier_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f'Metadata saved to: {metadata_path}')

def main():
    """Main training function"""
    print("=" * 60)
    print("Bird/Plane/Superman Image Classifier Training")
    print("=" * 60)
    
    # Check if dataset exists
    train_dir = CONFIG['data_dir'] / 'train'
    val_dir = CONFIG['data_dir'] / 'val'
    
    if not train_dir.exists() or not val_dir.exists():
        print("\n❌ ERROR: Dataset not found!")
        print(f"\nPlease create the following directory structure:")
        print(f"\n{CONFIG['data_dir']}/")
        print("    ├── train/")
        print("    │   ├── bird/")
        print("    │   ├── plane/")
        print("    │   └── superman/")
        print("    └── val/")
        print("        ├── bird/")
        print("        ├── plane/")
        print("        └── superman/")
        print("\nNote: No 'other' class needed!")
        print("Images with low confidence will be automatically classified as 'other'.")
        print("\nAdd images to each folder and run again.")
        return
    
    # Get data transforms
    data_transforms = get_data_transforms()
    
    # Load datasets
    print("\n📁 Loading datasets...")
    image_datasets = {
        'train': datasets.ImageFolder(train_dir, data_transforms['train']),
        'val': datasets.ImageFolder(val_dir, data_transforms['val'])
    }
    
    # Create dataloaders
    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=CONFIG['batch_size'], 
                          shuffle=True, num_workers=0),
        'val': DataLoader(image_datasets['val'], batch_size=CONFIG['batch_size'], 
                        shuffle=False, num_workers=0)
    }
    
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    print(f"Training samples: {dataset_sizes['train']}")
    print(f"Validation samples: {dataset_sizes['val']}")
    print(f"Classes: {image_datasets['train'].classes}")
    
    # Create model
    print("\n🤖 Creating model...")
    model = create_model(CONFIG['num_classes'])
    model = model.to(CONFIG['device'])
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'])
    
    # Train the model
    model, history = train_model(
        model, dataloaders, criterion, optimizer, 
        CONFIG['num_epochs'], CONFIG['device']
    )
    
    # Save the model
    save_model(model, history, CONFIG)
    
    print("\n✅ Training complete!")

if __name__ == '__main__':
    main()

