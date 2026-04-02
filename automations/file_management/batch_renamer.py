import os

# ==== SETTINGS =====
folder_path = "/home/navya/Desktop/document-detection/not_id"
base_name = input("Enter new base filename: ")
start_number = 1
# ===================

files = sorted(os.listdir(folder_path))

counter = start_number

for filename in files:
    old_path = os.path.join(folder_path, filename)

    # skip folders
    if not os.path.isfile(old_path):
        continue

    # keep original extension
    name, ext = os.path.splitext(filename)

    new_filename = f"{base_name}_{counter}{ext}"
    new_path = os.path.join(folder_path, new_filename)

    # ✅ rename IN PLACE
    os.rename(old_path, new_path)

    print(f"Renamed: {filename} -> {new_filename}")
    counter += 1

print("\nAll files renamed successfully.")