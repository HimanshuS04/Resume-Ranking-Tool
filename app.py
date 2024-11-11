import os
from flask import Flask, flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
import nlp
import db 
import datetime
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # This should be set to a secure random value in production


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



@app.route('/')
def home():
    try:
        if session['data'][1]=="Employee":
            return redirect(url_for('employeePage'))
        else:
            return redirect(url_for('employerPage'))
    except Exception as e:
        return render_template('index.html',data=None)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/signupPage')
def signupPage():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():
    type = request.form['type']
    email = request.form['email']
    password = request.form['pass']
    username = request.form['username']
    companyName = request.form['companyName']
    if type == 'Employer':
        try:
            signup=db.sign_up(username,email,password,type,companyName)
            if signup==1:
                flash('Email already in use')
                return redirect(url_for('signupPage'))
            flash('Signup Successful')
            session['data']=db.sign_in(email,password)
            if session['data']:
                    return redirect(url_for('employerPage'))
            return redirect(url_for('signupPage'))
        except Exception as e:
            flash('Failed to signup')
            return redirect(url_for('signupPage'))
    else:
        try:
            signup=db.sign_up(username,email,password,type)
            if(signup==1):
                flash('Email already in use')
                return redirect(url_for('signupPage'))
            flash('Signup Successful')
            session['data']=db.sign_in(email,password)
            if session['data']:
                return redirect(url_for('employeePage'))
            return redirect(url_for('signupPage'))
        except Exception as e:
            flash('Failed to signup')
    return redirect(url_for('signupPage'))



@app.route('/loginPage', methods=['GET','POST'])
def loginPage():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pass']
    try:
        session['data']=db.sign_in(email,password)
        if session['data']:
            if session['data'][1]=='Employer':
                return redirect(url_for('employerPage'))
            else:
                return redirect(url_for('employeePage'))
        else:
            flash('Invalid Credentials')
            return redirect(url_for('loginPage'))
    except Exception as e:
        flash('Failed to Login')
    return redirect(url_for('loginPage'))


@app.route('/employeePage')
def employeePage():
    try:
        
        jobs=db.jobs()
        return render_template('employeePage.html',jobs=jobs)
    except Exception as e:
        print(e)
        return redirect(url_for('loginPage'))
        
@app.route('/jobStatus')
def jobStatus():
    
        status=db.get_application_status(session['data'][0])
        return render_template('jobStatus.html',status=status)
    

@app.route('/employerPage')
def employerPage():
     try:
        
        return render_template('employerPage.html')
     except Exception as e:
         print(e)
         return redirect(url_for('loginPage'))

@app.route('/postedJobs')
def postedJobs():
    try:
        jobs=db.get_jobs_by_employer(session['data'][0])
        return render_template('postedJobs.html', jobs=jobs)
    except Exception as e:
         print(e)
         return render_template('employerPage.html')

@app.route('/addjob', methods=['POST'])
def addjob():
    try:
        title = request.form['title']
        des = request.form['des']
        location = request.form['location']
        salary = request.form['salary']
        closingDate = request.form['closingDate']
        id=session['data'][0]
        db.add_job(employer_id=id, title=title, description=des, location=location, salary=salary, date_closing=closingDate)
        return redirect(url_for('employerPage'))
    except Exception as e:
        flash('Failed to add job')
        return redirect(url_for('employerPage'))


@app.route('/apply/<job_id>',methods=['GET','POST'])
def apply(job_id):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('employeePage'))
        file = request.files['file']
        if file.filename == '':
            flash('No File Selected')
            return redirect(url_for('employeePage'))
        if file and allowed_file(file.filename):
           
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            try:
                description=db.get_job_description(job_id)
                score=nlp.score_resume(file_path,description)
                os.remove(file_path)
                db.apply(job_id, session['data'][0], score)
                flash('File Uploaded')
            except Exception as e:
                print(e)
                flash(f'Failed to upload file : {e}')
            return redirect(url_for('employeePage'))
        else:
            flash('Invalid file type')
            return redirect(url_for('employeePage'))
    return



@app.route('/results/<job_id>')
def results(job_id):
    results = db.get_job_results(job_id)
    if results==[]:
        flash('Job not found')
        return redirect(url_for('employerPage'))
    try:
        return render_template('results.html', results=results)
    except Exception as e:
        flash(f'Failed to list or download blobs: {e}')
        return redirect(url_for('employerPage'))



@app.route('/accepted/<application_id>/<job_id>/')
def accepted(application_id, job_id):
    db.accepted(application_id)
    return redirect(url_for('results',job_id=job_id))


@app.route('/rejected/<application_id>/<job_id>/')
def rejected(application_id, job_id):
    db.rejected(application_id)
    return redirect(url_for('results',job_id=job_id))





@app.route('/delete_job/<job_id>/')
def delete_job(job_id):
    db.delete_job(job_id)
    return redirect(url_for('employerPage'))


@app.route('/logout')
def logout():
    session.pop('data', None)
    session.pop('loggedin', None)
    return redirect(url_for('loginPage'))


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)