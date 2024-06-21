import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import extract as cs
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # This should be set to a secure random value in production

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/download_file')
def download():
    file=request.args.get('file')
    return redirect(url_for('download_file', name=file))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No File Selected')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File Uploaded')
            return redirect(url_for('home'))
        else :
            flash('Invalid file type')
            return redirect(url_for('home'))
    return


@app.route('/result')
def result():
    des=request.args.get('des')
    if des== '':
        flash('Invalid Input')
        return redirect(url_for('home'))
    resume_folder = 'uploads'
    keywords = cs.preprocess_text(des)
    ranked_resumes=cs.main(resume_folder, keywords, cs.COMPETENCIES)
    return render_template('results.html', ranked_resumes=ranked_resumes)

    


from flask import send_from_directory

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
    








