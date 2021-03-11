import sys
import pandas as pd

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from aubio import source, notes

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

UPLOAD_FOLDER = 'C:\Python\Projects\Aubio\Site'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'aif', 'mid', 'midi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
@app.route('/hello')
def hello():
    # Render the page
    return """<h1>Hello Python!</h1>
    <a href='/aubio'>Aubio</a>"""

@app.route('/aubio/sample')
def sample():
    filename = "Piano a4 sound.mp3"

    downsample = 1
    samplerate = 44100 // downsample

    win_s = 512 // downsample # fft size
    hop_s = 256 // downsample # hop size

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    tolerance = 0.8

    notes_o = notes("default", win_s, hop_s, samplerate)

    print("%8s" % "time","[ start","vel","last ]")

    data = pd.read_csv("Midi_Notes.csv")

    # total number of frames read
    total_frames = 0
    note_str = """<style>
    table, th, td 
    { border: 1px solid black;}
    </style>
    <table>
    <tr><th>Interval</th><th>Start</th><th>Vel</th><th>Last</th><th>Note</th></tr>"""
    while True:
        samples, read = s()
        new_note = notes_o(samples)
        if (new_note[0] != 0):
            rowvalue = data.loc[data['MIDI_note_number'] == new_note[0]]['Note_names_English'].values
            #note_str += ' '.join(["%.2f" % i for i in new_note])
            note_str += '<tr><td>' + "%.6f" % (total_frames/float(samplerate)) 
            note_str += '</td><td> ' + '</td><td> '.join(["%.2f" % i for i in new_note])
            note_str += '</td><td>' + ' '.join([i for i in rowvalue]) + '</td></tr>'
            #note_str += "%.6f" % (total_frames/float(samplerate)) + ' '.join(["%.2f" % i for i in new_note]) + ' '.join([i for i in rowvalue]) + '</br>'
            #print("%.6f" % (total_frames/float(samplerate)), new_note, rowvalue)
            #note_str = note_str + ("<p>%.6f" % (total_frames/float(samplerate)), new_note, rowvalue, "</p>")
        total_frames += read
        if read < hop_s: break
    note_str += "</table>"
    return note_str


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/aubio', methods=['GET', 'POST'])
def upload_file():
    get_return = '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        #return get_return + "<p/>" + upload_notes(file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            return get_return + "<p/>" + upload_notes(save_path)
    else:
        return get_return

def upload_notes(filename):
    downsample = 1
    samplerate = 44100 // downsample

    win_s = 512 // downsample # fft size
    hop_s = 256 // downsample # hop size

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    tolerance = 0.8

    notes_o = notes("default", win_s, hop_s, samplerate)

    print("%8s" % "time","[ start","vel","last ]")

    data = pd.read_csv("Midi_Notes.csv")

    # total number of frames read
    total_frames = 0
    note_str = """<style>
    table, th, td 
    { border: 1px solid black;}
    </style>
    <table>
    <tr><th>Interval</th><th>Start</th><th>Vel</th><th>Last</th><th>Note</th></tr>"""
    while True:
        samples, read = s()
        new_note = notes_o(samples)
        if (new_note[0] != 0):
            rowvalue = data.loc[data['MIDI_note_number'] == new_note[0]]['Note_names_English'].values
            #note_str += ' '.join(["%.2f" % i for i in new_note])
            note_str += '<tr><td>' + "%.6f" % (total_frames/float(samplerate)) 
            note_str += '</td><td> ' + '</td><td> '.join(["%.2f" % i for i in new_note])
            note_str += '</td><td>' + ' '.join([i for i in rowvalue]) + '</td></tr>'
            #note_str += "%.6f" % (total_frames/float(samplerate)) + ' '.join(["%.2f" % i for i in new_note]) + ' '.join([i for i in rowvalue]) + '</br>'
            #print("%.6f" % (total_frames/float(samplerate)), new_note, rowvalue)
            #note_str = note_str + ("<p>%.6f" % (total_frames/float(samplerate)), new_note, rowvalue, "</p>")
        total_frames += read
        if read < hop_s: break
    note_str += "</table>"
    return note_str

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)