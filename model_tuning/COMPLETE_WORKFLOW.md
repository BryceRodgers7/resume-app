# Complete Workflow Guide

This guide walks you through the entire process from scratch to a deployed, high-accuracy classifier.

## 🎯 Goal

Create a bird/plane/superman classifier with 85%+ accuracy using best practices.

## 📋 Prerequisites

```bash
cd model_tuning
pip install -r ../requirements.txt
```

---

## Phase 1: Initial Setup & Data Collection

### Step 1.1: Create Dataset Structure

```bash
python download_sample_data.py
```

**What this does:**
- Creates `dataset/train/` and `dataset/val/` folders
- Creates subfolders: `bird/`, `plane/`, `superman/`
- No "other" folder needed (uses confidence thresholding!)

### Step 1.2: Download Images (Fully Automated!)

**No manual downloading required!** Choose your method:

#### Option A: DuckDuckGo (Recommended - No API Key)

Fastest to get started:
```bash
python download_images.py
```

That's it! No setup, no API keys, downloads 375 images automatically in 15-20 minutes.

#### Option B: Bing API (Best Quality)

One-time setup for better results:
```bash
# 1. Get free API key from Azure Portal (1000 searches/month free)
# 2. Set environment variable
$env:BING_API_KEY="your-key-here"  # Windows
export BING_API_KEY="your-key-here"  # Linux/Mac

# 3. Run
python download_images.py --bing
```

#### Option C: Unsplash API (Highest Quality)

Professional photography:
```bash
# 1. Get free API key from unsplash.com/developers
# 2. Set environment variable
$env:UNSPLASH_API_KEY="your-key-here"  # Windows
export UNSPLASH_API_KEY="your-key-here"  # Linux/Mac

# 3. Run
python download_images.py --unsplash
```

**What gets downloaded automatically:**
- 100 training images per category
- 25 validation images per category  
- 375 total images
- Proper train/val split
- No manual work required!

**See `IMAGE_COLLECTION_GUIDE.md` for more details.**

### Step 1.3: Verify Dataset

Check you have:
- [ ] At least 50 images in each `train/` subfolder
- [ ] At least 10 images in each `val/` subfolder
- [ ] Images are clear and correctly labeled
- [ ] No duplicates between train and val

---

## Phase 2: Initial Training

### Step 2.1: Train First Model

```bash
python train_classifier.py
```

**What to expect:**
- Takes 10-30 minutes (depends on hardware)
- GPU will be used automatically if available
- Shows loss and accuracy for each epoch
- Saves model to `../models/`

**Example output:**
```
Epoch 1/10
Train Loss: 0.8234 Acc: 0.6500
Val Loss: 0.5123 Acc: 0.7800

...

Training Complete! Best Val Acc: 0.7800
```

**Initial accuracy targets:**
- 60-70%: Okay for first attempt
- 70-80%: Good start
- 80%+: Excellent!

### Step 2.2: Test the Model

```bash
python test_model.py
```

**Verifies:**
- Model file exists
- Model can be loaded
- Inference works correctly

### Step 2.3: Test in Web App

```bash
cd ..
streamlit run app.py
```

1. Navigate to "🖼️ Custom Image Classifier"
2. Upload various test images
3. Check predictions
4. Note any obvious mistakes

**What to test:**
- Clear examples of each class
- Ambiguous images
- Images of other objects (should classify as "other")
- Edge cases (partial objects, unusual angles)

---

## Phase 3: Error Analysis & Improvement

### Step 3.1: Analyze Training Errors

```bash
cd model_tuning
python analyze_training_errors.py
```

Choose dataset to analyze:
- Option 1: Training set (for finding mislabeled images)
- Option 2: Validation set (for understanding model weaknesses)

**Recommendation:** Analyze both, starting with training set.

### Step 3.2: Review HTML Report

Open `error_analysis_train.html` in your browser.

**Look for:**

1. **Top 30 Worst Predictions**
   - Images with highest loss
   - Focus on red-bordered cards (incorrect predictions)

2. **Per-Class Worst Images**
   - Class-specific problems
   - Patterns in errors

