"""
Download interesting test images from free sources.
Uses Unsplash Source API for random high-quality photos.
"""
import urllib.request
import os


def download_image(url, filename):
    """Download an image from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f"✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False


def main():
    output_dir = "test images"
    os.makedirs(output_dir, exist_ok=True)

    # Unsplash Source provides random images
    # Format: https://source.unsplash.com/{WIDTH}x{HEIGHT}/?{KEYWORD}

    images = [
        # Portrait/face
        ("https://source.unsplash.com/400x400/?portrait,face", "portrait_face.jpg"),

        # Landscape
        ("https://source.unsplash.com/500x300/?landscape,mountain", "landscape_mountain.jpg"),

        # Architecture
        ("https://source.unsplash.com/400x500/?architecture,building", "architecture_building.jpg"),

        # Animal
        ("https://source.unsplash.com/400x400/?animal,cat", "animal_cat.jpg"),

        # Nature
        ("https://source.unsplash.com/500x400/?nature,tree", "nature_tree.jpg"),

        # Urban/city
        ("https://source.unsplash.com/450x450/?city,urban", "city_urban.jpg"),

        # Abstract
        ("https://source.unsplash.com/400x400/?abstract,pattern", "abstract_pattern.jpg"),

        # Object/still life
        ("https://source.unsplash.com/350x350/?coffee,minimal", "object_coffee.jpg"),
    ]

    print("Downloading test images from Unsplash...")
    print("=" * 60)

    success_count = 0
    for url, filename in images:
        filepath = os.path.join(output_dir, filename)
        if download_image(url, filepath):
            success_count += 1

    print("=" * 60)
    print(f"Downloaded {success_count}/{len(images)} images successfully")
    print(f"Images saved to: {output_dir}/")


if __name__ == "__main__":
    main()
