from imageai import Detection

class Recognizer:
    def __init__(self) -> None:
        self.recognizer = Detection.ObjectDetection()
        self.recognizer.setModelTypeAsYOLOv3()
        self.recognizer.setModelPath("yolo.h5") # altrimenti yolo-tiny.h5, considerare che E' PIU' VELOCE MA MENO PRECISO
        self.recognizer.loadModel()

    #restituisci frame con tag, nome oggetto e probabilità
    def run(self, img):
        img, preds = self.recognizer.detectCustomObjectsFromImage(input_image=img, 
                        custom_objects=None, input_type="array",
                        output_type="array",
                        minimum_percentage_probability=40,
                        display_percentage_probability=True,
                        display_object_name=True)
        return img, preds