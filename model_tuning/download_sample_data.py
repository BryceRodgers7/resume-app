"""
Sample Data Download Script
Downloads sample images for training the classifier

This script provides examples of how to collect images programmatically.
You can also manually add images to the dataset folders.
"""

import requests
from pathlib import Path
import os

def create_dataset_structure():
    """Create the dataset folder structure"""
    base_dir = Path(__file__).parent / 'dataset'
    
    categories = ['bird', 'plane', 'superman']  # No "other" class needed!
    splits = ['train', 'val']
    
    for split in splits:
        for category in categories:
            folder = base_dir / split / category
            folder.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {folder}")
    
    print("\n✅ Dataset structure created!")
    print(f"\nBase directory: {base_dir}")
    print("\n💡 Note: No 'other' class needed!")
    print("The model uses confidence thresholding to detect 'other' automatically.")
    print("\nNext steps:")
    print("1. Add training images to model_tuning/dataset/train/<category>/")
    print("2. Add validation images to model_tuning/dataset/val/<category>/")
    print("3. Aim for at least 50-100 images per category for training")
    print("4. Aim for at least 10-20 images per category for validation")
    print("\nImage sources:")
    print("- Download from Google Images")
    print("- Use image datasets (ImageNet, COCO, etc.)")
    print("- Take your own photos")
    print("- Use web scraping tools (with permission)")
    
    # Create a README in the dataset folder
    readme_path = base_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write("""# Dataset for Bird/Plane/Superman Classifier

## Directory Structure

```
dataset/
├── train/
│   ├── bird/       # Training images of birds
│   ├── plane/      # Training images of planes
│   └── superman/   # Training images of Superman
└── val/
    ├── bird/       # Validation images of birds
    ├── plane/      # Validation images of planes
    └── superman/   # Validation images of Superman

## No "Other" Class!

This classifier uses **confidence thresholding** instead of an "other" class:
- Train only on bird, plane, and superman images
- During inference, if confidence is below threshold (default 60%), it's classified as "other"
- This is more robust than trying to train on miscellaneous "other" images!
```

## Data Collection Tips

1. **Variety**: Include different angles, lighting conditions, and backgrounds
2. **Balance**: Try to have similar numbers of images in each category
3. **Quality**: Use clear, well-lit images
4. **Validation**: Make sure validation images are different from training images

## Recommended Image Counts

- Minimum: 50 train + 10 val per category
- Recommended: 100+ train + 20+ val per category
- More data = Better model!

## Image Sources

### Birds
- Search for: eagles, sparrows, owls, parrots, etc.

### Planes
- Search for: commercial jets, fighter jets, prop planes, etc.

### Superman
- Search for: Superman photos, comics, movie stills, etc.


## Data Ethics

- Only use images you have rights to use
- Respect copyright and licensing
- Consider using Creative Commons licensed images
- For commercial use, ensure proper licensing
""")
    print(f"\n📝 README created at: {readme_path}")

def main():
    """Main function"""
    print("=" * 60)
    print("Dataset Preparation Tool")
    print("=" * 60)
    print()
    
    create_dataset_structure()
    
    print("\n" + "=" * 60)
    print("Dataset structure ready for images!")
    print("=" * 60)

if __name__ == '__main__':
    main()

