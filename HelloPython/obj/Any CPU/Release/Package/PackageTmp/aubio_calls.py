from flask import Flask

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

@app.route('/aubio/sample')
def sample():
    if len(sys.argv) < 2:
        sys.exit(1)

    filename = sys.argv[1]

    downsample = 1
    samplerate = 44100 // downsample
    if len( sys.argv ) > 2: samplerate = int(sys.argv[2])

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
    while True:
        samples, read = s()
        new_note = notes_o(samples)
        if (new_note[0] != 0):
            #note_str = ' '.join(["%.2f" % i for i in new_note])
            rowvalue = data.loc[data['MIDI_note_number'] == new_note[0]]['Note_names_English'].values
            #print("%.6f" % (total_frames/float(samplerate)), new_note, rowvalue)
            note_str = ' '.join("%.6f" % (total_frames/float(samplerate)), new_note, rowvalue)
        total_frames += read
        if read < hop_s: break
    return note_str