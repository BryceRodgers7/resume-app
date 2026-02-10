"""
Image Classifier Training Script
Trains a model to classify images as: bird, plane, superman, or other

TWO-PHASE TRAINING STRATEGY:
Phase 1 (10 epochs): Warm-up - Train classification head only (backbone frozen)
Phase 2 (30 epochs): Fine-tune - Unfreeze layer4 + head with lower learning rate

This progressive unfreezing approach:
- Prevents catastrophic forgetting of pretrained features
- Allows the head to learn good representations first
- Then fine-tunes deeper layers for task-specific features
- Results in better accuracy and generalization

Dataset Structure Expected:
model_tuning/dataset/
    ├── train/
    │   ├── bird/
    │   ├── plane/
    │   ├── superman/
    │   └── other/       # Add diverse images that are NOT birds/planes/superman
    └── val/
        ├── bird/
        ├── plane/
        ├── superman/
        └── other/       # Add diverse images for validation

The "other" class should contain diverse images like:
- Common objects (cars, furniture, food)
- People doing various activities
- Landscapes and buildings
- Animals that aren't birds
- Abstract patterns and textures

This helps the model learn to distinguish out-of-distribution images more reliably.

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
    # Two-phase training strategy
    'phase1_epochs': 10,      # Warm-up: train head only
    'phase2_epochs': 30,      # Fine-tune: train head + layer4
    'batch_size': 32,
    'phase1_lr': 0.001,       # Higher LR for training head from scratch
    'phase2_lr': 0.0001,      # Lower LR for fine-tuning
    'num_classes': 4,  # bird, plane, superman, other
    'class_names': ['bird', 'other', 'plane', 'superman'],  # Alphabetical order (how ImageFolder loads them)
    'entropy_threshold': 0.7,  # High entropy (0-1) indicates uncertainty -> classify as "other"
    'img_size': 224,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

def get_data_transforms():
    """Define image transformations for training and validation"""
    data_transforms = {
        'train': transforms.Compose([
            # Randomly crop and resize to 224x224 - adds scale and position variance for data augmentation
            transforms.RandomResizedCrop(CONFIG['img_size']),
            # Randomly flip images horizontally with 50% probability - helps model learn orientation invariance
            transforms.RandomHorizontalFlip(),
            # Randomly rotate images up to 15 degrees in either direction - handles slight angle variations
            transforms.RandomRotation(15),
            # Randomly adjust brightness, contrast, and saturation - makes model robust to lighting conditions
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            # Convert PIL image to PyTorch tensor with values in range [0, 1]
            transforms.ToTensor(),
            # Normalize using ImageNet mean and std dev - required for pretrained ResNet models
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            # Resize shortest side to 256 pixels while maintaining aspect ratio
            transforms.Resize(256),
            # Crop center 224x224 region - deterministic for consistent validation
            transforms.CenterCrop(CONFIG['img_size']),
            # Convert PIL image to PyTorch tensor with values in range [0, 1]
            transforms.ToTensor(),
            # Normalize using ImageNet mean and std dev - must match training normalization
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    return data_transforms

def create_model(num_classes):
    """Create a ResNet18 model with custom final layer"""
    model = models.resnet18(pretrained=True)
    
    # Freeze all layers initially (will be unfrozen in phase 2)
    for param in model.parameters():
        param.requires_grad = False
    
    # Replace final layer with custom head
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    
    return model

def unfreeze_layer4(model):
    """Unfreeze the last ResNet block (layer4) for fine-tuning"""
    print("\n🔓 Unfreezing layer4 for fine-tuning...")
    for param in model.layer4.parameters():
        param.requires_grad = True
    
    # Count trainable parameters
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"   Trainable parameters: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")

def get_trainable_params(model):
    """Get list of trainable parameters"""
    return [p for p in model.parameters() if p.requires_grad]

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
        'entropy_threshold': config['entropy_threshold'],
        'img_size': config['img_size'],
        'model_architecture': 'resnet18',
        'training_strategy': 'two_phase',
        'phase1_epochs': config['phase1_epochs'],
        'phase2_epochs': config['phase2_epochs'],
        'phase1_lr': config['phase1_lr'],
        'phase2_lr': config['phase2_lr'],
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
        print("    │   ├── superman/")
        print("    │   └── other/      # Diverse images NOT in the above categories")
        print("    └── val/")
        print("        ├── bird/")
        print("        ├── plane/")
        print("        ├── superman/")
        print("        └── other/      # Diverse images for validation")
        print("\n💡 TIP: The 'other' class should contain diverse images like:")
        print("   - Common objects (cars, furniture, food)")
        print("   - People, landscapes, buildings")
        print("   - Animals that aren't birds")
        print("   - Abstract patterns")
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
    
    # Count initial trainable parameters (only head)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"   Trainable parameters: {trainable:,} / {total:,} ({100*trainable/total:.1f}%)")
    
    # Loss function
    criterion = nn.CrossEntropyLoss()
    
    # ============================================================================
    # PHASE 1: Warm-up - Train head only with higher learning rate
    # ============================================================================
    print("\n" + "=" * 70)
    print("🔥 PHASE 1: WARM-UP - Training classification head only")
    print("=" * 70)
    print(f"   Epochs: {CONFIG['phase1_epochs']}")
    print(f"   Learning rate: {CONFIG['phase1_lr']}")
    print(f"   Frozen: All backbone layers (conv1, layer1-4)")
    print(f"   Trainable: Classification head only")
    
    # Create optimizer for phase 1 (only trainable params)
    optimizer_phase1 = optim.Adam(get_trainable_params(model), lr=CONFIG['phase1_lr'])
    
    # Train phase 1
    model, history_phase1 = train_model(
        model, dataloaders, criterion, optimizer_phase1, 
        CONFIG['phase1_epochs'], CONFIG['device']
    )
    
    # ============================================================================
    # PHASE 2: Fine-tune - Unfreeze layer4 + head with lower learning rate
    # ============================================================================
    print("\n" + "=" * 70)
    print("🎯 PHASE 2: FINE-TUNING - Unfreezing layer4 + head")
    print("=" * 70)
    print(f"   Epochs: {CONFIG['phase2_epochs']}")
    print(f"   Learning rate: {CONFIG['phase2_lr']} (10x lower)")
    print(f"   Frozen: conv1, layer1-3")
    print(f"   Trainable: layer4 + classification head")
    
    # Unfreeze layer4
    unfreeze_layer4(model)
    
    # Create new optimizer for phase 2 with lower learning rate
    optimizer_phase2 = optim.Adam(get_trainable_params(model), lr=CONFIG['phase2_lr'])
    
    # Train phase 2
    model, history_phase2 = train_model(
        model, dataloaders, criterion, optimizer_phase2, 
        CONFIG['phase2_epochs'], CONFIG['device']
    )
    
    # Combine training histories
    history = {
        'phase1': history_phase1,
        'phase2': history_phase2,
        'train_loss': history_phase1['train_loss'] + history_phase2['train_loss'],
        'train_acc': history_phase1['train_acc'] + history_phase2['train_acc'],
        'val_loss': history_phase1['val_loss'] + history_phase2['val_loss'],
        'val_acc': history_phase1['val_acc'] + history_phase2['val_acc'],
    }
    
    # Save the model
    save_model(model, history, CONFIG)
    
    print("\n" + "=" * 70)
    print("✅ TWO-PHASE TRAINING COMPLETE!")
    print("=" * 70)
    print(f"   Phase 1 (head only): {CONFIG['phase1_epochs']} epochs")
    print(f"   Phase 2 (layer4 + head): {CONFIG['phase2_epochs']} epochs")
    print(f"   Total epochs: {CONFIG['phase1_epochs'] + CONFIG['phase2_epochs']}")
    print(f"   Best validation accuracy: {max(history['val_acc']):.4f}")
    print("=" * 70)

if __name__ == '__main__':
    main()

