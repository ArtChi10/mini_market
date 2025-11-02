import os

def find_largest_file(start_path="/"):
    largest_file = None
    largest_size = 0

    for root, dirs, files in os.walk(start_path):
        for name in files:
            try:
                file_path = os.path.join(root, name)
                size = os.path.getsize(file_path)
                if size > largest_size:
                    largest_size = size
                    largest_file = file_path
            except (PermissionError, FileNotFoundError):
                continue

    return largest_file, largest_size

start_folder = os.path.expanduser("~")
file_path, size = find_largest_file(start_folder)

if file_path:
    print(f"Самый большой файл: {file_path}")
    print(f"Размер: {size / (1024 * 1024):.2f} МБ")
else:
    print("Файлы не найдены.")
