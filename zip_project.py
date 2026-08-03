import os
import zipfile

def zip_folder(folder_path, output_zip_path):
    # Exclude directories
    exclude_dirs = {
        '.git', '.venv', 'venv', 'env', '__pycache__', '.vscode', '.idea',
        'dataset', 'datasets', 'Dataset', 'Datasets',
        'node_modules', 'dist', 'build', '.next', 'out'
    }
    
    # Exclude file extensions
    exclude_extensions = {
        # Models
        '.pt', '.pth', '.h5', '.hdf5', '.onnx', '.pb', '.tflite', '.pkl', '.joblib', '.bin', '.weights',
        # Datasets
        '.csv', '.tsv', '.db', '.sqlite',
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.svg',
        # Video/Audio
        '.mp4', '.avi', '.mov', '.wav', '.mp3', '.mkv',
        # Archives
        '.zip', '.tar', '.gz', '.rar', '.7z',
        # OS files
        '.ds_store', 'thumbs.db'
    }

    # Normalize paths
    folder_path = os.path.abspath(folder_path)
    output_zip_path = os.path.abspath(output_zip_path)
    
    print(f"Zipping {folder_path} to {output_zip_path}...")
    
    count_added = 0
    count_skipped = 0

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Modify dirs in-place to avoid traversing excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Avoid zipping the output zip file itself
                if os.path.abspath(file_path) == output_zip_path:
                    continue
                
                # Check extension
                _, ext = os.path.splitext(file.lower())
                
                # Check if it's in excluded extensions
                if ext in exclude_extensions or file.lower() in exclude_extensions:
                    print(f"Skipping file: {os.path.relpath(file_path, folder_path)}")
                    count_skipped += 1
                    continue
                
                # Also check if file is very large (e.g., > 5MB)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        print(f"Skipping large file (>5MB): {os.path.relpath(file_path, folder_path)} ({file_size / (1024*1024):.2f} MB)")
                        count_skipped += 1
                        continue
                except Exception:
                    pass
                
                # Add to zip
                rel_path = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, rel_path)
                count_added += 1
                
    print(f"\nDone! Added {count_added} files, skipped {count_skipped} files.")

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_zip = os.path.join(current_dir, 'smartsnakebite.zip')
    zip_folder(current_dir, output_zip)
