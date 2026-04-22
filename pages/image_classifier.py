import streamlit as st
from PIL import Image
import requests
import json
import os
import math
import logging
import time
import concurrent.futures
from io import BytesIO
import nav
from app import home_page

COLD_START_HINT_SEC = 6
COLD_START_HINT_MESSAGE = "backend may need a cold start, just a moment.."

# requests.post timeout: (connect seconds, read seconds). Cold Cloud Run / API wakeups
# can exceed a short read timeout; override with BPSIMGCLSS_TIMEOUT (read seconds only).
def _predict_timeout():
    read_sec = float(os.getenv("BPSIMGCLSS_TIMEOUT", "120"))
    connect_sec = min(10.0, read_sec)
    return (connect_sec, read_sec)


def run_with_cold_start_hint(request_fn, hint_placeholder):
    """Run request_fn in a worker thread; after COLD_START_HINT_SEC, show a cold-start hint."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(request_fn)
        start = time.monotonic()
        hint_shown = False
        while not future.done():
            if not hint_shown and time.monotonic() - start >= COLD_START_HINT_SEC:
                hint_placeholder.info(COLD_START_HINT_MESSAGE)
                hint_shown = True
            time.sleep(0.25)
        return future.result()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Image Classifier",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

st.title("🖼️ Is It a Bird? Is It a Plane? 🦸")

st.markdown("""
### Custom Image Classifier with Transfer Learning & Entropy-Based Uncertainty Detection

This is a **custom-trained image classification model** built with PyTorch using transfer learning. This page showcases 
practical computer vision implementation, including training pipeline design, entropy-based out-of-distribution detection, and production-ready inference.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Transfer Learning**: Fine-tuned ResNet50 architecture pre-trained on ImageNet for custom classification
    - **Complete Training Pipeline**:  Including raw data collection, early-loss cleaning, and hard-negative mining
    - **Model Deployment**: Containerized inference model (Docker/Kubernetes) in a scalable Cloud Run service, provisioned with Terraform
    - **Prediction Diagnostics**: Confidence scores, entropy analysis, and threshold signals that explain how and why the model reached its prediction
    """)

with st.expander("🔧 Model Architecture", expanded=False):
    st.markdown("""
    **Model Specifications:**               
    - **Architecture**: ImageNet-pretrained ResNet50 with fine-tuned final residual block
    - **Classifier**: Linear head on 2048-D pooled features (2048 → 4 classes)
    - **Input**: 224x224 RGB, ImageNet normalization
    - **Framework**: PyTorch / torchvision
    """)

with st.expander("🔍 Training Pipeline", expanded=False):
    st.markdown("""
    **Training & Validation Procedure**
    1) Collect initial dataset
    2) Remove duplicates using pHash
    3) Train model (just the head, 3 epochs)
    4) Early-loss clean mislabeled data
    5) Retrain (from scratch, 15 epochs)
    6) Hard-negative mining
    7) Train again with mined images (4 epochs, lower LR)
    8) Temperature calibration (~1.60)
    9) Choose confidence threshold (0.7)
    10) Final evaluation on validation set (loss 0.102, accuracy 0.978)
                
    **Model Specifications:**
    - Batch processing with GPU optimization
    - Data augmentation (resize, crop, random flips, color jitter)
    - Transfer learning with frozen early layers
    - CrossEntropyLoss optimization with Adam
    - Validation-based checkpointing
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
    - Watch the **entropy metric** - it tells you how uncertain the model is
    - Try uploading completely unrelated images (cars, food, people) to see the OOD detection in action!
    
    **What to Expect:**
    - Images clearly matching a category → Low entropy, high confidence
    - Ambiguous/unfamiliar images → High entropy, classified as "other"
    """)

st.info("🧠 **Model Training Code**: Check out the complete training pipeline code on [GitHub →](https://github.com/BryceRodgers7/img-classifier-birdplanesuper)!")

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
        response = requests.post(api_endpoint, files=files, timeout=_predict_timeout())
        
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
    "Upload an image to get started",
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
            
            cold_hint = st.empty()
            result, error = None, None
            with st.spinner("Analyzing image via API..."):
                # Convert image to bytes for API request
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format=image.format or 'JPEG')
                img_byte_arr.seek(0)

                def run_predict():
                    return predict_with_api(img_byte_arr)

                result, error = run_with_cold_start_hint(run_predict, cold_hint)
            # Show errors only after the spinner context exits, so the spinner unmounts (st.stop()
            # inside the spinner can leave the UI stuck "spinning").
            cold_hint.empty()
            if error:
                st.error(f"❌ {error}")
                st.stop()
            
            # Log full API response
            assert result is not None
            logger.info("API response received: %s", json.dumps(result, indent=2))

            # Extract results from API response
            predicted_class = result['predicted_class']
            confidence = result['confidence']
            top_class = result['top_class']
            top_prob = result['top_prob']
            confidence_threshold = result['confidence_threshold']
            all_probs = result['all_probs']
            threshold_applied = result.get('threshold_applied', False)

            logger.info(
                "Parsed — predicted_class=%s, confidence=%.4f, top_class=%s, top_prob=%.4f, "
                "confidence_threshold=%.4f, threshold_applied=%s, all_probs=%s",
                predicted_class, confidence, top_class, top_prob,
                confidence_threshold, threshold_applied, all_probs
            )
            
            # Calculate entropy from probabilities for display purposes
            prob_values = list(all_probs.values())
            entropy = -sum(p * math.log(p + 1e-10) for p in prob_values)
            max_entropy = math.log(len(prob_values))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            # Determine detection reason
            if threshold_applied:
                detection_reason = 'low_confidence_threshold'
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
            if detection_reason == 'high_entropy':
                st.warning(f"⚠️ **High Uncertainty Detected** (entropy: {normalized_entropy:.3f})")
                st.caption("The model's predictions are spread across multiple classes, indicating this image doesn't clearly match any trained category.")
            elif detection_reason == 'low_confidence_threshold':
                st.warning(f"⚠️ **Below Confidence Threshold** (confidence: {confidence:.4f} < threshold: {confidence_threshold:.4f})")
                st.caption("The model's top prediction did not meet the required confidence threshold and was overridden.")
            else:
                st.success(f"✅ **Confident Prediction** (confidence: {confidence:.4f} ≥ threshold: {confidence_threshold:.4f})")
            
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
                - **Predicted Class**: {predicted_class}
                - **Confidence**: {confidence:.4f} ({confidence * 100:.2f}%)
                - **Top Class (raw)**: {top_class}
                - **Top Probability (raw)**: {top_prob:.4f} ({top_prob * 100:.2f}%)
                - **Confidence Threshold**: {confidence_threshold:.4f}
                - **Threshold Applied**: {threshold_applied}
                - **Normalized Entropy**: {normalized_entropy:.4f}
                - **Detection Method**: {detection_reason.replace('_', ' ').title()}
                
                **Entropy Interpretation:**
                - Entropy near 0.0 = Very certain (one class has ~100% probability)
                - Entropy near 0.5 = Moderate uncertainty
                - Entropy near 1.0 = Very uncertain (probabilities spread evenly)
                
                **Raw API Response:**
                """)
                st.json(result)
                st.markdown("**Current Distribution:**")
                
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
                st.info("📦 This image doesn't clearly match any of the specific categories (bird/plane/superman)")


