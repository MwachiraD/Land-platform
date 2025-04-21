import os

EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', 'env'}
EXCLUDE_FILES = {'.DS_Store'}
MAX_DEPTH = 2  # Adjust this to control how deep the tree goes

def short_tree(dir_path, prefix="", depth=0):
    if depth > MAX_DEPTH:
        return
    entries = sorted(os.listdir(dir_path))
    for i, entry in enumerate(entries):
        if entry in EXCLUDE_FILES:
            continue
        path = os.path.join(dir_path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        if os.path.isdir(path):
            if entry in EXCLUDE_DIRS:
                print(f"{prefix}{connector}{entry}/ (hidden)")
                continue
            print(f"{prefix}{connector}{entry}/")
            extension = "    " if is_last else "│   "
            short_tree(path, prefix + extension, depth + 1)
        else:
            print(f"{prefix}{connector}{entry}")

if __name__ == "__main__":
    print("project_root/")
    short_tree(".", "")
