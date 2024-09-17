from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
import re
from tqdm import tqdm

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def secure_filename(filename):
    """
    Sanitize the filename to remove or replace invalid characters.
    """
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename

@app.route('/')
def index():
    # Ensure the upload folder exists when rendering the index page
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    return render_template_string('''
    <!doctype html>
    <title>File Transfer</title>
    <h1>Upload a file</h1>
    <input type="file" name="file" id="fileInput" style="display: block;">
    <h1>Download files</h1>
    <ul>
      {% for filename in files %}
      <li><a href="{{ url_for('download_file', filename=filename) }}">{{ filename }}</a></li>
      {% endfor %}
    </ul>
    <script>
      document.getElementById('fileInput').onchange = function(event) {
        var files = event.target.files;
        var formData = new FormData();
        for (var i = 0; i < files.length; i++) {
          formData.append('files[]', files[i]);
        }
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        xhr.onload = function () {
          if (xhr.status === 200) {
            window.location.reload();
          } else {
            alert('An error occurred!');
          }
        };
        xhr.send(formData);
      };
    </script>
    ''', files=os.listdir(UPLOAD_FOLDER))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('files[]')
    for file in tqdm(files, desc="Uploading files", unit="file"):
        if file.filename == '':
            continue
        secure_name = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
    return '', 200

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
