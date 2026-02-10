import streamlit as st
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models
import json
from pathlib import Path
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Image Classifier",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🖼️ Is It a Bird? Is It a Plane? 🦸")

st.markdown("""
### Custom Image Classifier with Transfer Learning & Entropy-Based Uncertainty Detection

This is a **custom-trained image classification model** built with PyTorch using transfer learning. The model demonstrates 
practical computer vision implementation, including training pipeline design, entropy-based out-of-distribution detection, and production-ready inference.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Transfer Learning**: Fine-tuned ResNet18 architecture pre-trained on ImageNet for custom classification
    - **PyTorch Implementation**: Complete training pipeline with data augmentation, optimization, and model persistence
    - **Dual OOD Detection Strategy**: 
      - **Explicit "Other" Class**: Trained on diverse out-of-distribution images
      - **Entropy-Based Detection**: Uses prediction entropy to identify uncertain/anomalous inputs
    - **Model Deployment**: Serialized model loading, preprocessing pipeline, and inference serving in production
    - **Computer Vision Best Practices**: 
      - Image preprocessing and normalization
      - Data augmentation strategies
      - Batch processing and GPU optimization
    - **State Management**: Cached model loading for performance optimization
    """)

with st.expander("🔧 Technical Architecture", expanded=False):
    st.markdown("""
    **Model Specifications:**
    - **Base Architecture**: ResNet18 (pre-trained on ImageNet)
    - **Custom Head**: 512-neuron fully connected layer with ReLU + Dropout (0.3)
    - **Classes**: 4 trained categories (bird, plane, superman, other)
    - **Input**: 224x224 RGB images with ImageNet normalization
    - **Framework**: PyTorch with torchvision transforms
    
    **Training Pipeline:**
    - Data augmentation (resize, crop, random flips, color jitter)
    - Transfer learning with frozen early layers
    - CrossEntropyLoss optimization with Adam
    - Validation-based checkpointing
    - [View training code on GitHub →](https://github.com/bryceglarsen/resume-app/tree/main/model_tuning)
    
    **Dual Out-of-Distribution (OOD) Detection:**
    This model uses **two complementary strategies** to detect unfamiliar images:
    
    1. **Explicit "Other" Class Training**: 
       - Trained on diverse images (cars, people, landscapes, etc.)
       - Learns explicit patterns of what is NOT bird/plane/superman
    
    2. **Entropy-Based Uncertainty Detection**:
       - Calculates prediction entropy: H = -Σ(p_i * log(p_i))
       - High entropy (flat probability distribution) → model is uncertain
       - Example: [0.25, 0.25, 0.25, 0.25] has high entropy (very uncertain)
       - Example: [0.9, 0.05, 0.03, 0.02] has low entropy (very confident)
       - Images with high entropy are reclassified as "other"
       - More robust to novel image types not seen during training
    
    This **layered approach** provides better protection against false positives on out-of-distribution images.
    """)

with st.expander("💡 Try it Out", expanded=False):
    st.markdown("""
    **Upload images to classify:**
    - 🐦 **Birds**: Sparrows, eagles, parrots, penguins, etc.
    - ✈️ **Planes**: Commercial jets, fighter jets, propeller planes, helicopters
    - 🦸 **Superman**: Images of the Man of Steel in action
    - 📦 **Other**: Anything else (detected via trained "other" class + entropy analysis)
    
    **Tips for Best Results:**
    - Use clear, well-lit images with visible subjects
    - Avoid heavily cropped or blurry photos
    - The model works best with images similar to training data
    - Watch the **entropy metric** - it tells you how uncertain the model is
    - Try uploading completely unrelated images (cars, food, people) to see the OOD detection in action!
    
    **What to Expect:**
    - Images clearly matching a category → Low entropy, high confidence
    - Ambiguous/unfamiliar images → High entropy, classified as "other"
    - The model now has **two layers of protection** against false positives
    """)

st.info("🧠 **Model Training Code**: Check out the complete training pipeline and scripts on [GitHub in the  `model_tuning/`  folder](https://github.com/BryceRodgers7/resume-app/tree/main/model_tuning)!")

st.divider()

# Model configuration
MODEL_PATH = Path(__file__).parent.parent / 'models' / 'bird_plane_superman_other_classifier_latest.pth'
METADATA_PATH = Path(__file__).parent.parent / 'models' / 'bird_plane_superman_other_classifier_metadata.json'

