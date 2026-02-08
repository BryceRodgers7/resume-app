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
### Custom Image Classifier with Transfer Learning & Confidence Thresholding

This is a **custom-trained image classification model** built with PyTorch using transfer learning. The model demonstrates 
practical computer vision implementation, including training pipeline design, confidence thresholding, and production-ready inference.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Transfer Learning**: Fine-tuned ResNet18 architecture pre-trained on ImageNet for custom classification
    - **PyTorch Implementation**: Complete training pipeline with data augmentation, optimization, and model persistence
    - **Confidence Thresholding**: Smart "other" class detection without explicit training data—predictions below threshold are rejected
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
    - **Classes**: 3 trained categories (bird, plane, superman) + confidence threshold for "other"
    - **Input**: 224x224 RGB images with ImageNet normalization
    - **Framework**: PyTorch with torchvision transforms
    
    **Training Pipeline:**
    - Data augmentation (resize, crop, random flips, color jitter)
    - Transfer learning with frozen/unfrozen layers
    - CrossEntropyLoss optimization with Adam
    - Validation-based checkpointing
    - [View training code on GitHub →](https://github.com/bryceglarsen/resume-app/tree/main/model_tuning)
    
    **Confidence Thresholding:**
    Instead of training an "other" class, this model uses **confidence thresholding**:
    - Predictions above threshold → classified as predicted category
    - All predictions below threshold → classified as "other"
    - More robust than training on miscellaneous "other" data
    """)

with st.expander("💡 Try it Out", expanded=False):
    st.markdown("""
    **Upload images to classify:**
    - 🐦 **Birds**: Sparrows, eagles, parrots, penguins, etc.
    - ✈️ **Planes**: Commercial jets, fighter jets, propeller planes, helicopters
    - 🦸 **Superman**: Images of the Man of Steel in action
    - 📦 **Other**: Anything else (detected via confidence threshold)
    
    **Tips for Best Results:**
    - Use clear, well-lit images with visible subjects
    - Avoid heavily cropped or blurry photos
    - The model works best with images similar to training data
    - Watch the confidence breakdown to see how certain the model is
    """)

st.info("🧠 **Model Training Code**: Check out the complete training pipeline and scripts on [GitHub in the `model_tuning/` folder](https://github.com/BryceRodgers7/resume-app/tree/main/model_tuning)!")

st.divider()

# Model configuration
MODEL_PATH = Path(__file__).parent.parent / 'models' / 'bird_plane_superman_classifier_latest.pth'
METADATA_PATH = Path(__file__).parent.parent / 'models' / 'classifier_metadata.json'

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
            confidence_threshold = metadata.get('confidence_threshold', 0.6)
        else:
            # Default fallback
            class_names = ['bird', 'plane', 'superman']
            num_classes = 3
            confidence_threshold = 0.6
        
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
            return model, class_names, confidence_threshold, True
        else:
            return None, class_names, confidence_threshold, False
            
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, ['bird', 'plane', 'superman'], 0.6, False

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

def predict(model, image_tensor, class_names, confidence_threshold):
    """Make prediction on image with confidence thresholding"""
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)
        
        confidence_score = confidence.item()
        
        # Check if confidence is above threshold
        if confidence_score < confidence_threshold:
            predicted_class = 'other'
        else:
            predicted_class = class_names[predicted_idx.item()]
        
        # Get all class probabilities
        all_probs = probabilities[0].numpy()
        
    return predicted_class, confidence_score, all_probs

# Load model
model, class_names, confidence_threshold, model_loaded = load_model()

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
                predicted_class, confidence, all_probs = predict(model, img_tensor, class_names, confidence_threshold)
                
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
                st.metric("Confidence", f"{confidence * 100:.1f}%")
                
                # Progress bar for confidence
                st.progress(confidence)
                
                # Show all class probabilities
                st.markdown("### 📊 Confidence Breakdown:")
                for idx, class_name in enumerate(class_names):
                    prob = all_probs[idx]
                    emoji_icon = emoji_map.get(class_name, '❓')
                    
                    # Highlight if below threshold
                    threshold_note = ""
                    if prob == confidence and prob < confidence_threshold:
                        threshold_note = f" (below {confidence_threshold*100:.0f}% threshold)"
                    
                    st.write(f"{emoji_icon} **{class_name.capitalize()}**: {prob * 100:.1f}%{threshold_note}")
                    st.progress(float(prob))
                
                # Show threshold info
                st.info(f"📏 **Confidence Threshold**: {confidence_threshold*100:.0f}% - Predictions below this are classified as 'other'")
                
                # Fun message based on result
                if predicted_class == 'superman':
                    st.balloons()
                    st.success("🦸‍♂️ It's Superman! Faster than a speeding bullet!")
                elif predicted_class == 'bird':
                    st.info("🐦 It's a bird! Tweet tweet!")
                elif predicted_class == 'plane':
                    st.info("✈️ It's a plane! Ready for takeoff!")
                else:
                    st.info(f"📦 It's something else! None of the classes matched with sufficient confidence (>{confidence_threshold*100:.0f}%)")


