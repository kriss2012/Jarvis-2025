import cv2
import numpy as np
from PIL import Image #pillow package
import os

path = 'backend\\auth\\samples' # Path for samples already taken

# Try to obtain a recognizer factory in a way that works across opencv versions
# Preferred API (opencv-contrib-python recent versions)
face_module = getattr(cv2, 'face', None)

if face_module is not None:
    # recent: cv2.face.LBPHFaceRecognizer_create
    # older face module: cv2.face.createLBPHFaceRecognizer
    creator = getattr(face_module, 'LBPHFaceRecognizer_create', None) or getattr(face_module, 'createLBPHFaceRecognizer', None)
else:
    # very old API: cv2.createLBPHFaceRecognizer
    creator = getattr(cv2, 'createLBPHFaceRecognizer', None)

if creator is None:
    raise ImportError("LBPHFaceRecognizer not found in cv2; please install opencv-contrib-python (pip install opencv-contrib-python).")

# create the recognizer instance
recognizer = creator()

detector = cv2.CascadeClassifier("backend\\auth\\haarcascade_frontalface_default.xml")
#Haar Cascade classifier is an effective object detection approach


def Images_And_Labels(path): # function to fetch the images and labels

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths: # to iterate particular image path

        gray_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_arr = np.array(gray_img,'uint8') #creating an array

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_arr)

        for (x,y,w,h) in faces:
            faceSamples.append(img_arr[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

print ("Training faces. It will take a few seconds. Wait ...")

faces,ids = Images_And_Labels(path)
recognizer.train(faces, np.array(ids))

recognizer.write('backend\\auth\\trainer\\trainer.yml')  # Save the trained model as trainer.yml

print("Model trained, Now we can recognize your face.")
 