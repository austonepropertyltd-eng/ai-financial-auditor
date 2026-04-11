import os
import shutil

UPLOAD_DIR = "uploads"

def save_file(file):
    # create uploads folder if not exist
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path