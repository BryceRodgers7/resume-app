import streamlit as st
from PIL import Image
import requests
import json
import os
import math
from io import BytesIO

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

# API configuration
API_URL = os.getenv('BPSIMGCLSS_API_URL', '')

def predict_with_api(image_file):
    """Make prediction on image using API endpoint"""
    try:
        # Reset file pointer to beginning
        image_file.seek(0)
        
        # Prepare the image file for POST request
        files = {'file': ('image.jpg', image_file, 'image/jpeg')}
        
        # Make POST request to /predict endpoint
        api_endpoint = f"{API_URL}/predict"
        response = requests.post(api_endpoint, files=files, timeout=30)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse JSON response
        result = response.json()
        
        return result, None
        
    except requests.exceptions.Timeout:
        return None, "Request timed out. The API server may be slow or unresponsive."
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the API server. Please check if the server is running."
    except requests.exceptions.HTTPError as e:
        return None, f"API returned an error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return None, f"Error making prediction: {str(e)}"

# Sidebar - API Status
with st.sidebar:
    st.subheader("🔌 API Status")
    if API_URL:
        st.success(f"✅ API URL configured")
        st.caption(f"Endpoint: {API_URL}/predict")
    else:
        st.error("❌ API URL not configured")
        st.caption("Set BPSIMGCLSS_API_URL environment variable")
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
        st.image(image, caption="Uploaded Image", use_container_width=True)
    
    with col2:
        st.markdown("### 🔍 Classification")
        
        if st.button("Classify Image", type="primary", use_container_width=True):
            # Check if API URL is configured
            if not API_URL:
                st.error("❌ API URL not configured. Please set the BPSIMGCLSS_API_URL environment variable.")
                st.stop()
            
            with st.spinner("Analyzing image via API..."):
                # Convert image to bytes for API request
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format=image.format or 'JPEG')
                img_byte_arr.seek(0)
                
                # Make API prediction
                result, error = predict_with_api(img_byte_arr)
                
                if error:
                    st.error(f"❌ {error}")
                    st.stop()
                
                # Extract results from API response
                predicted_class = result['predicted_class']
                confidence = result['confidence']
                all_probs = result['probabilities']
                threshold_applied = result.get('threshold_applied', False)
                
                # Calculate entropy from probabilities for display purposes
                prob_values = list(all_probs.values())
                entropy = -sum(p * math.log(p + 1e-10) for p in prob_values)
                max_entropy = math.log(len(prob_values))
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                
                # Determine detection reason
                if threshold_applied:
                    detection_reason = 'high_entropy'
                elif predicted_class == 'other':
                    detection_reason = 'predicted_other'
                else:
                    detection_reason = 'confident_prediction'
                
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
                    st.metric("Entropy", f"{normalized_entropy:.3f}", 
                             help="Lower entropy = more certain. Higher entropy = more uncertain/spread out probabilities")
                
                # Progress bar for confidence
                st.progress(confidence)
                
                # Show detection reasoning
                entropy_threshold = 0.7  # Default threshold for display
                if detection_reason == 'high_entropy':
                    st.warning(f"⚠️ **High Uncertainty Detected** (entropy: {normalized_entropy:.3f} > {entropy_threshold:.2f})")
                    st.caption("The model's predictions are spread across multiple classes, indicating this image doesn't clearly match any trained category.")
                elif detection_reason == 'predicted_other':
                    st.info("📦 **Classified as 'Other'** - The model learned this doesn't match bird/plane/superman patterns")
                else:
                    st.success(f"✅ **Confident Prediction** (entropy: {normalized_entropy:.3f} ≤ {entropy_threshold:.2f})")
                
                # Show all class probabilities
                st.markdown("### 📊 Confidence Breakdown:")
                for class_name, prob in all_probs.items():
                    emoji_icon = emoji_map.get(class_name, '❓')
                    st.write(f"{emoji_icon} **{class_name.capitalize()}**: {prob * 100:.1f}%")
                    st.progress(float(prob))
                
                # Show technical details in expander
                with st.expander("🔬 Technical Details"):
                    st.markdown(f"""
                    **Prediction Metrics:**
                    - **Max Confidence**: {confidence * 100:.2f}%
                    - **Normalized Entropy**: {normalized_entropy:.4f} (threshold: {entropy_threshold:.2f})
                    - **Detection Method**: {detection_reason.replace('_', ' ').title()}
                    
                    **Entropy Interpretation:**
                    - Entropy near 0.0 = Very certain (one class has ~100% probability)
                    - Entropy near 0.5 = Moderate uncertainty
                    - Entropy near 1.0 = Very uncertain (probabilities spread evenly)
                    
                    **Current Distribution:**
                    """)
                    
                    # Show if distribution is uniform or peaked
                    prob_values_list = list(all_probs.values())
                    max_prob = max(prob_values_list)
                    min_prob = min(prob_values_list)
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


