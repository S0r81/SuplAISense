
#!/usr/bin/python3
from flask import Flask, render_template, session, redirect, request, flash, jsonify
from flask import make_response
from functools import wraps
import pymongo
from werkzeug.utils import secure_filename
from bson import ObjectId
from gridfs import GridFS
import os


app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient("mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
db = client.user_login_system
fs = GridFS(db)

# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Routes
from user import routes

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/dashboard/')
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    # Get the file from the request
    file = request.files['file']


    # Check if the file is a PDF
    if file and file.filename.endswith('.pdf'):
        # Get the user ID from the session
        user_id = session['user']['_id']

        # Store the file in MongoDB using GridFS
        file_id = fs.put(file, filename=file.filename, content_type="application/pdf", user_id=user_id)

        # Flash a success message
        flash('File uploaded successfully!')
    else:
        # Flash an error message
        flash('File must be a PDF!')

    # Redirect back to the dashboard
    return redirect('/dashboard')



@app.route('/get_uploaded_pdfs')
@login_required
def get_uploaded_pdfs():
    user_id = session['user']['_id']
    files = list(fs.find({"user_id": user_id}))
    return jsonify([{"file_id": str(file._id), "filename": file.filename, "url": f"/pdf/{file._id}"} for file in files])



@app.route('/pdf/<file_id>')
@login_required
def pdf(file_id):
    file = fs.get(ObjectId(file_id))
    response = make_response(file.read())
    response.headers.set("Content-Type", file.content_type)
    response.headers.set("Content-Disposition", f"inline; filename={file.filename}")
    return response

@app.route('/delete_pdf/<file_id>', methods=['POST'])
@login_required
def delete_pdf(file_id):
    try:
        fs.delete(ObjectId(file_id))
        return 'PDF deleted successfully', 200
    except Exception as e:
        print(e)
        return 'Error deleting PDF', 400

