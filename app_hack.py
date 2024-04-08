from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from speech2text_flutter import WhisperModel
import os

app = Flask(__name__)
whisper_model = WhisperModel()

# Configure upload folder
UPLOAD_FOLDER = '/Users/aidaizhusup/check_whisper/CHECK'
ALLOWED_EXTENSIONS = {'wav'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_config = config.get('db_conf')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config.get('user_name')}:{db_config.get('password')}@localhost:3306/{db_config.get('db_name')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/receive_data', methods=['POST'])
def receive_data():
    try:
        # Check if the POST request has the file part
        if 'audio' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['audio']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Check if the file extension is allowed
        if file and allowed_file(file.filename):
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the audio file
            text = whisper_model.generate_text_from_audio(filepath)
            response_data = {"text": text}
            return jsonify(response_data), 200
        else:
            return jsonify({"error": "Invalid file extension"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7575, debug=True)
