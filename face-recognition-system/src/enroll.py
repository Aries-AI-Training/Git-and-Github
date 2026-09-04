import os
import pickle
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

def generate_embeddings():
    dataset_path = "dataset"
    embeddings_dir = "models"
    embeddings_file = os.path.join(embeddings_dir, "registered_embeddings.pkl")
    
    # Ensure models directory exists
    os.makedirs(embeddings_dir, exist_ok=True)
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset directory '{dataset_path}' not found!")
        return

    # Initialize MTCNN (Face Detector) and InceptionResnetV1 (FaceNet model) on CPU
    print("Loading FaceNet models...")
    mtcnn = MTCNN(keep_all=False, device='cpu')
    resnet = InceptionResnetV1(pretrained='vggface2').eval()

    registered_data = {}
    
    print("\n--- 🧠 Starting Face Enrollment with FaceNet 🧠 ---")
    
    # Loop through each person folder in dataset/
    for person_name in os.listdir(dataset_path):
        person_dir = os.path.join(dataset_path, person_name)
        
        # Skip if it is not a directory
        if not os.path.isdir(person_dir):
            continue
            
        print(f"\nProcessing images for: '{person_name}'...")
        person_embeddings = []
        
        # Loop through images of the person
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            
            try:
                # Load image using PIL
                img = Image.open(img_path)
                
                # Detect and crop face (returns a tensor of shape [3, 160, 160])
                img_cropped = mtcnn(img)
                
                if img_cropped is not None:
                    # Generate embedding (returns a tensor, convert to numpy vector)
                    with torch.no_grad():
                        embedding = resnet(img_cropped.unsqueeze(0)).numpy()[0]
                    person_embeddings.append(embedding)
                    print(f"  ✅ Successfully processed: {img_name}")
                else:
                    print(f"  ❌ No face detected in: {img_name}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {img_name}: {str(e)}")
        
        # Calculate the average embedding
        if person_embeddings:
            avg_embedding = np.mean(person_embeddings, axis=0)
            registered_data[person_name] = avg_embedding
            print(f"🎉 Generated representative embedding for '{person_name}' using {len(person_embeddings)} images.")
        else:
            print(f"⚠️ Warning: No valid embeddings generated for '{person_name}'!")

    # Save the dictionary of registered embeddings using Pickle
    if registered_data:
        with open(embeddings_file, "wb") as f:
            pickle.dump(registered_data, f)
        print(f"\n💾 All registered embeddings saved successfully to '{embeddings_file}'!")
    else:
        print("\n⚠️ No registered embeddings to save!")

if __name__ == "__main__":
    generate_embeddings()