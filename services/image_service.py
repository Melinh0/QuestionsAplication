import os
import zipfile
from io import BytesIO
from werkzeug.utils import secure_filename
import fitz  
import re

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_images_from_pdf(pdf_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    doc = fitz.open(pdf_path)
    image_names = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    base_name = re.sub(r'[^\w\-_]', '_', base_name)
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_name = f"{base_name}_pag{page_num+1:03d}.png"
        full_path = os.path.join(destination_folder, image_name)
        pix.save(full_path)
        image_names.append(image_name)
    doc.close()
    return image_names

def save_uploaded_images(files, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    saved_count = 0
    for file in files:
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
            filename = secure_filename(file.filename)
            file.save(os.path.join(destination_folder, filename))
            saved_count += 1
    return saved_count

def create_images_zip(topic_name, images_folder):
    if not os.path.exists(images_folder):
        return None
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if not image_files:
        return None
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in image_files:
            filepath = os.path.join(images_folder, filename)
            zf.write(filepath, arcname=filename)
    memory_file.seek(0)
    return memory_file
