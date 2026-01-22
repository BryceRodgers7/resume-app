"""
Test script to verify the trained model works correctly
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import json

def test_model():
    """Test if the model can be loaded"""
    print("=" * 60)
    print("Model Test Script")
    print("=" * 60)
    
    model_dir = Path(__file__).parent.parent / 'models'
    model_path = model_dir / 'bird_plane_superman_classifier_latest.pth'
    metadata_path = model_dir / 'classifier_metadata.json'
    
    # Check if files exist
    print("\n1. Checking for model files...")
    if not model_path.exists():
        print(f"   ❌ Model file not found: {model_path}")
        print("\n   Please train the model first:")
        print("   python train_classifier.py")
        return False
    else:
        print(f"   ✓ Model file found: {model_path}")
    
    if not metadata_path.exists():
        print(f"   ⚠️  Metadata file not found: {metadata_path}")
        print("   Using default configuration")
        class_names = ['bird', 'plane', 'superman']
        num_classes = 3
    else:
        print(f"   ✓ Metadata file found: {metadata_path}")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        class_names = metadata['class_names']
        num_classes = metadata['num_classes']
        print(f"\n   Classes: {class_names}")
        print(f"   Image size: {metadata['img_size']}")
        print(f"   Architecture: {metadata['model_architecture']}")
    
    # Try to load the model
    print("\n2. Loading model...")
    try:
        model = models.resnet18(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        print("   ✓ Model loaded successfully!")
    except Exception as e:
        print(f"   ❌ Error loading model: {str(e)}")
        return False
    
    # Test inference
    print("\n3. Testing inference...")
    try:
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            output = model(dummy_input)
            probabilities = torch.nn.functional.softmax(output, dim=1)
        
        print("   ✓ Inference successful!")
        print(f"   Output shape: {output.shape}")
        print(f"   Sample probabilities: {probabilities[0].numpy()}")
    except Exception as e:
        print(f"   ❌ Error during inference: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Model is ready to use.")
    print("=" * 60)
    print("\nYou can now use the model in the Streamlit app:")
    print("streamlit run app.py")
    
    return True

if __name__ == '__main__':
    test_model()

