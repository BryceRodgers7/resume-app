"""
Training Error Analysis Tool

Analyzes model predictions to find images with highest loss.
Helps identify mislabeled, poor quality, or ambiguous images.

Usage:
    1. Train your model first with train_classifier.py
    2. Run: python analyze_training_errors.py
    3. Review the generated HTML report with worst images
    4. Manually delete problematic images from dataset
    5. Retrain for better accuracy
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from pathlib import Path
import json
import shutil
from PIL import Image

def load_model():
    """Load the trained model"""
    model_path = Path(__file__).parent.parent / 'models' / 'bird_plane_superman_classifier_latest.pth'
    metadata_path = Path(__file__).parent.parent / 'models' / 'classifier_metadata.json'
    
    # Load metadata
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        num_classes = metadata['num_classes']
    else:
        num_classes = 3  # Default: bird, plane, superman
    
    # Create model
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    
    return model, metadata

def get_data_loader(data_dir, batch_size=1):
    """Create data loader with validation transforms"""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(data_dir, transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    return loader, dataset

def analyze_errors(model, data_loader, dataset, device='cpu'):
    """Analyze model predictions and find high-loss images"""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss(reduction='none')
    
    results = []
    
    print("\n🔍 Analyzing predictions...")
    
    with torch.no_grad():
        for idx, (inputs, labels) in enumerate(data_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            # Get prediction
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Get probabilities
            probs = torch.nn.functional.softmax(outputs, dim=1)
            pred_prob, pred_class = torch.max(probs, 1)
            
            # Get image path
            img_path, true_label = dataset.samples[idx]
            
            # Store result
            results.append({
                'image_path': img_path,
                'true_label': true_label,
                'true_class': dataset.classes[true_label],
                'pred_label': pred_class.item(),
                'pred_class': dataset.classes[pred_class.item()],
                'pred_prob': pred_prob.item(),
                'loss': loss.item(),
                'correct': pred_class.item() == true_label
            })
            
            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1}/{len(data_loader)} images...")
    
    return results

def generate_html_report(results, class_names, output_path):
    """Generate HTML report showing worst predictions"""
    
    # Sort by loss (highest first)
    results_sorted = sorted(results, key=lambda x: x['loss'], reverse=True)
    
    # Overall stats
    total = len(results)
    correct = sum(1 for r in results if r['correct'])
    accuracy = correct / total * 100
    
    # Per-class worst images
    worst_per_class = {}
    for class_name in class_names:
        class_results = [r for r in results if r['true_class'] == class_name]
        worst_per_class[class_name] = sorted(class_results, key=lambda x: x['loss'], reverse=True)[:20]
    
    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Training Error Analysis</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat {{
            display: inline-block;
            margin-right: 30px;
            font-size: 18px;
        }}
        .stat-value {{
            font-weight: bold;
            color: #2196F3;
            font-size: 24px;
        }}
        .class-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .image-card {{
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background: #fafafa;
        }}
        .image-card.error {{
            border-color: #f44336;
            background: #ffebee;
        }}
        .image-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 5px;
        }}
        .image-info {{
            margin-top: 10px;
            font-size: 12px;
        }}
        .loss {{
            font-weight: bold;
            color: #f44336;
        }}
        .prediction {{
            color: #666;
        }}
        .correct {{
            color: #4CAF50;
        }}
        .incorrect {{
            color: #f44336;
        }}
        .confidence {{
            font-style: italic;
            color: #2196F3;
        }}
        .delete-tip {{
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>🔍 Training Error Analysis Report</h1>
    
    <div class="stats">
        <div class="stat">
            <div>Total Images</div>
            <div class="stat-value">{total}</div>
        </div>
        <div class="stat">
            <div>Correct</div>
            <div class="stat-value">{correct}</div>
        </div>
        <div class="stat">
            <div>Accuracy</div>
            <div class="stat-value">{accuracy:.1f}%</div>
        </div>
    </div>
    
    <div class="delete-tip">
        <strong>💡 How to use this report:</strong><br>
        1. Review images with high loss (shown first in each section)<br>
        2. Look for mislabeled, blurry, or ambiguous images<br>
        3. Delete problematic images from your dataset folders<br>
        4. Retrain the model for improved accuracy
    </div>
"""
    
    # Add worst overall images
    html += """
    <div class="class-section">
        <h2>⚠️ Top 30 Worst Predictions (All Classes)</h2>
        <div class="image-grid">
"""
    
    for result in results_sorted[:30]:
        card_class = "image-card error" if not result['correct'] else "image-card"
        status_class = "correct" if result['correct'] else "incorrect"
        status_text = "✓ Correct" if result['correct'] else "✗ Incorrect"
        
        # Make path relative for display
        rel_path = Path(result['image_path']).relative_to(Path(__file__).parent)
        
        html += f"""
            <div class="{card_class}">
                <img src="file:///{result['image_path']}" alt="{result['true_class']}">
                <div class="image-info">
                    <div class="loss">Loss: {result['loss']:.4f}</div>
                    <div>True: <strong>{result['true_class']}</strong></div>
                    <div class="prediction">Predicted: <strong>{result['pred_class']}</strong></div>
                    <div class="confidence">Confidence: {result['pred_prob']*100:.1f}%</div>
                    <div class="{status_class}">{status_text}</div>
                    <div style="font-size: 10px; color: #999; margin-top: 5px; word-break: break-all;">
                        {rel_path}
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
"""
    
    # Add per-class sections
    for class_name in class_names:
        worst_images = worst_per_class[class_name]
        if not worst_images:
            continue
        
        class_total = len([r for r in results if r['true_class'] == class_name])
        class_correct = len([r for r in results if r['true_class'] == class_name and r['correct']])
        class_acc = class_correct / class_total * 100 if class_total > 0 else 0
        
        html += f"""
    <div class="class-section">
        <h2>📊 {class_name.upper()} - Worst Images</h2>
        <p>Accuracy: {class_acc:.1f}% ({class_correct}/{class_total} correct)</p>
        <div class="image-grid">
"""
        
        for result in worst_images:
            card_class = "image-card error" if not result['correct'] else "image-card"
            status_class = "correct" if result['correct'] else "incorrect"
            status_text = "✓ Correct" if result['correct'] else "✗ Incorrect"
            
            rel_path = Path(result['image_path']).relative_to(Path(__file__).parent)
            
            html += f"""
            <div class="{card_class}">
                <img src="file:///{result['image_path']}" alt="{result['true_class']}">
                <div class="image-info">
                    <div class="loss">Loss: {result['loss']:.4f}</div>
                    <div class="prediction">Predicted: <strong>{result['pred_class']}</strong></div>
                    <div class="confidence">Confidence: {result['pred_prob']*100:.1f}%</div>
                    <div class="{status_class}">{status_text}</div>
                    <div style="font-size: 10px; color: #999; margin-top: 5px; word-break: break-all;">
                        {rel_path}
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function"""
    print("=" * 70)
    print("Training Error Analysis Tool")
    print("=" * 70)
    
    # Check if model exists
    model_path = Path(__file__).parent.parent / 'models' / 'bird_plane_superman_classifier_latest.pth'
    if not model_path.exists():
        print("\n❌ Model not found! Please train the model first:")
        print("   python train_classifier.py")
        return
    
    # Load model
    print("\n📦 Loading model...")
    model, metadata = load_model()
    class_names = metadata['class_names']
    print(f"✓ Model loaded with {len(class_names)} classes: {', '.join(class_names)}")
    
    # Choose dataset
    print("\n📁 Which dataset to analyze?")
    print("1. Training set (dataset/train/)")
    print("2. Validation set (dataset/val/)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    data_split = 'train' if choice == '1' else 'val'
    data_dir = Path(__file__).parent / 'dataset' / data_split
    
    if not data_dir.exists():
        print(f"\n❌ Dataset not found: {data_dir}")
        return
    
    # Load data
    print(f"\n📊 Loading {data_split} dataset...")
    data_loader, dataset = get_data_loader(data_dir)
    print(f"✓ Loaded {len(dataset)} images")
    
    # Analyze
    results = analyze_errors(model, data_loader, dataset)
    
    # Generate report
    output_path = Path(__file__).parent / f'error_analysis_{data_split}.html'
    print(f"\n📝 Generating HTML report...")
    generate_html_report(results, class_names, output_path)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print("=" * 70)
    
    total = len(results)
    correct = sum(1 for r in results if r['correct'])
    accuracy = correct / total * 100
    
    print(f"\n📊 Results Summary:")
    print(f"   Total images: {total}")
    print(f"   Correct predictions: {correct}")
    print(f"   Accuracy: {accuracy:.1f}%")
    
    # Per-class accuracy
    print(f"\n📈 Per-class accuracy:")
    for class_name in class_names:
        class_results = [r for r in results if r['true_class'] == class_name]
        class_correct = sum(1 for r in class_results if r['correct'])
        class_total = len(class_results)
        if class_total > 0:
            class_acc = class_correct / class_total * 100
            print(f"   {class_name}: {class_acc:.1f}% ({class_correct}/{class_total})")
    
    print(f"\n📄 Report saved to: {output_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Open the HTML report in your browser")
    print(f"   2. Review images with high loss")
    print(f"   3. Delete problematic images from dataset folders")
    print(f"   4. Retrain: python train_classifier.py")

if __name__ == '__main__':
    main()