**Types of problems to identify:**

| Problem Type | How to Identify | Action |
|-------------|----------------|---------|
| Mislabeled | Prediction seems right, label seems wrong | Delete or relabel |
| Blurry/Dark | Can't clearly see subject | Delete |
| Multiple subjects | Bird AND plane in image | Delete |
| Wrong object | Cat labeled as bird | Delete |
| Partial/cropped | Only wing visible, labeled as plane | Delete or keep for variety |
| Unusual angle | Upside down, very far away | Keep (helps model generalize) |

### Step 3.3: Clean Dataset

Based on report, delete problematic images:

```bash
# Example: Delete worst bird images
cd dataset/train/bird/
# Manually review and delete files shown in report
```

**Guidelines:**
- Delete obvious problems (mislabeled, blurry)
- Keep challenging but valid images
- Don't remove more than 10-20% of images
- Document what you removed (mental note is fine)

### Step 3.4: Retrain

After cleaning dataset:

```bash
python train_classifier.py
```

**Expected improvement:**
- 5-10% accuracy increase is common
- More balanced per-class accuracy
- Lower validation loss

---

## Phase 4: Optimization

### Step 4.1: Adjust Confidence Threshold

Based on web app testing, you might need to adjust the threshold.

**Edit `train_classifier.py`:**
```python
CONFIG = {
    'confidence_threshold': 0.6,  # Adjust this
    # ...
}
```

**Tuning guide:**

| Observation | Current | New | Reason |
|------------|---------|-----|---------|
| Too many things classified as "other" | 0.6 | 0.5 | Be more permissive |
| Wrong classes predicted confidently | 0.6 | 0.7 | Be more conservative |
| Good balance | 0.6 | Keep | Perfect! |

**After changing, retrain:**
```bash
python train_classifier.py
```

### Step 4.2: Add More Data (If Needed)

If one class has low accuracy:

```bash
# Download more images for that specific class
python download_images.py
# Or manually collect more
```

**Focus on:**
- Class with lowest accuracy
- Underrepresented variations (angles, lighting, etc.)
- Edge cases the model struggles with

### Step 4.3: Extended Training (Optional)

For even better accuracy, train longer:

**Edit `train_classifier.py`:**
```python
CONFIG = {
    'num_epochs': 20,  # Instead of 10
    # ...
}
```

**When to do this:**
- Validation accuracy still improving at epoch 10
- You have 100+ images per class
- Aiming for 90%+ accuracy

**Watch for overfitting:**
- If validation accuracy starts decreasing, stop
- If train accuracy >> val accuracy, you're overfitting

---

## Phase 5: Final Validation & Deployment

### Step 5.1: Final Error Analysis

Run error analysis one more time on validation set:

```bash
python analyze_training_errors.py
# Choose: 2 (validation set)
```

**Review to confirm:**
- No obvious problems remain
- Errors make sense (truly ambiguous cases)
- Accuracy acceptable for your use case

### Step 5.2: Final Testing

Create a test set of new images (not in train/val):

```bash
mkdir test_images
# Add various images
```

Test each in the web app:
```bash
streamlit run ../app.py
```

**Test categories:**
- Clear examples (should be >90% confident)
- Edge cases (acceptable if lower confidence)
- Other objects (should classify as "other")

### Step 5.3: Documentation

Document your final model:

```bash
# Create a file: model_info.txt
echo "Model: Bird/Plane/Superman Classifier" > model_info.txt
echo "Training Date: $(date)" >> model_info.txt
echo "Training Images: <count>" >> model_info.txt
echo "Validation Accuracy: <percentage>" >> model_info.txt
echo "Confidence Threshold: 0.6" >> model_info.txt
echo "Notes: <any important observations>" >> model_info.txt
```

---

## Phase 6: Monitoring & Maintenance

### Step 6.1: Monitor Performance

As users test the app:
- Note any consistent errors
- Collect examples of failures
- Track user feedback

### Step 6.2: Continuous Improvement

Periodically (weekly/monthly):

```bash
# Add new images based on failures
# Re-run error analysis
python analyze_training_errors.py

# Clean and retrain
python train_classifier.py

# Test improvements
streamlit run ../app.py
```

