import os
import pickle
import numpy as np
import cv2
from insightface.app import FaceAnalysis


# -----------------------------
# Settings
# -----------------------------

DATASET_DIR = "dataset"
OUTPUT_DIR = "models/registered_embeddings"

PEOPLE = ["Layan", "lujain", "Nouf", "yara"]

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


# -----------------------------
# Initialize ArcFace model
# -----------------------------

print("Loading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(ctx_id=0, det_size=(640, 640))

print("ArcFace model loaded successfully.")


# -----------------------------
# Generate embeddings
# -----------------------------

def generate_average_embedding(person_folder):

    embeddings = []

    if not os.path.exists(person_folder):
        print(f"Folder not found: {person_folder}")
        return None

    for filename in os.listdir(person_folder):

        if not filename.lower().endswith(IMAGE_EXTENSIONS):
            continue

        image_path = os.path.join(person_folder, filename)

        try:

            # Read the image using OpenCV
            image = cv2.imread(image_path)

            if image is None:
                print(f"Could not read: {filename}")
                continue

            # Detect faces
            faces = app.get(image)

            if len(faces) == 0:
                print(f"No face detected: {filename}")
                continue

            # Take the largest detected face
            face = max(
                faces,
                key=lambda x: (x.bbox[2] - x.bbox[0])
                * (x.bbox[3] - x.bbox[1])
            )

            # Get face embedding
            embedding = face.embedding

            embeddings.append(embedding)

            print(f"Processed: {filename}")

        except Exception as e:

            print(f"Could not process {filename}: {e}")

    # No valid embeddings
    if len(embeddings) == 0:
        return None

    # Average all valid embeddings
    average_embedding = np.mean(embeddings, axis=0)

    # Normalize the final embedding
    average_embedding = average_embedding / np.linalg.norm(
        average_embedding
    )

    return average_embedding


# -----------------------------
# Save registered embeddings
# -----------------------------

def save_enrollments():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for person in PEOPLE:

        print("\n" + "=" * 50)
        print(f"Processing enrollment for: {person}")
        print("=" * 50)

        folder = os.path.join(DATASET_DIR, person)

        average_embedding = generate_average_embedding(folder)

        if average_embedding is None:

            print(f"Failed to generate embedding for {person}")
            continue

        save_path = os.path.join(
            OUTPUT_DIR,
            f"{person.lower()}_embedding.pkl"
        )

        with open(save_path, "wb") as file:
            pickle.dump(average_embedding, file)

        print(f"Saved embedding for {person}")
        print(f"Path: {save_path}")


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    save_enrollments()