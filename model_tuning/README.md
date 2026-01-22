# Image Classifier Model Tuning

This folder contains scripts for training a custom image classifier to identify:
- 🐦 **Birds**
- ✈️ **Planes**
- 🦸 **Superman**
- 📦 **Other** (detected via confidence thresholding - no training needed!)

## Quick Start

### 1. Prepare Your Dataset

First, create the dataset structure and add images:

```bash
python download_sample_data.py
```

This will create:
```
model_tuning/dataset/
├── train/
│   ├── bird/
│   ├── plane/
│   ├── superman/
│   └── other/
└── val/
    ├── bird/
    ├── plane/
    ├── superman/
    └── other/
```

### 2. Download Images (Automated!)

Use the automated downloader - no manual collection needed:

```bash
# No API key needed (DuckDuckGo)
python download_images.py

# Better quality with free Bing API key
python download_images.py --bing

# Highest quality with free Unsplash API key
python download_images.py --unsplash
```

**Automatically downloads:**
- Training: 100 images per category
- Validation: 25 images per category
- Total: 375 images in 10-20 minutes

### 3. Train the Model

Once you have images in the dataset folders:

```bash
python train_classifier.py
```

The training script will:
- Load and preprocess your images
- Train a ResNet18 model using transfer learning
- Save the trained model to `../models/`
- Create metadata about the training

### 4. Use the Model

The trained model will be saved as:
- `models/bird_plane_superman_classifier_latest.pth`
- `models/classifier_metadata.json`

You can then use the model in the Streamlit app via the "Custom Image Classifier" page.

## Training Configuration

You can modify these settings in `train_classifier.py`:

```python
CONFIG = {
    'num_epochs': 10,           # Number of training epochs
    'batch_size': 32,           # Batch size for training
    'learning_rate': 0.001,     # Learning rate
    'img_size': 224,            # Input image size
}
```

## Tips for Better Results

1. **More Data**: More images = better model
2. **Variety**: Include different angles, lighting, backgrounds
3. **Balance**: Similar numbers of images per category
4. **Quality**: Clear, well-focused images work best
5. **Validation Split**: Keep validation data separate from training

## Model Architecture

- **Base Model**: ResNet18 (pretrained on ImageNet)
- **Transfer Learning**: Fine-tuned on your custom dataset
- **Final Layers**: Custom classifier for 4 classes

## Advanced Features

### 🔍 Error Analysis Tool

Find and remove problematic images from your dataset:

```bash
python analyze_training_errors.py
```

This generates an HTML report showing images with highest prediction loss, helping you:
- Identify mislabeled images
- Find poor quality images
- Detect ambiguous cases
- Improve accuracy by cleaning your dataset

See `ADVANCED_FEATURES.md` for detailed guide.

### 📥 Automated Image Downloading

Download training images automatically:

```bash
python download_images.py
```

Supports:
- Bing Image Search API (with free Azure key)
- URL list files (urls_bird.txt, etc.)
- Manual collection guides

See `IMAGE_COLLECTION_GUIDE.md` for detailed instructions.

### 🎯 Confidence Thresholding (No "Other" Class)

This classifier uses a smart approach:
- Train on only 3 classes (bird, plane, superman)
- Use confidence threshold to detect "other"
- No need to collect miscellaneous "other" images!

If prediction confidence < 60% (configurable), it's classified as "other".

## Troubleshooting

**"Dataset not found" error:**
- Run `download_sample_data.py` first
- Make sure images are in the correct folders

**Low accuracy:**
- Add more training images
- Increase number of epochs
- Check image quality and variety

**Out of memory:**
- Reduce `batch_size` in CONFIG
- Use smaller images (reduce `img_size`)
- Use CPU instead of GPU

**Training is slow:**
- Use GPU if available (will automatically detect)
- Reduce number of epochs for quick tests
- Use fewer images for prototyping

