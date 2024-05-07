import os
import json
from math import sqrt
#from sklearn import neighbors
from sklearn.neighbors import KNeighborsClassifier
from os import listdir
from os.path import isdir, join, isfile, splitext
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.cli import image_files_in_folder                                 #This is not working for me
#from face_recognition.face_recognition_cli import  image_files_in_folder                #comment this line if you got error
from flask import Flask, jsonify, request, redirect,render_template
from flask_cors import CORS
from os import path  
 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
REGISTER_PATH="./Register/"
TEMP_PATH="./Temp/"
if not os.path.exists(REGISTER_PATH):
    os.makedirs(REGISTER_PATH )

app = Flask(__name__)
CORS(app)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def upload_register():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return json.dumps({"status": "Error", "msg": "Image cannot be empty "})
        name = request.form.get('name')
        email = request.form.get('email')
        
       
        if(name ==''):
            return json.dumps({"status": "Error", "msg": "Name cannot be empty "})

        file = request.files['file']
       # src = path.realpath(REGISTER_PATH+"/"+email+"/"+name+"/"+file.filename)
       
        print(name)
        print(file)
        
       

        if file.filename == '':
            return json.dumps({"status": "Error", "msg": "Image cannot be empty "})

        if file and allowed_file(file.filename):
            if os.path.exists(REGISTER_PATH+email):

                #file.save(REGISTER_PATH+email+"/"+file.filename)
                foo = Image.open(file)
                #foo = foo.rotate(90, PIL.Image.NEAREST, expand = 1)
                foo.save(REGISTER_PATH+email+"/"+file.filename.strip(),optimize=True,quality=85)
                os.rename(REGISTER_PATH+email+"/"+file.filename,REGISTER_PATH+email+"/"+name+".jpg")
                
                #return json.dumps({"status": "Error", "msg": "User Already Registered"})
            else:
                os.makedirs(REGISTER_PATH+email)
                foo = Image.open(file)
                #file.save(REGISTER_PATH+email+"/"+file.filename)
                #foo = foo.rotate(90, PIL.Image.NEAREST, expand = 1)
                foo.save(REGISTER_PATH+email+"/"+file.filename.strip(),optimize=True,quality=85)
                os.rename(REGISTER_PATH+email+"/"+file.filename,REGISTER_PATH+email+"/"+name+".jpg")
                

            print(file)
            return json.dumps(train(REGISTER_PATH))
        else:
            return json.dumps({"status": "Error", "msg": "Image Format not supported <png,jpg,jpeg> "})

    # If no valid image file was uploaded, show the file upload form:
    return json.dumps ({"status":"Error","msg":"GET Not Allowed "})


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)
        foo = Image.open(file)
        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            print(file)
            #foo = foo.rotate(90, PIL.Image.NEAREST, expand = 1) 
            foo.save(TEMP_PATH+"/"+file.filename.strip(),optimize=True,quality=85)
            return json.dumps(predict(file))

    # If no valid image file was uploaded, show the file upload form:
    return render_template('index.html')


def predict(X_img_path, knn_clf = None, model_save_path ="train", DIST_THRESH = .5):

    # if not isfile(X_img_path) or splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
    #     raise Exception("invalid image path: {}".format(X_img_path))
    if knn_clf is None:
        with open(model_save_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # X_img = face_recognition.load_image_file(X_img_path)
    #X_img = face_recognition.load_image_file(X_img_path)
    X_img = face_recognition.load_image_file(TEMP_PATH+X_img_path.filename)
    X_faces_loc = face_locations(X_img)
    if len(X_faces_loc) == 0:
        return []

    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_faces_loc)

    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)

    is_recognized = [closest_distances[0][i][0] <= DIST_THRESH for i in range(len(X_faces_loc))]

    return [{"result":pred,"status":str(rec)} if rec else {"result":"N/A","status":str(rec)} for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_faces_loc, is_recognized)]


def train(train_dir, model_save_path="train", n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []
    for class_dir in listdir(train_dir):
        if not isdir(join(train_dir, class_dir)):
            continue
        for img_path in image_files_in_folder(join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            faces_bboxes = face_locations(image)
            if len(faces_bboxes) != 1:
                if verbose:
                    print("image {} not fit for training: {}".format(img_path, "didn't find a face" if len(
                        faces_bboxes) < 1 else "found more than one face"))
                continue
            X.append(face_recognition.face_encodings(image, known_face_locations=faces_bboxes)[0])
            y.append(class_dir)

    if n_neighbors is None:
        n_neighbors = int(round(sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically as:", n_neighbors)

    #knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf = KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    if model_save_path != "":
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)
    return {"status":"Success","msg":"Trained successfully"}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

'''
http://localhost:5001/         GET      web interface
http://localhost:5001/         POST     for face search variable name is search  return JSON
http://localhost:5001/register POST     for Registering face. variable names photo= file name = name
can be tested with postman

sample html will load 
'''
