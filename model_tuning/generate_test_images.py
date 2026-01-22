"""
Generate Simple Test Images

This script creates basic synthetic images for testing the training pipeline.
Use this to verify everything works before collecting real training data.

These are NOT good for actual training - they're just for testing the system!
"""

from PIL import Image, ImageDraw, ImageFont
import random
from pathlib import Path

def generate_colored_image_with_text(text, color, size=(224, 224)):
    """Generate a simple colored image with text"""
    # Create image with solid color
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic font if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Add text in center
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text with contrasting color
    text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)
    draw.text(position, text, fill=text_color, font=font)
    
    # Add some random shapes for variety
    for _ in range(random.randint(2, 5)):
        shape_color = tuple(random.randint(0, 255) for _ in range(3))
        x1, y1 = random.randint(0, size[0]), random.randint(0, size[1])
        x2, y2 = random.randint(0, size[0]), random.randint(0, size[1])
        
        shape_type = random.choice(['circle', 'rectangle', 'line'])
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], outline=shape_color, width=2)
        elif shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], outline=shape_color, width=2)
        else:
            draw.line([x1, y1, x2, y2], fill=shape_color, width=2)
    
    return img

def create_test_dataset(num_images_per_category=10):
    """Create a small test dataset with synthetic images"""
    
    base_dir = Path(__file__).parent / 'dataset'
    
    categories = {
        'bird': [(135, 206, 250), (70, 130, 180), (176, 224, 230)],  # Blue tones
        'plane': [(192, 192, 192), (169, 169, 169), (211, 211, 211)],  # Gray tones
        'superman': [(220, 20, 60), (255, 0, 0), (178, 34, 34)]  # Red tones
        # No "other" class - confidence thresholding handles it!
    }
    
    splits = ['train', 'val']
    
    print("=" * 60)
    print("Generating Test Images")
    print("=" * 60)
    print("\n⚠️  NOTE: These are simple synthetic images for TESTING ONLY!")
    print("For real training, you need actual photos of birds, planes, etc.\n")
    
    for split in splits:
        print(f"\nGenerating {split} images...")
        
        for category, colors in categories.items():
            # Fewer images for validation
            num_images = num_images_per_category if split == 'train' else max(3, num_images_per_category // 3)
            
            output_dir = base_dir / split / category
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for i in range(num_images):
                # Pick a random color from the category's color palette
                color = random.choice(colors)
                
                # Add some variation
                color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in color)
                
                # Generate image
                img = generate_colored_image_with_text(
                    category.upper(),
                    color
                )
                
                # Save image
                filename = output_dir / f"{category}_{i:03d}.png"
                img.save(filename)
            
            print(f"  ✓ Created {num_images} {category} images in {split}/")
    
    print("\n" + "=" * 60)
    print("✅ Test dataset created!")
    print("=" * 60)
    print(f"\nLocation: {base_dir}")
    print(f"\nYou can now run: python train_classifier.py")
    print("\nReminder: These synthetic images are just for testing.")
    print("For a real classifier, replace these with actual photos!")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Test Image Generator")
    print("=" * 60)
    print("\nThis will create simple synthetic images for testing.")
    print("These images are NOT suitable for real training!\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    num_images = input("\nHow many training images per category? (default: 10): ")
    try:
        num_images = int(num_images) if num_images else 10
    except:
        num_images = 10
    
    create_test_dataset(num_images)
    
    print("\n📝 Next steps:")
    print("1. Run: python train_classifier.py")
    print("2. Run: python test_model.py")
    print("3. Run: streamlit run ../app.py")
    print("\n4. Then collect REAL images and retrain for actual use!")

if __name__ == '__main__':
    main()