---

## 🎯 Target Metrics

### Minimum Viable Model
- **Validation Accuracy**: 70%+
- **Per-class accuracy**: 60%+ for each class
- **Confidence on clear examples**: 80%+

### Production Quality
- **Validation Accuracy**: 85%+
- **Per-class accuracy**: 80%+ for each class
- **Confidence on clear examples**: 90%+

### Excellent Model
- **Validation Accuracy**: 90%+
- **Per-class accuracy**: 85%+ for each class
- **Confidence on clear examples**: 95%+

---

## 📊 Troubleshooting Decision Tree

```
Low accuracy (<70%)?
├─ Yes → Need more training data
│         - Collect 100+ images per class
│         - Run error analysis to clean dataset
│
└─ No → One class performing poorly?
    ├─ Yes → Focus on that class
    │         - Add more images for that class
    │         - Check for mislabeled images
    │         - Ensure variety in images
    │
    └─ No → Too many "other" classifications?
        ├─ Yes → Lower confidence threshold to 0.5
        │
        └─ No → Wrong class predictions?
            ├─ Yes → Raise confidence threshold to 0.7
            │         Run error analysis
            │
            └─ No → Model is working well!
                     Consider extended training for marginal improvements
```

---

## 🔄 Quick Reference Commands

```bash
# Setup
python download_sample_data.py

# Download images (if using automation)
python download_images.py

# Train
python train_classifier.py

# Test model
python test_model.py

# Analyze errors
python analyze_training_errors.py

# Run web app
cd ..
streamlit run app.py

# Generate test images (for quick testing)
cd model_tuning
python generate_test_images.py
```

---

## 📈 Expected Timeline

### Quick Prototype (1-2 hours)
```
15 min: Setup + generate test images
20 min: Train on test images
10 min: Test in web app
Result: Working demo (low accuracy)
```

### Basic Model (4-6 hours)
```
2 hours: Collect 50-100 images per class
30 min: Initial training
30 min: Testing and error analysis
1 hour: Clean dataset
30 min: Retrain
Result: 70-80% accuracy
```

### Production Model (8-12 hours)
```
4 hours: Collect 200+ images per class
1 hour: Initial training
1 hour: First error analysis and cleaning
1 hour: Retrain
1 hour: Second error analysis and cleaning
1 hour: Final training with extended epochs
1 hour: Extensive testing
Result: 85-90%+ accuracy
```

---

## ✅ Final Checklist

Before considering model "complete":

**Data Quality:**
- [ ] 100+ training images per class
- [ ] 20+ validation images per class
- [ ] No obvious mislabeled images
- [ ] Good variety (angles, lighting, backgrounds)
- [ ] No duplicates between train/val

**Model Performance:**
- [ ] Validation accuracy meets target (70%+ minimum, 85%+ ideal)
- [ ] All classes have acceptable accuracy
- [ ] Tested with various real-world images
- [ ] "Other" detection works reasonably well

**Documentation:**
- [ ] Model info file created
- [ ] Known limitations documented
- [ ] Usage instructions clear

**Deployment:**
- [ ] Model loads correctly in web app
- [ ] UI responsive and user-friendly
- [ ] Error handling works
- [ ] Tested on multiple browsers (if web deployed)

---

## 🎓 Key Takeaways

1. **Start small, iterate**: Quick prototype → Basic model → Production model
2. **Error analysis is crucial**: Most improvements come from cleaning data
3. **Confidence thresholding is powerful**: No need for "other" training data
4. **Quality over quantity**: 100 good images better than 500 mediocre ones
5. **Test extensively**: Edge cases reveal model weaknesses
6. **Document everything**: Future you will thank current you

---

## 🚀 You're Ready!

Follow this workflow and you'll have a production-quality image classifier. Don't skip the error analysis phase - it's the secret to high accuracy!

Questions? Check:
- `QUICKSTART.md` - Beginner guide
- `ADVANCED_FEATURES.md` - Feature details
- `README.md` - Technical documentation

Happy training! 🎉