@st.cache_resource
def load_model():
    """Load the trained classifier model"""
    try:
        # Load metadata
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            class_names = metadata['class_names']
            num_classes = metadata['num_classes']
            entropy_threshold = metadata.get('entropy_threshold', 0.7)
        else:
            # Default fallback - assume 4-class model
            class_names = ['bird', 'other', 'plane', 'superman']
            num_classes = 4
            entropy_threshold = 0.7
        
        # Create model architecture (must match training)
        model = models.resnet18(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        # Load trained weights
        if MODEL_PATH.exists():
            model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
            model.eval()
            return model, class_names, entropy_threshold, True
        else:
            return None, class_names, entropy_threshold, False
            
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, ['bird', 'other', 'plane', 'superman'], 0.7, False

def preprocess_image(image):
    """Preprocess image for model input"""
    # Define the same transforms as during training (validation transforms)
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Apply transforms and add batch dimension
    img_tensor = transform(image).unsqueeze(0)
    return img_tensor

def predict(model, image_tensor, class_names, entropy_threshold):
    """Make prediction on image with entropy-based uncertainty detection"""
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)
        
        confidence_score = confidence.item()
        predicted_idx_val = predicted_idx.item()
        
        # Calculate entropy for uncertainty detection
        # Entropy = -Σ(p_i * log(p_i))
        # High entropy means the model is uncertain (probabilities are spread out)
        log_probs = torch.log(probabilities + 1e-10)  # Add small value to avoid log(0)
        entropy = -torch.sum(probabilities * log_probs, dim=1)
        
        # Normalize entropy to [0, 1] range
        max_entropy = np.log(len(class_names))
        normalized_entropy = entropy.item() / max_entropy
        
        # Get all class probabilities
        all_probs = probabilities[0].numpy()
        
        # Determine predicted class using entropy-based detection
        predicted_class = class_names[predicted_idx_val]
        
        # If entropy is high, the model is uncertain -> classify as "other"
        # This catches cases where probabilities are spread out (e.g., [0.3, 0.25, 0.25, 0.2])
        if normalized_entropy > entropy_threshold:
            predicted_class = 'other'
            detection_reason = 'high_entropy'
        # If model already predicted "other" class, keep it
        elif predicted_class == 'other':
            detection_reason = 'predicted_other'
        else:
            detection_reason = 'confident_prediction'
        
    return predicted_class, confidence_score, all_probs, normalized_entropy, detection_reason

# Load model
model, class_names, entropy_threshold, model_loaded = load_model()

# Sidebar - Model Status
with st.sidebar:
    st.subheader("🔌 Model Status")
    if model_loaded:
        st.success("✅ Model loaded successfully!")
    else:
        st.error("❌ Model not found")
        st.caption("[View training code on GitHub →](https://github.com/bryceglarsen/resume-app/tree/main/model_tuning)")

# File uploader
uploaded_file = st.file_uploader(
    "Upload an image to classify",
    type=['png', 'jpg', 'jpeg', 'webp'],
    help="Upload a clear image for best results"
)

if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Uploaded Image", use_column_width=True)
    
    with col2:
        st.markdown("### 🔍 Classification")
        
        if st.button("Classify Image", type="primary", use_container_width=True):
            with st.spinner("Analyzing image..."):
                # Preprocess and predict
                img_tensor = preprocess_image(image)
                predicted_class, confidence, all_probs, entropy, detection_reason = predict(
                    model, img_tensor, class_names, entropy_threshold
                )
                
                # Display result with emoji
                emoji_map = {
                    'bird': '🐦',
                    'plane': '✈️',
                    'superman': '🦸',
                    'other': '📦'
                }
                
                emoji = emoji_map.get(predicted_class, '❓')
                
                # Main prediction
                st.markdown(f"## {emoji} **{predicted_class.upper()}** {emoji}")
                
                # Show metrics in columns
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Confidence", f"{confidence * 100:.1f}%")
                with metric_col2:
                    st.metric("Entropy", f"{entropy:.3f}", 
                             help="Lower entropy = more certain. Higher entropy = more uncertain/spread out probabilities")
                
                # Progress bar for confidence
                st.progress(confidence)
                
                # Show detection reasoning
                if detection_reason == 'high_entropy':
                    st.warning(f"⚠️ **High Uncertainty Detected** (entropy: {entropy:.3f} > {entropy_threshold:.2f})")
                    st.caption("The model's predictions are spread across multiple classes, indicating this image doesn't clearly match any trained category.")
                elif detection_reason == 'predicted_other':
                    st.info("📦 **Classified as 'Other'** - The model learned this doesn't match bird/plane/superman patterns")
                else:
                    st.success(f"✅ **Confident Prediction** (entropy: {entropy:.3f} ≤ {entropy_threshold:.2f})")
                
                # Show all class probabilities
                st.markdown("### 📊 Confidence Breakdown:")
                for idx, class_name in enumerate(class_names):
                    prob = all_probs[idx]
                    emoji_icon = emoji_map.get(class_name, '❓')
                    st.write(f"{emoji_icon} **{class_name.capitalize()}**: {prob * 100:.1f}%")
                    st.progress(float(prob))
                
                # Show technical details in expander
                with st.expander("🔬 Technical Details"):
                    st.markdown(f"""
                    **Prediction Metrics:**
                    - **Max Confidence**: {confidence * 100:.2f}%
                    - **Normalized Entropy**: {entropy:.4f} (threshold: {entropy_threshold:.2f})
                    - **Detection Method**: {detection_reason.replace('_', ' ').title()}
                    
                    **Entropy Interpretation:**
                    - Entropy near 0.0 = Very certain (one class has ~100% probability)
                    - Entropy near 0.5 = Moderate uncertainty
                    - Entropy near 1.0 = Very uncertain (probabilities spread evenly)
                    
                    **Current Distribution:**
                    """)
                    
                    # Show if distribution is uniform or peaked
                    max_prob = max(all_probs)
                    min_prob = min(all_probs)
                    if max_prob - min_prob < 0.2:
                        st.caption("⚖️ Flat distribution - model is very uncertain")
                    else:
                        st.caption("📊 Peaked distribution - model has a clear preference")
                
                # Fun message based on result
                st.divider()
                if predicted_class == 'superman':
                    st.balloons()
                    st.success("🦸‍♂️ It's Superman! Faster than a speeding bullet!")
                elif predicted_class == 'bird':
                    st.info("🐦 It's a bird! Tweet tweet!")
                elif predicted_class == 'plane':
                    st.info("✈️ It's a plane! Ready for takeoff!")
                else:
                    st.info("📦 This image doesn't clearly match any of the trained categories (bird/plane/superman)")


