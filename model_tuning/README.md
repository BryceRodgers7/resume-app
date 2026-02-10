# Image Classifier Training Guide

This directory contains the training script for the bird/plane/superman image classifier with out-of-distribution (OOD) detection.

## Overview

The model uses **two complementary strategies** to detect images that don't belong to any trained category:

1. **Explicit "Other" Class**: Train on diverse images that are NOT birds/planes/superman
2. **Entropy-Based Detection**: Analyze prediction uncertainty to catch novel image types

## Dataset Setup

### Directory Structure

Create the following directory structure:

```
model_tuning/dataset/
    ├── train/
    │   ├── bird/           # Bird images for training
    │   ├── plane/          # Plane images for training
    │   ├── superman/       # Superman images for training
    │   └── other/          # Diverse "other" images for training
    └── val/
        ├── bird/           # Bird images for validation
        ├── plane/          # Plane images for validation
        ├── superman/       # Superman images for validation
        └── other/          # Diverse "other" images for validation
```

### Collecting "Other" Class Images

The "other" class should contain **diverse images** that are NOT birds, planes, or superman. Aim for variety to help the model learn what doesn't belong in the main categories.

#### Recommended Categories for "Other" Class:

1. **Common Objects** (20-30% of "other" dataset)
   - Cars, trucks, motorcycles
   - Furniture (chairs, tables, couches)
   - Food items
   - Electronics
   - Tools and equipment

2. **People & Activities** (20-30%)
   - People portraits
   - People doing sports
   - People at work
   - Groups of people
   - Close-up faces

3. **Nature & Landscapes** (15-20%)
   - Mountains, forests, beaches
   - Flowers and plants (not including birds)
   - Sunsets/sunrises
   - Natural scenery
   - Weather phenomena

4. **Animals (Non-Birds)** (15-20%)
   - Dogs, cats, horses
   - Wild animals (lions, elephants, etc.)
   - Marine life (fish, dolphins)
   - Insects
   - Reptiles

5. **Buildings & Architecture** (10-15%)
   - Houses, skyscrapers
   - Bridges, monuments
   - Interior rooms
   - Street scenes
   - Urban landscapes

6. **Abstract & Miscellaneous** (5-10%)
   - Abstract art
   - Patterns and textures
   - Text/documents
   - Signs and symbols
   - Screenshots from games/apps

### Image Sources

You can collect images from:
- **Open datasets**: ImageNet, COCO, Open Images
- **Creative Commons**: Wikimedia Commons, Unsplash, Pexels
- **Your own photos**: Take pictures of everyday objects
- **Web scraping**: Use tools like `google-images-download` (respect copyright)

### Dataset Size Recommendations

| Split | Bird | Plane | Superman | Other | Total |
|-------|------|-------|----------|-------|-------|
| **Train** | 100-500 | 100-500 | 100-500 | 300-1500 | 600-3000 |
| **Val** | 20-100 | 20-100 | 20-100 | 60-300 | 120-600 |

**Important Notes:**
- The "other" class should have **more images** than individual classes (2-3x)
- More diversity in "other" = better OOD detection
- Validation split should be ~20% of total dataset

## Training the Model

### 1. Prepare Your Dataset

Ensure you have images in all four class folders for both train and val splits.

### 2. Run Training Script

```bash
cd model_tuning
python train_classifier.py
```

### 3. Two-Phase Training Strategy

The script uses a **progressive unfreezing** approach for better results:

**Phase 1 - Warm-up (10 epochs)**
- Freezes entire ResNet backbone
- Trains only the classification head
- Learning rate: 0.001 (higher for training from scratch)
- Goal: Let the head learn good representations

**Phase 2 - Fine-tuning (30 epochs)**
- Unfreezes last ResNet block (layer4) + head
- Keeps earlier layers frozen (conv1, layer1-3)
- Learning rate: 0.0001 (10x lower for fine-tuning)
- Goal: Adapt deeper features to your specific task

**Why This Works:**
- Prevents catastrophic forgetting of pretrained ImageNet features
- Head learns task-specific patterns first
- Then deeper layers adapt to your data
- Results in better accuracy and generalization

**Total Training Time:** 40 epochs (~20-30 minutes on CPU, 5-10 minutes on GPU)

### 4. Monitor Training

The script will output:
- Phase 1 and Phase 2 progress separately
- Training and validation loss/accuracy per epoch
- Best validation accuracy achieved
- Trainable parameter counts for each phase

### 5. Training Configuration

Edit `train_classifier.py` to modify:

