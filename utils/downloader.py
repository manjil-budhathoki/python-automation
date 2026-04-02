from bing_image_downloader import downloader

# Define your keywords
keywords = ["student id card", "government id card", "driving license"]

# Download images for each keyword
for query in keywords:
    print(f"Downloading images for: {query}")
    downloader.download(
        query,
        limit=30,             # Number of images to download per keyword
        output_dir='dataset', # Folder where images will be saved
        adult_filter_off=True,
        force_replace=False,
        verbose=True
    )

print("Done! All images have been downloaded.")