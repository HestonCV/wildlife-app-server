from flask import Flask, request, jsonify, send_file
import os
from sqlalchemy import desc
from models import db, User, Image, Camera

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/upload', methods=['POST'])
def upload_file():
    # get information sent from camera
    file = request.files['image']
    classification = request.form['classification']
    date = request.form['date']
    camera_id = request.form['camera_id']
    
    if file:
        # save the image to /uploads
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # add image data to database
        image = Image(filename=filename, classification=classification, date=date, camera_id=camera_id)
        db.session.add(image)
        db.session.commit()

        return 'Image uploaded successfully', 200
    return 'Failed to upload image', 400

@app.route('/images')
def serve_images():
    response_data = []

    images = Image.query.order_by(desc(Image.date)).all()
    for image in images:
        response_data.append({
            'url': f'http://192.168.1.145:5000/image/{image.filename}',
            'classification': image.classification,
            'date': str(image.date.strftime("%m-%d-%Y %-I:%M %p")),
            'id': image.id,
            'camera': image.camera.name,
        })
    return jsonify(response_data)

@app.route('/image/<filename>')
def serve_image(filename):
    image_path = os.path.join('./uploads', filename)
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)