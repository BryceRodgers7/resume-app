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
Upload an image and find out if it's a **bird**, a **plane**, **Superman**, or something else entirely!

This classifier uses a custom-trained neural network model.

---
""")

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

# Check if model exists
if not model_loaded:
    st.warning("""
    ⚠️ **Model not found!** 
    
    The classifier model hasn't been trained yet. To use this feature:
    
    1. Navigate to the `model_tuning` folder
    2. Follow the instructions in `model_tuning/README.md`
    3. Run the training script to create your model
    
    Quick start:
    ```bash
    cd model_tuning
    python download_sample_data.py  # Create dataset structure
    # Add images to dataset folders
    python train_classifier.py      # Train the model
    ```
    """)
    
    st.info("""
    **Expected model location:**
    - `models/bird_plane_superman_classifier_latest.pth`
    - `models/classifier_metadata.json`
    """)
    
else:
    st.success("✅ Model loaded successfully!")
    
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

# Additional information
with st.expander("ℹ️ About This Classifier"):
    st.markdown("""
    ### How It Works
    
    This image classifier uses a **deep learning neural network** (ResNet18) that has been 
    fine-tuned to recognize three specific categories:
    
    - 🐦 **Bird**: Various types of birds
    - ✈️ **Plane**: Aircraft of all kinds
    - 🦸 **Superman**: The Man of Steel himself
    - 📦 **Other**: Automatically detected when confidence is too low
    
    ### How "Other" Works
    
    Unlike traditional classifiers, this model doesn't have an "other" class in training.
    Instead, it uses **confidence thresholding**:
    - If the highest prediction is above the confidence threshold (default 60%), it's classified as that category
    - If all predictions are below the threshold, it's classified as "other"
    - This is more robust than training on an "other" class!
    
    ### Technical Details
    
    - **Architecture**: ResNet18 with transfer learning
    - **Framework**: PyTorch
    - **Input Size**: 224x224 pixels
    - **Classes**: 3 trained (bird, plane, superman) + confidence threshold for "other"
    - **Confidence Threshold**: Configurable in training (default 60%)
    
    ### Tips for Best Results
    
    - Use clear, well-lit images
    - Ensure the subject is clearly visible
    - Avoid heavily cropped or blurry images
    - The model works best with images similar to its training data
    
    ### Model Training
    
    The model is trained using the scripts in the `model_tuning` folder.
    You can retrain it with your own images to improve accuracy!
    """)

st.markdown("---")
st.caption("Built with PyTorch and Streamlit")
