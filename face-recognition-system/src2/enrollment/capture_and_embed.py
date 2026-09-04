import os
import pickle
import numpy as np
from deepface import DeepFace

MODEL_NAME = "ArcFace"

def generate_average_embedding(image_folder):
    embeddings = []
    valid_extensions = (".jpg", ".jpeg", ".png")
    
    if not os.path.exists(image_folder):
        print(f"Directory not found: {image_folder}")
        return None

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(valid_extensions):
            img_path = os.path.join(image_folder, filename)
            try:
                rep = DeepFace.represent(img_path = img_path, 
                                         model_name = MODEL_NAME, 
                                         enforce_detection = True)
                if rep and len(rep) > 0:
                    embeddings.append(rep[0]["embedding"])
            except Exception as e:
                print(f"Could not process {filename}: {e}")
                
    if len(embeddings) > 0:
        return np.mean(embeddings, axis=0)
    return None

def save_enrollments():
    os.makedirs("models/registered_embeddings", exist_ok=True)
    
    # تحديث الأسماء لتشمل الأربعة أشخاص
    participants = ["lujain", "layan", "nouf", "yara"]
    for person in participants:
        folder = f"dataset/{person}"
        print(f"Processing enrollment for: {person}")
        avg_emb = generate_average_embedding(folder)
        
        if avg_emb is not None:
            save_path = f"models/registered_embeddings/{person}_embedding.pkl"
            with open(save_path, "wb") as f:
                pickle.dump(avg_emb, f)
            print(f"Saved embedding for {person} to {save_path}")
        else:
            print(f"Failed to generate embeddings for {person}")

if __name__ == "__main__":
    save_enrollments() 