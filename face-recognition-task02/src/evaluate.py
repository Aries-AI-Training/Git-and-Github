import os
import csv
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from src.matcher import FaceMatcher


# ==============================
# Settings
# ==============================

TEST_DIR = "dataset"
OUTPUT_FILE = "outputs/evaluation_results.csv"

THRESHOLD = 0.60


# ==============================
# Load ArcFace
# ==============================

print("Loading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(ctx_id=0, det_size=(640, 640))

print("ArcFace model loaded successfully.")


# ==============================
# Load registered embeddings
# ==============================

matcher = FaceMatcher(threshold=THRESHOLD)


# ==============================
# Evaluate one image
# ==============================

def process_image(image_path, actual_person):

    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not read image: {image_path}")
        return None

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face detected: {image_path}")
        return None

    # Take the largest face
    face = max(
        faces,
        key=lambda x: (x.bbox[2] - x.bbox[0])
        * (x.bbox[3] - x.bbox[1])
    )

    embedding = face.embedding

    predicted_person, similarity = matcher.identify_face(embedding)

    print(
        f"Actual: {actual_person:<8} | "
        f"Predicted: {predicted_person:<8} | "
        f"Similarity: {similarity:.4f}"
    )

    return {
        "actual": actual_person,
        "predicted": predicted_person,
        "similarity": similarity,
        "image": image_path
    }


# ==============================
# Main evaluation
# ==============================

def evaluate():

    print("\nStarting evaluation...")
    print("=" * 60)

    results = []

    # Four registered people
    people = ["Layan", "Lujain", "Nouf", "Yara"]

    for person in people:

        person_dir = os.path.join(TEST_DIR, person)

        if not os.path.exists(person_dir):
            print(f"Folder not found: {person_dir}")
            continue

        for filename in os.listdir(person_dir):

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            image_path = os.path.join(person_dir, filename)

            result = process_image(
                image_path,
                person
            )

            if result:
                results.append(result)

    # ==============================
    # Save results
    # ==============================

    os.makedirs("outputs", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "actual",
                "predicted",
                "similarity",
                "image"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    # ==============================
    # Calculate metrics
    # ==============================

    total = len(results)

    correct = sum(
        1
        for r in results
        if r["actual"].lower() == r["predicted"].lower()
    )

    false_rejection = sum(
        1
        for r in results
        if r["actual"] != "Unknown"
        and r["predicted"] == "Unknown"
    )

    false_acceptance = sum(
        1
        for r in results
        if r["actual"] == "Unknown"
        and r["predicted"] != "Unknown"
    )

    accuracy = (
        correct / total * 100
        if total > 0
        else 0
    )

    # ==============================
    # Summary
    # ==============================

    print("\n")
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"Total samples: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"False Acceptance: {false_acceptance}")
    print(f"False Rejection: {false_rejection}")

    print(
        f"\nResults saved to: {OUTPUT_FILE}"
    )


# ==============================
# Run
# ==============================

if __name__ == "__main__":
    evaluate()