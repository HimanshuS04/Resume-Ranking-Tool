import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import extract as cs

UPLOAD_FOLDER = 'uploads'  # Temporary folder for local storage
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# Azure Blob Storage configuration
connection_string ="DefaultEndpointsProtocol=https;AccountName=dbholder;AccountKey=YTzkyTfhB90UljYSI+4YJX/WD+4Z8iNo+dFQXbH1a691Mpz2M/al0gQQmVBvpQjqHjltnrnBF7YP+AStwbMo+A==;BlobEndpoint=https://dbholder.blob.core.windows.net/;FileEndpoint=https://dbholder.file.core.windows.net/;TableEndpoint=https://dbholder.table.core.windows.net/;QueueEndpoint=https://dbholder.queue.core.windows.net/"  # Replace with your Azure Storage connection string
container_name = "resumes"  # Replace with your Azure container name

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # This should be set to a secure random value in production

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('home.html')



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No File Selected')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save file locally
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Upload file to Azure Blob Storage
            try:
                blob_client = container_client.get_blob_client(filename)
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data)
                os.remove(file_path)  # Remove file from local storage after uploading to Azure
                flash('File Uploaded')
            except Exception as e:
                flash(f'Failed to upload file to Azure Blob Storage: {e}')
            return redirect(url_for('home'))
        else:
            flash('Invalid file type')
            return redirect(url_for('home'))
    return

@app.route('/result')
def result():
    des=request.args.get('des')
    if des == '':
        flash('Invalid Input')
        return redirect(url_for('home'))
    resume_folder = 'uploads'
    ranked_resumes = cs.main(resume_folder, des)
    return render_template('results.html', ranked_resumes=ranked_resumes)

@app.route('/uploads/<name>')
def download_file(name):
    try:
        # Download file from Azure Blob Storage
        blob_client = container_client.get_blob_client(name)
        download_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    except Exception as e:
        flash(f'Failed to download file from Azure Blob Storage: {e}')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
