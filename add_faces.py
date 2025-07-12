
import cv2
import face_recognition
import pickle
import numpy as np
import os

if not os.path.exists('data/'):
    os.makedirs('data/')

video = cv2.VideoCapture(0)
if not video.isOpened():
    print("Error: Could not open video source.")
    exit()

facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces_data = []
names = []

i = 0
name = input("Enter your Aadhar number: ")
framesTotal = 51
captureAfterFrame = 2

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = rgb[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (150, 150))
        encodings = face_recognition.face_encodings(face_img)
        if len(encodings) > 0 and len(faces_data) < framesTotal and i % captureAfterFrame == 0:
            faces_data.append(encodings[0])
            names.append(name)
        i += 1
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q') or len(faces_data) >= framesTotal:
        break

video.release()
cv2.destroyAllWindows()

# Load previous data
try:
    with open('data/faces_data.pkl', 'rb') as f:
        existing_faces = pickle.load(f)
    with open('data/names.pkl', 'rb') as f:
        existing_names = pickle.load(f)
    faces_data = existing_faces + faces_data
    names = existing_names + names
except:
    pass

with open('data/faces_data.pkl', 'wb') as f:
    pickle.dump(faces_data, f)
with open('data/names.pkl', 'wb') as f:
    pickle.dump(names, f)

print("Face data stored successfully.")
