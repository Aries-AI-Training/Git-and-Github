import cv2
import pickle
import numpy as np
from deepface import DeepFace

MODEL_NAME = "ArcFace"
THRESHOLD = 0.65

def load_registered_faces():
    database = {}
    participants = ["Lujain", "Layan", "Nouf", "Yara"]
    
    for person in participants:
        path = f"models/registered_embeddings/{person.lower()}_embedding.pkl"
        try:
            with open(path, "rb") as f:
                database[person] = pickle.load(f)
        except Exception:
            pass
            
    return database

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def run_webcam():
    database = load_registered_faces()
    if not database:
        print("Error: No registered embeddings found. Run enrollment first.")
        return

    cap = cv2.VideoCapture(0)
    print("Starting real-time face recognition... Press 'q' to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        try:
            demographies = DeepFace.extract_faces(img_path = frame, 
                                                  detector_backend = 'opencv', 
                                                  enforce_detection = False)
            
            for face_obj in demographies:
                facial_area = face_obj['facial_area']
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                
                face_img = frame[y:y+h, x:x+w]
                if face_img.size == 0:
                    continue

                rep = DeepFace.represent(img_path = face_img, 
                                         model_name = MODEL_NAME, 
                                         enforce_detection = False)
                
                if rep:
                    current_embedding = rep[0]["embedding"]
                    
                    best_match = "Unknown"
                    max_similarity = -1.0

                    for name, ref_embedding in database.items():
                        sim = cosine_similarity(current_embedding, ref_embedding)
                        if sim > max_similarity:
                            max_similarity = sim
                            best_match = name

                    if max_similarity < THRESHOLD:
                        best_match = "Unknown"

                    color = (0, 255, 0) if best_match != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    label = f"{best_match} ({max_similarity:.2f})"
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        except Exception:
            pass

        cv2.imshow('Real-Time Face Recognition - 4 Persons', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam()