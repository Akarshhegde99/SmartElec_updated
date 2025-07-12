import cv2
import face_recognition
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(text):
    speaker = Dispatch('SAPI.Spvoice')
    speaker.speak(text)

print("Press 1 to vote 'UNITED CONGRESS PARTY'")
print("Press 2 to vote 'UNITED REPUBLICAN FRONT'")
print("Press 3 to vote 'UNITED LEFT FRONT'")
print("Press 4 to vote 'NEW INDEPENDENT PARTY'")

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

with open('data/names.pkl', 'rb') as f:
    LABELS = pickle.load(f)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

COL_NAMES = ['NAME', 'VOTE', 'DATE', 'TIME']
gui_width, gui_height = 1400, 700
background = cv2.imread("background_img.png")

def check_if_exists(name):
    try:
        with open("Votes.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == name:
                    return True
    except FileNotFoundError:
        return False
    return False

output_name = None

while True:
    ret, frame = video.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_crop = rgb[y:y+h, x:x+w]
        face_crop = cv2.resize(face_crop, (150, 150))
        encodings = face_recognition.face_encodings(face_crop)

        if len(encodings) > 0:
            distances = face_recognition.face_distance(FACES, encodings[0])
            min_distance = min(distances)
            idx = np.argmin(distances)

            if min_distance < 0.45:
                output_name = LABELS[idx]
                ts = time.time()
                date = datetime.fromtimestamp(ts).strftime("%d-%m-%y")
                timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

                if check_if_exists(output_name):
                    speak("You have already voted")
                    print("You have already voted")
                    video.release()
                    cv2.destroyAllWindows()
                    exit()

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y-40), (x+w, y), (0, 0, 255), -1)
                cv2.putText(frame, output_name, (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            else:
                output_name = None

    if background is not None:
        bg_resized = cv2.resize(background, (gui_width, gui_height))
        frame_resized = cv2.resize(frame, (640, 480))
        bg_resized[150:150+480, 50:50+640] = frame_resized
        cv2.imshow('Voting Booth', bg_resized)
    else:
        cv2.imshow('Voting Booth', frame)

    key = cv2.waitKey(1)

    if output_name:
        vote_cast = None
        if key == ord('1'):
            vote_cast = "United Congress Party"
        elif key == ord('2'):
            vote_cast = "United Republican Front"
        elif key == ord('3'):
            vote_cast = "United Left Front"
        elif key == ord('4'):
            vote_cast = "New Independent Party"

        if vote_cast:
            speak("Your vote has been recorded")
            with open("Votes.csv", "a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not os.path.exists("Votes.csv") or os.path.getsize("Votes.csv") == 0:
                    writer.writerow(COL_NAMES)
                writer.writerow([output_name, vote_cast, date, timestamp])
            speak("Thank you for participating in the elections")
            time.sleep(3)
            break

    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
