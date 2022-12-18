import cv2

#camera locale
def initLocalCam(camID):  
    cam = cv2.VideoCapture(camID) #0=front-cam, 1=back-cam
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    return cam

#leggi immagine da camera
def readImage(cam):
    ret, frame = cam.read()

    return frame