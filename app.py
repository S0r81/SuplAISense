#!/usr/bin/python3
from flask import Flask, render_template, session, redirect, request, flash
from functools import wraps
import pymongo
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = client = pymongo.MongoClient("mongodb+srv://user:HIZ05Jh0NVv6YKg@suplaisense.8zr73kh.mongodb.net/?retryWrites=true&w=majority")
db = client.user_login_system

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

        # Securely save the file to disk
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Add the file and user ID to the database
        db.files.insert_one({'user_id': user_id, 'filename': filename})

        # Flash a success message
        flash('File uploaded successfully!')
    else:
        # Flash an error message
        flash('File must be a PDF!')

    # Redirect back to the dashboard
    return redirect('/dashboard')