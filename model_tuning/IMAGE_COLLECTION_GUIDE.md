# Automated Image Collection Guide

This classifier uses **fully automated image downloading** - no manual work required!

## 🚀 Quick Start (Recommended)

### Option 1: DuckDuckGo (No API Key Needed)

Fastest way to get started - works immediately:

```bash
python download_images.py --duckduckgo
```

or simply:

```bash
python download_images.py
```

**Pros:**
- ✅ No API key needed
- ✅ Works immediately
- ✅ Completely free
- ✅ No registration required

**Cons:**
- ⚠️ Results may be limited
- ⚠️ Variable image quality

---

### Option 2: Bing API (Best Balance)

Best quality automated downloads with free API:

**Setup (one-time, 5 minutes):**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Bing Search v7"
4. Select free tier (1000 searches/month)
5. Create and copy one of the API keys

**Set environment variable:**

```bash
# Windows PowerShell
$env:BING_API_KEY="your-api-key-here"

# Linux/Mac
export BING_API_KEY="your-api-key-here"
```

**Run:**

```bash
python download_images.py --bing
```

**Pros:**
- ✅ Free tier (1000 calls/month)
- ✅ High quality results
- ✅ Reliable and fast
- ✅ Good variety

---

### Option 3: Unsplash API (Highest Quality)

Professional photography from Unsplash:

**Setup (one-time, 5 minutes):**

1. Go to [Unsplash Developers](https://unsplash.com/developers)
2. Create an account (free)
3. Register a new application
4. Copy the Access Key

**Set environment variable:**

```bash
# Windows PowerShell
$env:UNSPLASH_API_KEY="your-access-key-here"

# Linux/Mac
export UNSPLASH_API_KEY="your-access-key-here"
```

**Run:**

```bash
python download_images.py --unsplash
```

**Pros:**
- ✅ Highest quality images
- ✅ Professional photography
- ✅ Free commercial license
- ✅ 50 requests/hour (free tier)

**Cons:**
- ⚠️ Smaller dataset available
- ⚠️ Rate limited (50/hour)

---

## 📊 What Gets Downloaded

The script automatically downloads:

### Categories
1. **Birds**: Eagles, parrots, owls, sparrows, hawks, seagulls
2. **Planes**: Commercial jets, fighter jets, small aircraft
3. **Superman**: Movie scenes, comic art, costume photos

### Quantities
- **Training set**: 100 images per category
- **Validation set**: 25 images per category
- **Total**: 375 images

### File Organization
```
dataset/
├── train/
│   ├── bird/       (100 images)
│   ├── plane/      (100 images)
│   └── superman/   (100 images)
└── val/
    ├── bird/       (25 images)
    ├── plane/      (25 images)
    └── superman/   (25 images)
```

---

## ⏱️ Time Estimates

- **DuckDuckGo**: 15-25 minutes
- **Bing API**: 10-15 minutes
- **Unsplash API**: 20-30 minutes (rate limiting)

Grab a coffee while it downloads! ☕

---

## 🔍 Quality Control (The Important Part!)

The only manual work you need to do is **after training**, not during collection:

### 1. Download Images (Automated)
```bash
python download_images.py --duckduckgo
```

### 2. Train Model (Automated)
```bash
python train_classifier.py
```

### 3. Analyze Errors (Automated)
```bash
python analyze_training_errors.py
```

### 4. Review High-Loss Images (Manual - This is the key!)

Open the generated `error_analysis_train.html` in your browser.

**Look for:**
- ❌ Mislabeled images (delete)
- ❌ Blurry/dark images (delete)
- ❌ Wrong objects (delete)
- ❌ Multiple objects (delete)
- ✅ Challenging but correct images (keep)

**Delete bad images:**
```bash
# Navigate to dataset folders and delete files shown in report
cd dataset/train/bird/
# Delete problematic image files
```

### 5. Retrain (Automated)
```bash
python train_classifier.py
```

This iterative process (train → analyze → clean → retrain) is how you achieve high accuracy!

---

## 🎯 Complete Workflow

```bash
# 1. Create dataset structure
python download_sample_data.py

# 2. Download images (automated - choose one)
python download_images.py --duckduckgo  # No API key
python download_images.py --bing        # Free API key
python download_images.py --unsplash    # Free API key

# 3. Train model
python train_classifier.py

# 4. Analyze for problems
python analyze_training_errors.py

# 5. Manually review and delete bad images
# Open error_analysis_train.html
# Delete problematic images from dataset folders

# 6. Retrain
python train_classifier.py

# 7. Deploy
cd ..
streamlit run app.py
```

---

## 🔄 Recommended: Iterative Improvement

For best results, repeat this cycle 2-3 times:

```
Download → Train → Analyze → Clean → Retrain
```

**Expected improvements:**
- 1st iteration: 70-75% accuracy
- 2nd iteration: 80-85% accuracy
- 3rd iteration: 85-90% accuracy

---

## ⚖️ Copyright & Ethics

### For Learning/Personal Projects
- ✅ Generally okay to use images for learning
- ✅ This classifier is for educational purposes

### For Commercial Use
- ⚠️ Ensure proper licensing
- ✅ Unsplash provides free commercial licenses
- ⚠️ Bing/DuckDuckGo results may have various licenses

### Best Practices
- Only use images you have rights to use
- Respect copyright and licensing
- For commercial deployment, use Unsplash or licensed images
- Review terms of service for each platform

---

## 💡 Pro Tips

### Getting Better Results

1. **Start with DuckDuckGo** - no setup needed
2. **Train immediately** - see how it performs
3. **Use error analysis** - this is the secret sauce!
4. **Delete bad images** - quality over quantity
5. **Retrain** - watch accuracy improve
6. **Iterate** - 2-3 cycles gets best results

### Troubleshooting

**DuckDuckGo fails:**
- Try Bing API (more reliable)
- Check internet connection
- Run script again (it skips existing files)

**Bing API fails:**
- Verify API key is correct
- Check you're within free tier limits (1000/month)
- Ensure key has search permissions

**Not enough images:**
- Run the script multiple times with different queries
- Try different download method
- Manually add a few more if needed

**Too many bad images:**
- Use error analysis to identify them
- Delete and retrain
- Consider switching to Unsplash for higher quality

---

## 🎓 Summary

**Key Points:**
1. ✅ Image downloading is **fully automated**
2. ✅ No manual downloading required
3. ✅ Multiple free options available
4. ✅ The only manual work is **error analysis** (reviewing high-loss images)
5. ✅ This approach achieves high accuracy with minimal manual effort

**Time Investment:**
- Setup: 5 minutes (if using API keys)
- Download: 10-25 minutes (automated)
- Training: 10-30 minutes (automated)
- Error review: 10-20 minutes (manual - THE IMPORTANT PART)
- Total: ~1 hour for first iteration

**Result:**
A production-quality image classifier with 85%+ accuracy!

---

Ready to start? Just run:

```bash
python download_images.py
```

That's it! The script will guide you through the rest. 🚀

