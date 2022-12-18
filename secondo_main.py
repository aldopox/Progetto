from camera import * # *= importa tutto quello che ho scritto su camera
from recognizer import * # *= importa tutto quello che ho detto su recognizer
import cv2
import time
import requests

url = 'http://127.0.0.1:5000/datastream'


def get_cam_id():
    try:
        with open('ID') as f:
            lines = f.readlines()
        cam_id = lines[0]
    except FileNotFoundError:
        print()
        print("Benvenuto!")
        cam_id = input("Inserisci qui un identificativo per la fotocamera per continuare: ")
        f = open("ID", "w")
        f.write(cam_id)
        f.close()
        print(f"Grazie. {cam_id} è l'ID associato alla tua fotocamera")
        print()
    return cam_id

def publish_data(cam_id, found_objects):
    data = {'CAMERA_ID': cam_id, 'ITEMS': str(found_objects)}
    r = requests.post(url, data=data)

cam_id = get_cam_id()
cam = initLocalCam(0)

recognizer = Recognizer()

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("Ops, qualcosa è andato storto!")
        break
    frame, preds = recognizer.run(frame)
    found_objects = [dict["name"] for dict in preds]
    print("Oggetti trovati:"+str(found_objects))
    publish_data(cam_id, found_objects)
    time.sleep(1)

    cv2.imshow("", frame)

    print("Premi Esc per chiudere la fotocamera")

    k = cv2.waitKey(1)

    if k%256==27:
        print()
        print("Chiudo fotocamera")
        break

cam.release()
cv2.destroyAllWindows()

