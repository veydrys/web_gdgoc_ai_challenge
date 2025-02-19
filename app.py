from flask import Flask, render_template, request, send_from_directory
import os
import fitz
from PIL import Image
import docx

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TRANSLATED_FOLDER = 'translated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRANSLATED_FOLDER'] = TRANSLATED_FOLDER

# xử lý văn bản
class TextNLP:
    @staticmethod
    def translate(text):
        return text.upper()

# xử lý ảnh
class ImageNLP:
    @staticmethod
    def translate_image(image_path):
        translated_path = os.path.join(TRANSLATED_FOLDER, "translated_" + os.path.basename(image_path))
        img = Image.open(image_path)
        img.save(translated_path)
        return translated_path

# xử lý tài liệu
class DocumentNLP:
    @staticmethod
    def translate_pdf(pdf_path):
        translated_path = os.path.join(TRANSLATED_FOLDER, "translated_" + os.path.basename(pdf_path))
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()

        for page in doc:
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            text = page.get_text("text")
            translated_text = TextNLP.translate(text)
            new_page.insert_text((50, 50), translated_text, fontsize=12)

        new_doc.save(translated_path)
        return translated_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image-translation', methods=['GET', 'POST'])
def image_translation():
    filename, translated_filename = None, None
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        translated_filepath = ImageNLP.translate_image(filepath)
        translated_filename = os.path.basename(translated_filepath)

    return render_template('image_translation.html', filename=filename, translated_filename=translated_filename)

@app.route('/document-translation', methods=['GET', 'POST'])
def document_translation():
    filename, translated_filename = None, None
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        filename = file.filename
        file_ext = filename.rsplit('.', 1)[-1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        if file_ext == 'pdf':
            translated_filepath = DocumentNLP.translate_pdf(filepath)
            translated_filename = os.path.basename(translated_filepath)

    return render_template('document_translation.html', filename=filename, translated_filename=translated_filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/translated/<filename>')
def translated_file(filename):
    return send_from_directory(TRANSLATED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