```python
CONFIG = {
    'phase1_epochs': 10,           # Warm-up epochs (head only)
    'phase2_epochs': 30,           # Fine-tuning epochs (layer4 + head)
    'batch_size': 32,              # Adjust based on GPU memory
    'phase1_lr': 0.001,            # Learning rate for phase 1
    'phase2_lr': 0.0001,           # Learning rate for phase 2 (10x lower)
    'entropy_threshold': 0.7,      # Adjust based on validation performance
}
```

### 5. Model Output

After training, the model will be saved to:
- `../models/bird_plane_superman_classifier_latest.pth` - Model weights
- `../models/classifier_metadata.json` - Model configuration and class names

## Entropy Threshold Tuning

The `entropy_threshold` determines when to classify predictions as "other" based on uncertainty.

### Default: 0.7

- **Lower threshold (0.5-0.65)**: More aggressive - catches more OOD images but may have false positives
- **Higher threshold (0.75-0.85)**: More conservative - fewer false positives but may miss some OOD images

### How to Tune:

1. Train your model
2. Test on validation images (both in-distribution and OOD)
3. Look at entropy values in the UI
4. Adjust threshold in `train_classifier.py` CONFIG
5. No need to retrain - just update `classifier_metadata.json` and reload the app

## Testing Your Model

After training, test the model in the Streamlit app:

1. Start the app: `streamlit run app.py`
2. Navigate to "Image Classifier" page
3. Upload test images:
   - ✅ Images from trained categories (should be confident)
   - ✅ Images from "other" class (should detect as "other")
   - ✅ Completely novel images (should detect via high entropy)

### Good Test Cases:

- **True Positives**: Clear bird/plane/superman images → Should classify correctly
- **True Negatives**: Cars, people, buildings → Should classify as "other"
- **Edge Cases**: Bird-shaped plane, cartoon superman, etc. → Watch entropy values

## Advanced Tips

### 1. Data Augmentation

The training script already includes:
- Random cropping and resizing
- Horizontal flipping
- Rotation (±15°)
- Color jittering

For more augmentation, modify `get_data_transforms()` in `train_classifier.py`.

### 2. Adjusting Training Phases

The default configuration (10 + 30 epochs) works well for most cases. To adjust:

**Shorter training (faster, less accurate):**
```python
'phase1_epochs': 5,
'phase2_epochs': 15,
```

**Longer training (slower, potentially more accurate):**
```python
'phase1_epochs': 15,
'phase2_epochs': 45,
```

**More aggressive fine-tuning (unfreeze more layers):**
```python
# In unfreeze_layer4() function, also unfreeze layer3:
def unfreeze_layer4(model):
    for param in model.layer3.parameters():  # Add this
        param.requires_grad = True
    for param in model.layer4.parameters():
        param.requires_grad = True
```

### 3. Learning Rate Tuning

The default learning rates (0.001 → 0.0001) work well. Adjust if needed:

**If training is unstable (loss jumping around):**
```python
'phase1_lr': 0.0005,  # Lower
'phase2_lr': 0.00005,  # Lower
```

**If training is too slow (loss decreasing very slowly):**
```python
'phase1_lr': 0.002,   # Higher
'phase2_lr': 0.0002,  # Higher
```

### 4. Ensemble Models

Train multiple models with different random seeds and ensemble their predictions for even better OOD detection.

## Troubleshooting

### Issue: Model always predicts "other"
**Solution**: Lower entropy threshold or collect more diverse training data for bird/plane/superman classes

### Issue: Model never predicts "other" for unfamiliar images
**Solution**: 
1. Increase entropy threshold
2. Add more diverse images to "other" class
3. Check that "other" class is properly loaded (should be in alphabetical position)

### Issue: Training loss not decreasing
**Solution**: 
1. Lower learning rate (0.0001)
2. Unfreeze more layers
3. Check dataset labels are correct
4. Ensure images are loading properly

### Issue: Overfitting (train acc high, val acc low)
**Solution**: 
1. Add more data augmentation
2. Increase dropout rate
3. Collect more training data
4. Use regularization (weight decay)

## Need Help?

- Check training logs for errors
- Verify dataset structure matches expected format
- Test with a small dataset first (10-20 images per class)
- Monitor entropy values in the UI to calibrate threshold

## References

- **Transfer Learning**: [PyTorch Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- **Entropy for OOD Detection**: [Hendrycks & Gimpel, 2017](https://arxiv.org/abs/1610.02136)
- **ResNet Architecture**: [He et al., 2015](https://arxiv.org/abs/1512.03385)
