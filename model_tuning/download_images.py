"""
Automated Image Downloader for Training Dataset

Fully automated image downloading for training your classifier.
No manual downloading required - just run and go!

Methods supported:
1. Bing Image Search API (best quality, requires free Azure API key)
2. DuckDuckGo Search (no API key needed, fully automated)
3. Unsplash API (high quality, requires free API key)

Usage:
    # Bing (recommended if you have API key)
    python download_images.py --bing
    
    # DuckDuckGo (no API key needed!)
    python download_images.py --duckduckgo
    
    # Unsplash (highest quality)
    python download_images.py --unsplash
    
    # Auto-detect (tries available methods)
    python download_images.py --auto
"""

import requests
from pathlib import Path
import time
import json
from urllib.parse import quote, urlencode
import hashlib
from PIL import Image
import io
import os
import sys

class ImageDownloader:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_image(self, url, filename):
        """Download a single image from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Verify it's actually an image
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save image
            img.save(filename, 'JPEG', quality=95)
            return True
            
        except Exception as e:
            print(f"  ⚠️  Failed to download {url}: {str(e)[:50]}")
            return False
    
    def download_from_urls_file(self, urls_file, category):
        """Download images from a text file containing URLs"""
        urls_path = Path(urls_file)
        if not urls_path.exists():
            print(f"❌ File not found: {urls_file}")
            return 0
        
        with open(urls_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"\n📥 Downloading {len(urls)} images for '{category}'...")
        
        downloaded = 0
        for i, url in enumerate(urls, 1):
            # Create filename from hash of URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            filename = self.output_dir / f"{category}_{i:04d}_{url_hash}.jpg"
            
            if filename.exists():
                print(f"  ⏭️  Skipping (exists): {filename.name}")
                continue
            
            print(f"  [{i}/{len(urls)}] Downloading...", end='')
            if self.download_image(url, filename):
                downloaded += 1
                print(f" ✓ Saved as {filename.name}")
            else:
                print(f" ✗ Failed")
            
            # Be nice to servers
            time.sleep(0.5)
        
        return downloaded
    
    def search_duckduckgo(self, query, max_images=100):
        """
        Search DuckDuckGo for images (no API key needed!)
        Uses DuckDuckGo's public image search API
        """
        print(f"\n🔍 Searching DuckDuckGo for '{query}'...")
        
        all_urls = []
        
        try:
            # DuckDuckGo image search endpoint
            url = "https://duckduckgo.com/"
            params = {"q": query, "t": "h_", "iax": "images", "ia": "images"}
            
            # Get the search page
            response = self.session.get(url, params=params)
            
            # Get vqd token (required for image search)
            import re
            vqd_match = re.search(r'vqd=([\d-]+)', response.text)
            if not vqd_match:
                print("  ⚠️  Could not extract search token")
                return []
            
            vqd = vqd_match.group(1)
            
            # Search for images
            search_url = "https://duckduckgo.com/i.js"
            headers = {
                "authority": "duckduckgo.com",
                "accept": "application/json, text/javascript, */*; q=0.01",
                "referer": "https://duckduckgo.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            offset = 0
            while len(all_urls) < max_images:
                params = {
                    "l": "us-en",
                    "o": "json",
                    "q": query,
                    "vqd": vqd,
                    "f": ",,,",
                    "p": "1",
                    "v7exp": "a",
                    "s": offset
                }
                
                response = self.session.get(search_url, params=params, headers=headers, timeout=10)
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    break
                
                for result in results:
                    if "image" in result:
                        all_urls.append(result["image"])
                
                print(f"  Found {len(results)} images (total: {len(all_urls)})")
                
                # Check if more results available
                if not data.get("next"):
                    break
                
                offset += len(results)
                time.sleep(1)  # Be nice to DuckDuckGo
                
                if len(all_urls) >= max_images:
                    break
                    
        except Exception as e:
            print(f"  ⚠️  Search error: {str(e)}")
            print("  💡 Tip: If DuckDuckGo doesn't work, try Bing API (free at Azure)")
        
        return all_urls[:max_images]
    
    def search_bing(self, query, max_images=100, api_key=None):
        """
        Search Bing for images
        Requires Bing Search API key from Azure
        """
        if not api_key:
            print("\n❌ Bing API key required!")
            print("\nTo get a Bing Search API key:")
            print("1. Go to https://portal.azure.com")
            print("2. Create a 'Bing Search v7' resource (Free tier available)")
            print("3. Copy one of the API keys")
            print("4. Set BING_API_KEY environment variable or pass as parameter")
            return []
        
        print(f"\n🔍 Searching Bing for '{query}'...")
        
        search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        
        all_urls = []
        offset = 0
        
        while len(all_urls) < max_images:
            params = {
                "q": query,
                "count": min(150, max_images - len(all_urls)),
                "offset": offset,
                "imageType": "photo",
                "size": "medium"
            }
            
            try:
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                images = data.get("value", [])
                if not images:
                    break
                
                for img in images:
                    all_urls.append(img["contentUrl"])
                
                print(f"  Found {len(images)} images (total: {len(all_urls)})")
                
                offset += len(images)
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  ⚠️  Search error: {str(e)}")
                break
        
        return all_urls[:max_images]
    
    def search_unsplash(self, query, max_images=100, api_key=None):
        """
        Search Unsplash for high-quality images
        Requires free Unsplash API key from https://unsplash.com/developers
        """
        if not api_key:
            print("\n❌ Unsplash API key required!")
            print("\nTo get a free Unsplash API key:")
            print("1. Go to https://unsplash.com/developers")
            print("2. Register your application (free)")
            print("3. Copy the Access Key")
            print("4. Set UNSPLASH_API_KEY environment variable")
            return []
        
        print(f"\n🔍 Searching Unsplash for '{query}'...")
        
        search_url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {api_key}"}
        
        all_urls = []
        page = 1
        
        while len(all_urls) < max_images:
            params = {
                "query": query,
                "per_page": 30,
                "page": page,
                "orientation": "landscape"
            }
            
            try:
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    break
                
                for result in results:
                    # Use regular size (not raw) for reasonable file sizes
                    all_urls.append(result["urls"]["regular"])
                
                print(f"  Found {len(results)} images (total: {len(all_urls)})")
                
                page += 1
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  ⚠️  Search error: {str(e)}")
                break
        
        return all_urls[:max_images]

def download_category_images(category, queries, method='duckduckgo', api_key=None, 
                             base_dir=None, train_count=100, val_count=25):
    """Download images for a single category using specified method"""
    
    print(f"\n{'='*70}")
    print(f"📥 Downloading {category.upper()} images")
    print(f"{'='*70}")
    
    for split, max_images in [('train', train_count), ('val', val_count)]:
        print(f"\n🎯 Collecting {max_images} images for {split} set...")
        
        output_dir = base_dir / split / category
        downloader = ImageDownloader(output_dir)
        
        # Collect URLs from all queries
        all_urls = []
        images_per_query = max_images // len(queries) + 1
        
        for query in queries:
            if method == 'bing':
                urls = downloader.search_bing(query, images_per_query, api_key)
            elif method == 'duckduckgo':
                urls = downloader.search_duckduckgo(query, images_per_query)
            elif method == 'unsplash':
                urls = downloader.search_unsplash(query, images_per_query, api_key)
            else:
                print(f"❌ Unknown method: {method}")
                return 0
            
            all_urls.extend(urls)
            
            if len(all_urls) >= max_images:
                break
        
        # Download images
        print(f"\n💾 Downloading {min(len(all_urls), max_images)} images...")
        downloaded = 0
        
        for i, url in enumerate(all_urls[:max_images], 1):
            filename = output_dir / f"{category}_{split}_{i:04d}.jpg"
            
            # Skip if exists
            if filename.exists():
                print(f"  [{i}/{max_images}] ⏭️  Already exists: {filename.name}")
                downloaded += 1
                continue
            
            print(f"  [{i}/{max_images}] Downloading...", end=' ')
            if downloader.download_image(url, filename):
                downloaded += 1
                print(f"✓ {filename.name}")
            else:
                print(f"✗ Failed")
            
            # Rate limiting
            time.sleep(0.5)
        
        print(f"\n✅ Downloaded {downloaded}/{max_images} {split} images for {category}")
    
    return downloaded


def main():
    """Main function"""
    print("=" * 70)
    print("🤖 FULLY AUTOMATED Image Downloader")
    print("=" * 70)
    print("\n✨ No manual downloading required - just choose your method!\n")
    
    base_dir = Path(__file__).parent / 'dataset'
    
    # Define search queries for each category
    search_queries = {
        'bird': [
            'eagle flying nature',
            'parrot colorful bird',
            'owl bird wildlife',
            'sparrow small bird',
            'hawk bird prey',
            'seagull bird flight'
        ],
        'plane': [
            'commercial airplane flying',
            'fighter jet aircraft',
            'boeing airplane',
            'cessna small plane',
            'military aircraft',
            'passenger airplane'
        ],
        'superman': [
            'superman flying hero',
            'superman movie scene',
            'man of steel superman',
            'superman comic book',
            'superman costume hero',
            'clark kent superman'
        ]
    }
    
    # Check command line arguments
    args = sys.argv[1:]
    
    # Determine method
    method = None
    bing_api_key = os.environ.get('BING_API_KEY')
    unsplash_api_key = os.environ.get('UNSPLASH_API_KEY')
    
    if '--bing' in args:
        if not bing_api_key:
            print("❌ Bing API key not found!")
            print("\n📝 To get a FREE Bing API key:")
            print("   1. Go to https://portal.azure.com")
            print("   2. Create 'Bing Search v7' resource (free tier: 1000 calls/month)")
            print("   3. Copy an API key")
            print("   4. Set environment variable:")
            print("      Windows: $env:BING_API_KEY=\"your-key\"")
            print("      Linux/Mac: export BING_API_KEY=\"your-key\"")
            return
        method = 'bing'
        api_key = bing_api_key
        print("🎯 Using Bing Image Search (best quality with API key)")
        
    elif '--unsplash' in args:
        if not unsplash_api_key:
            print("❌ Unsplash API key not found!")
            print("\n📝 To get a FREE Unsplash API key:")
            print("   1. Go to https://unsplash.com/developers")
            print("   2. Create an application (free)")
            print("   3. Copy the Access Key")
            print("   4. Set environment variable:")
            print("      Windows: $env:UNSPLASH_API_KEY=\"your-key\"")
            print("      Linux/Mac: export UNSPLASH_API_KEY=\"your-key\"")
            return
        method = 'unsplash'
        api_key = unsplash_api_key
        print("🎯 Using Unsplash (highest quality images)")
        
    elif '--duckduckgo' in args or '--auto' in args or len(args) == 0:
        method = 'duckduckgo'
        api_key = None
        print("🎯 Using DuckDuckGo (no API key needed!)")
        print("💡 Tip: For better results, get a free Bing API key")
        
    else:
        print("\n📋 Usage:")
        print("  python download_images.py --duckduckgo    # No API key needed (default)")
        print("  python download_images.py --bing          # Best quality (free API key)")
        print("  python download_images.py --unsplash      # Highest quality (free API key)")
        print("  python download_images.py --auto          # Auto-detect available method")
        print("\n💡 Run without arguments to use DuckDuckGo (no API key needed)")
        return
    
    print(f"\n📁 Dataset directory: {base_dir}")
    print("\n⚙️  Configuration:")
    print("   - Training images per category: 100")
    print("   - Validation images per category: 25")
    print("   - Total images per category: 125")
    print("   - Total download: ~375 images")
    
    response = input("\n▶️  Start downloading? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    print("\n" + "=" * 70)
    print("🚀 Starting automated download...")
    print("=" * 70)
    print("\n⏱️  This will take 10-20 minutes depending on your connection...")
    print("☕ Time to grab a coffee!\n")
    
    # Download images for each category
    start_time = time.time()
    total_downloaded = 0
    
    for category, queries in search_queries.items():
        downloaded = download_category_images(
            category=category,
            queries=queries,
            method=method,
            api_key=api_key,
            base_dir=base_dir,
            train_count=100,
            val_count=25
        )
        total_downloaded += downloaded
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   - Time elapsed: {elapsed/60:.1f} minutes")
    print(f"   - Total images: {total_downloaded}")
    print(f"   - Location: {base_dir}")
    
    print("\n🎯 Next steps:")
    print("   1. Train the model:")
    print("      python train_classifier.py")
    print("\n   2. After training, analyze errors:")
    print("      python analyze_training_errors.py")
    print("\n   3. Review high-loss images and delete bad ones")
    print("\n   4. Retrain for better accuracy!")
    
    print("\n💡 Tip: Error analysis helps you identify and remove")
    print("   problematic images - this is the key to high accuracy!")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()

