import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from matcher import FaceMatcher


DATASET_DIR = "dataset"

THRESHOLDS = [
    0.40,
    0.50,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80
]


print("Loading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("Model loaded.")


def get_embeddings_from_person(person):

    person_dir = os.path.join(
        DATASET_DIR,
        person
    )

    embeddings = []

    if not os.path.exists(person_dir):
        return embeddings

    for filename in os.listdir(person_dir):

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        image_path = os.path.join(
            person_dir,
            filename
        )

        image = cv2.imread(image_path)

        if image is None:
            continue

        faces = app.get(image)

        if len(faces) == 0:
            continue

        face = max(
            faces,
            key=lambda f:
            (f.bbox[2] - f.bbox[0]) *
            (f.bbox[3] - f.bbox[1])
        )

        embeddings.append(face.embedding)

    return embeddings


def run_experiment():

    matcher = FaceMatcher(
        threshold=0.65
    )

    print("\nRegistered people:")

    for person in matcher.database:
        print("-", person)

    print("\nThreshold Experiment")
    print("=" * 60)

    # Get similarities of enrollment images
    # against their registered identity.

    results = []

    for person in matcher.database:

        embeddings = get_embeddings_from_person(
            person
        )

        for embedding in embeddings:

            similarity = matcher.cosine_similarity(
                embedding,
                matcher.database[person]
            )

            results.append(
                (person, similarity)
            )

    for threshold in THRESHOLDS:

        accepted = 0
        rejected = 0

        for person, similarity in results:

            if similarity >= threshold:
                accepted += 1
            else:
                rejected += 1

        print(
            f"Threshold: {threshold:.2f} | "
            f"Accepted: {accepted} | "
            f"Rejected: {rejected}"
        )


if __name__ == "__main__":
    run_experiment()