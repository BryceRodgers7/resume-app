# 🚀 Quick Start Guide: Bird/Plane/Superman Classifier

This guide will help you train your first image classifier in just a few steps!

## 📋 Prerequisites

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- PyTorch & torchvision
- Pillow (PIL)
- numpy

## 🎯 Step-by-Step Tutorial

### Step 1: Create Dataset Structure

Run the setup script to create the necessary folders:

```bash
cd model_tuning
python download_sample_data.py
```

This creates:
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

### Step 2: Download Training Images (Fully Automated!)

**No manual downloading required!** Use the automated downloader:

```bash
# Easiest: No API key needed
python download_images.py

# Or with better quality (free Bing API key)
$env:BING_API_KEY="your-key"
python download_images.py --bing

# Or highest quality (free Unsplash API key)
$env:UNSPLASH_API_KEY="your-key"
python download_images.py --unsplash
```

**What it does automatically:**
- Downloads 100 training images per category
- Downloads 25 validation images per category
- Proper train/val split
- Total: 375 images in 10-20 minutes

**Categories downloaded:**
- 🐦 Birds: Eagles, parrots, owls, sparrows, hawks, seagulls
- ✈️ Planes: Commercial jets, fighter jets, small aircraft
- 🦸 Superman: Movie scenes, comic art, costume photos

No manual work needed - just run the command and wait!

### Step 3: Train the Model

Once you have your images ready:

```bash
python train_classifier.py
```

**What to expect:**
- Training will take 5-30 minutes depending on your hardware
- GPU: Much faster (if available, will be used automatically)
- CPU: Slower but will work fine
- You'll see progress for each epoch showing loss and accuracy

**Example output:**
```
Training on cuda
============================================================

Epoch 1/10
------------------------------------------------------------
Train Loss: 0.8234 Acc: 0.6500
Val Loss: 0.5123 Acc: 0.7800

Epoch 2/10
------------------------------------------------------------
Train Loss: 0.4567 Acc: 0.8200
Val Loss: 0.3891 Acc: 0.8600

...

Training Complete! Best Val Acc: 0.9200
Model saved to: models/bird_plane_superman_classifier_latest.pth
```

### Step 4: Test Your Model

Verify the model works correctly:

```bash
python test_model.py
```

This will check:
- ✓ Model file exists
- ✓ Model can be loaded
- ✓ Inference works correctly

### Step 5: Use in Streamlit App

Start the Streamlit app:

```bash
cd ..
streamlit run app.py
```

Then:
1. Navigate to "🖼️ Custom Image Classifier" page
2. Upload an image
3. Click "Classify Image"
4. See the results!

## 💡 Tips for Better Results

### If accuracy is low:

1. **Add more images** - More data = better model
   - Aim for 100+ training images per category
   - Ensure validation images are different from training

2. **Improve image diversity**
   - Different lighting conditions
   - Different angles and perspectives
   - Different backgrounds

3. **Balance your dataset**
   - Similar number of images in each category
   - If one category has way more images, the model may be biased

4. **Train for more epochs**
   - Edit `train_classifier.py` and change `num_epochs` from 10 to 20 or 30
   - Monitor validation accuracy - stop if it starts decreasing (overfitting)

5. **Use higher quality images**
   - Clear, in-focus images
   - Good lighting
   - Subject clearly visible

### If training is slow:

1. **Use GPU** if available (automatically detected)
2. **Reduce batch size** in `train_classifier.py`:
   ```python
   'batch_size': 16,  # Instead of 32
   ```
3. **Use fewer training images** for quick prototyping
4. **Reduce number of epochs** for testing

### If you get "out of memory" errors:

1. Reduce `batch_size` in `train_classifier.py`:
   ```python
   'batch_size': 8,  # or even 4
   ```
2. Close other applications using GPU/RAM
3. Use CPU instead of GPU (slower but uses less memory)

## 📊 Understanding Your Results

### Training Metrics

- **Train Loss**: Should decrease over epochs (lower is better)
- **Train Acc**: Should increase over epochs (higher is better)
- **Val Loss**: Should decrease but may plateau
- **Val Acc**: Most important metric - aim for 80%+ for good performance

### What's Good Accuracy?

- **90%+**: Excellent! Your model is working great
- **80-90%**: Good - model is useful
- **70-80%**: Okay - may need more training or data
- **<70%**: Needs improvement - add more data or train longer

## 🔧 Customization

### Want to classify different things?

1. Change the class names in `train_classifier.py`:
   ```python
   'class_names': ['cat', 'dog', 'rabbit', 'other'],
   ```

2. Update the folder names in `dataset/train/` and `dataset/val/`

3. Update `pages/image_classifier.py` title and descriptions

### Advanced: Fine-tune all layers

In `train_classifier.py`, comment out the freeze lines:

```python
# Freeze early layers (optional - comment out to fine-tune all layers)
# for param in model.parameters():
#     param.requires_grad = False
```

This allows the entire model to be trained, which may improve accuracy but takes longer.

## 🐛 Troubleshooting

### "Dataset not found" error
- Make sure you ran `download_sample_data.py`
- Check that images are in the correct folders
- Verify folder structure matches the expected layout

### "Model not found" in Streamlit app
- Run `train_classifier.py` first
- Check that `models/bird_plane_superman_classifier_latest.pth` exists
- Run `test_model.py` to verify

### Poor predictions
- Add more training images
- Ensure validation set is representative
- Train for more epochs
- Check image quality

### Training is very slow
- Use GPU if available
- Reduce batch size or number of epochs
- Use fewer images for quick testing

## 🚀 Advanced Features

### Improve Accuracy with Error Analysis

After training, find problematic images:

```bash
python analyze_training_errors.py
```

This creates an HTML report showing images with highest loss (worst predictions). Review these images and delete any that are:
- Mislabeled
- Blurry or poor quality
- Ambiguous

Then retrain for better accuracy!

### Fully Automated Image Collection

All image downloading is automated - no manual work required!

```bash
# Easiest: No API key needed (DuckDuckGo)
python download_images.py

# Better quality: Free Bing API key from Azure
python download_images.py --bing

# Highest quality: Free Unsplash API key
python download_images.py --unsplash
```

Downloads 375 images automatically in 10-20 minutes. See `IMAGE_COLLECTION_GUIDE.md` for details.

### Understanding "Other" Classification

This classifier doesn't have an "other" training class! Instead:
- It trains on only bird, plane, and superman
- During inference, if confidence is below 60%, it's classified as "other"
- This is more robust than trying to train on miscellaneous objects

You can adjust the confidence threshold in `train_classifier.py` (0.5-0.7 recommended).

## 📚 Next Steps

Once you have a working model:

1. **Run error analysis** to find and remove bad images
2. **Collect more data** to improve accuracy
3. **Adjust confidence threshold** for better "other" detection
4. **Try different images** in the web app
5. **Customize** for your own use case
6. **Share** your model with others!

## 🎓 Learning Resources

- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [Transfer Learning Guide](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [Image Classification Best Practices](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)

---

Happy training! 🚀

If you have questions or issues, check the main `README.md` or create an issue in the repository.

