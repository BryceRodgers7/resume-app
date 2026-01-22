# Advanced Features Guide

This guide covers the advanced features of the image classifier system.

## Table of Contents

1. [Automated Image Downloading](#automated-image-downloading)
2. [Training Error Analysis](#training-error-analysis)
3. [Confidence Thresholding (No "Other" Class)](#confidence-thresholding)
4. [Best Practices](#best-practices)

---

## 1. Automated Image Downloading

### Overview

The `download_images.py` script helps you automatically collect training images from various sources.

### Methods Available

#### Method 1: Download from URL Files (Easiest)

1. Create text files with image URLs (one per line):
   - `urls_bird.txt`
   - `urls_plane.txt`
   - `urls_superman.txt`

2. Run the download script:
   ```bash
   python download_images.py
   ```

3. Choose whether to download to `train` or `val` folders

**Example URL file** (`urls_bird.txt`):
```
https://example.com/eagle.jpg
https://example.com/parrot.jpg
https://example.com/owl.jpg
...
```

#### Method 2: Bing Image Search API (Automated)

1. Get a free Bing Search API key:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create "Bing Search v7" resource
   - Copy API key

2. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:BING_API_KEY="your-key-here"
   
   # Linux/Mac
   export BING_API_KEY="your-key-here"
   ```

3. Run with Bing search:
   ```bash
   python download_images.py --bing
   ```

This will automatically search and download ~100 images per category!

#### Method 3: Auto-Detect (Easiest)

Let the script choose the best available method:
```bash
python download_images.py --auto
```

This will use DuckDuckGo by default (no API key), or automatically use Bing/Unsplash if you have API keys set.

### Copyright & Ethics

⚠️ **Important**: Always respect copyright and licensing!

- **For learning/personal projects**: Generally okay to use images
- **For commercial use**: Ensure proper licensing
- **Best practice**: Use Creative Commons or public domain images
- **Recommended**: Unsplash and Pexels provide free commercial licenses

---

## 2. Training Error Analysis

### Overview

The `analyze_training_errors.py` script helps you identify problematic images in your dataset by analyzing which images have the highest prediction loss.

### Why This Matters

Common problems in training datasets:
- **Mislabeled images**: Bird labeled as plane, etc.
- **Poor quality**: Blurry, dark, or unclear images
- **Ambiguous images**: Multiple objects in one image
- **Edge cases**: Unusual angles or partial objects

These problems hurt model accuracy. Finding and removing them improves performance!

### How to Use

1. **Train your model first**:
   ```bash
   python train_classifier.py
   ```

2. **Run error analysis**:
   ```bash
   python analyze_training_errors.py
   ```

3. **Choose dataset**: Select train or validation set to analyze

4. **Review HTML report**: Opens automatically showing worst images

5. **Delete bad images**: Remove problematic images from dataset folders

6. **Retrain**: Run training again for improved accuracy

### Understanding the Report

The HTML report shows:

**Overall Statistics:**
- Total images analyzed
- Current accuracy
- Number of correct predictions

**Worst Images Section:**
- Top 30 images with highest loss across all classes
- Red border = incorrect prediction
- Shows: loss value, true label, predicted label, confidence

**Per-Class Sections:**
- Top 20 worst images for each class
- Helps identify class-specific problems
- Class accuracy statistics

**What to Look For:**

1. **High loss + incorrect prediction**: Likely mislabeled or ambiguous
2. **High loss + correct prediction**: Poor quality or edge case
3. **Patterns**: If many images from same source have high loss, that source may be problematic

### Example Workflow

```bash
# Initial training
python train_classifier.py
# Result: 75% accuracy

# Analyze errors
python analyze_training_errors.py
# Choose: 1 (training set)
# Opens: error_analysis_train.html

# Review report and delete ~10 worst images
# Delete from dataset/train/<category>/ folders

# Retrain
python train_classifier.py
# Result: 82% accuracy (improved!)

# Repeat until satisfied
```

### Tips for Using Error Analysis

**When to analyze:**
- After initial training
- When accuracy plateaus
- Before deploying model

**What to remove:**
- Clearly mislabeled images
- Extremely blurry or dark images
- Images with multiple subjects
- Heavily cropped or partial objects

**What to keep:**
- Challenging but correctly labeled images (helps model learn!)
- Edge cases that are still valid
- Images with slight quality issues

**How many to remove:**
- Start with top 5-10 worst per class
- Don't remove more than 10-20% of dataset
- If removing many images, dataset quality needs improvement

---

## 3. Confidence Thresholding (No "Other" Class)

### Overview

This classifier uses an advanced approach: instead of training on an "other" class, it uses **confidence thresholding** to detect when an image doesn't match any trained category.

### Traditional Approach (Not Used Here)

```
Classes: bird, plane, superman, other
Problem: What is "other"? Cars? Dogs? Buildings? Everything else?
Issue: Hard to collect representative "other" images
Result: Model may misclassify anything unfamiliar as one of the main classes
```

### Our Approach (Better!)

```
Trained Classes: bird, plane, superman (only 3)
Inference: Check confidence score
  - If max confidence > threshold (60%): Use that class
  - If max confidence < threshold: Classify as "other"
```

### Why This Is Better

1. **No ambiguous "other" class**: Don't need to collect miscellaneous images
2. **More robust**: Naturally detects unfamiliar objects
3. **Adjustable**: Can tune threshold without retraining
4. **Cleaner dataset**: Only collect images of actual target classes

### How It Works

**During Training:**
- Train on only 3 classes: bird, plane, superman
- No "other" folder needed!
- Model learns to distinguish these 3 classes

**During Inference:**
```python
# Model predicts probabilities for each class
probabilities = model.predict(image)
# Example: [bird: 0.45, plane: 0.38, superman: 0.17]

max_prob = max(probabilities)  # 0.45 (bird)

if max_prob >= confidence_threshold:  # 0.60
    prediction = highest_class  # Would be "bird"
else:
    prediction = "other"  # None are confident enough

# In this example: max 0.45 < 0.60 → classified as "other"
```

### Adjusting the Confidence Threshold

**In Training** (`train_classifier.py`):
```python
CONFIG = {
    'confidence_threshold': 0.6,  # Change this value
    # 0.5 = 50% (more permissive, fewer "other")
    # 0.7 = 70% (more strict, more "other")
    # 0.6 = 60% (default, balanced)
}
```

**Guidelines:**
- **0.5-0.6 (50-60%)**: Balanced, good default
- **0.7+ (70%+)**: Conservative, only very confident predictions
- **<0.5 (<50%)**: Aggressive, rarely classifies as "other"

**When to adjust:**
- Too many false positives → Increase threshold
- Too many "other" classifications → Decrease threshold
- Test with validation images to find optimal value

### Testing Confidence Thresholding

After training, test with various images:

**Expected behavior:**
- Clear bird photo → High confidence (>80%) → "bird"
- Clear plane photo → High confidence (>80%) → "plane"
- Superman image → High confidence (>80%) → "superman"
- Car photo → Low confidence (<60%) → "other"
- Ambiguous image → Low confidence (<60%) → "other"
- Random object → Low confidence (<60%) → "other"

---

## 4. Best Practices

### Complete Workflow

```bash
# 1. Setup
cd model_tuning
python download_sample_data.py

# 2. Collect Images
# Option A: Manual (recommended)
# Download from Unsplash/Pexels to dataset/train/<category>/

# Option B: Automated
# Create urls_*.txt files or use Bing API
python download_images.py

# 3. Initial Training
python train_classifier.py

# 4. Test Model
python test_model.py

# 5. Analyze Errors
python analyze_training_errors.py
# Review HTML report

# 6. Clean Dataset
# Delete problematic images identified in analysis

# 7. Retrain
python train_classifier.py

# 8. Deploy
cd ..
streamlit run app.py

# 9. Test in Production
# Upload various test images
# Adjust confidence threshold if needed

# 10. Iterate
# Repeat steps 5-7 to improve further
```

### Quality Checklist

Before training, verify:

**Dataset Quality:**
- [ ] At least 50 images per class (100+ recommended)
- [ ] Images are clear and well-lit
- [ ] Subject is main focus of image
- [ ] Variety of angles and conditions
- [ ] No duplicates or near-duplicates
- [ ] Validation set is different from training

**Training Settings:**
- [ ] Confidence threshold set appropriately (0.5-0.7)
- [ ] Enough epochs (10-20 for most datasets)
- [ ] GPU available for faster training (optional)

**After Training:**
- [ ] Validation accuracy > 80%
- [ ] Per-class accuracy relatively balanced
- [ ] Model file saved successfully
- [ ] Test inference works

**After Error Analysis:**
- [ ] Reviewed worst 10 images per class
- [ ] Removed obvious problems
- [ ] Documented any patterns noticed
- [ ] Ready to retrain

### Performance Optimization

**For Better Accuracy:**
1. More diverse training images
2. Remove low-quality images via error analysis
3. Balance dataset (similar counts per class)
4. Train for more epochs
5. Adjust confidence threshold

**For Faster Training:**
1. Use GPU (automatically detected)
2. Reduce batch size if out of memory
3. Start with fewer images for prototyping
4. Use fewer epochs for quick iterations

**For Better "Other" Detection:**
1. Test with various non-target images
2. Adjust confidence threshold based on results
3. Monitor false positive rate
4. Consider retraining if main classes are confused

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Low overall accuracy (<70%) | Add more training images, increase epochs |
| One class has low accuracy | Add more images for that class, check for mislabeled images |
| Too many "other" classifications | Lower confidence threshold (e.g., 0.5) |
| False positives (wrong class) | Raise confidence threshold (e.g., 0.7) |
| Training very slow | Use GPU, reduce batch size, or use fewer images |
| Out of memory | Reduce batch_size in train_classifier.py |
| Model not loading in app | Run test_model.py to diagnose |

### Advanced Tips

**Data Augmentation:**
The training script already includes:
- Random cropping
- Horizontal flips
- Rotation (15°)
- Color jittering

These help the model generalize better!

**Transfer Learning:**
We use ResNet18 pretrained on ImageNet, which provides:
- Good initial features
- Faster training
- Better results with less data

**Fine-tuning Strategy:**
Current: Only final layers are trained (faster)
Alternative: Uncomment freeze lines in `train_classifier.py` to train all layers (slower but may improve accuracy)

---

## Summary

You now have a complete pipeline:

1. **📥 Download Images**: Automated or manual collection
2. **🎓 Train Model**: Using only 3 target classes
3. **🔍 Analyze Errors**: Find and remove problematic images
4. **🎯 Confidence Thresholding**: Robust "other" detection
5. **🔄 Iterate**: Continuous improvement

This approach provides:
- ✅ Cleaner datasets (no ambiguous "other" class)
- ✅ Better accuracy (error analysis removes bad images)
- ✅ Robust inference (confidence thresholding)
- ✅ Easy collection (automated downloading)

Happy training! 🚀

