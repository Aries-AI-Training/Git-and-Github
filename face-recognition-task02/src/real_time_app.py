import cv2
import time
import os
from insightface.app import FaceAnalysis
from matcher import FaceMatcher

# ==============================
# Settings
# ==============================

THRESHOLD = 0.65

DATASET_DIR = "dataset"

PEOPLE = {
    "1": "lujain",
    "2": "Layan",
    "3": "Nouf",
    "4": "yara"
}

TEST_IMAGES_PER_PERSON = 5


# ==============================
# Load ArcFace
# ==============================

print("Loading ArcFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(ctx_id=0, det_size=(640, 640))

print("ArcFace model loaded.")


# ==============================
# Load registered faces
# ==============================

matcher = FaceMatcher(
    embeddings_dir="models/registered_embeddings",
    threshold=THRESHOLD
)

print("\nRegistered people:")

for name in matcher.database.keys():
    print("-", name)


# ==============================
# Choose person
# ==============================

def choose_person():

    print("\n")
    print("=" * 50)
    print("WHO IS GOING TO TAKE TEST PHOTOS?")
    print("=" * 50)

    print("1 - Lujain")
    print("2 - Layan")
    print("3 - Nouf")
    print("4 - Yara")
    print("Q - Cancel")

    while True:

        choice = input("\nChoose person (1/2/3/4): ").strip().lower()

        if choice in PEOPLE:
            return PEOPLE[choice]

        if choice == "q":
            return None

        print("Invalid choice. Please choose 1, 2, 3, or 4.")


# ==============================
# Save test images
# ==============================

def capture_test_images(cap):

    person = choose_person()

    if person is None:
        print("Test capture cancelled.")
        return

    person_dir = os.path.join(
        DATASET_DIR,
        person
    )

    os.makedirs(
        person_dir,
        exist_ok=True
    )

    # Find existing test images
    existing_tests = [
        f
        for f in os.listdir(person_dir)
        if f.startswith("test_")
        and f.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

    start_number = len(existing_tests) + 1

    print("\n")
    print("=" * 60)
    print(f"TEST IMAGE CAPTURE FOR: {person}")
    print("=" * 60)
    print(f"We will capture {TEST_IMAGES_PER_PERSON} NEW images.")
    print("Change your position slightly between images.")
    print()
    print("Examples:")
    print("- Look straight")
    print("- Turn slightly left")
    print("- Turn slightly right")
    print("- Move closer/farther")
    print("- Change facial expression")
    print()

    input("Press ENTER when you are ready...")

    captured = 0

    while captured < TEST_IMAGES_PER_PERSON:

        ret, frame = cap.read()

        if not ret:
            print("Could not read frame.")
            continue

        faces = app.get(frame)

        # Display instructions
        cv2.putText(
            frame,
            f"{person} - Test {captured + 1}/{TEST_IMAGES_PER_PERSON}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "SPACE = Capture | Q = Cancel",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Draw detected faces
        for face in faces:

            x1, y1, x2, y2 = face.bbox.astype(int)

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Test Image Capture",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        # ==============================
        # SPACE = Capture
        # ==============================

        if key == 32:

            if len(faces) == 0:
                print("No face detected. Try again.")
                continue

            if len(faces) > 1:
                print("More than one face detected. Try again.")
                continue

            filename = (
                f"test_{start_number + captured:03d}.jpg"
            )

            save_path = os.path.join(
                person_dir,
                filename
            )

            success = cv2.imwrite(
                save_path,
                frame
            )

            if success:

                captured += 1

                print(
                    f"Saved: {save_path}"
                )

            else:

                print(
                    "Could not save image."
                )

        # ==============================
        # Q = Cancel
        # ==============================

        elif key == ord("q"):

            print("Test capture cancelled.")

            cv2.destroyAllWindows()

            return

    cv2.destroyAllWindows()

    print("\n")
    print("=" * 60)
    print(f"FINISHED: {person}")
    print("=" * 60)

    print(
        f"{TEST_IMAGES_PER_PERSON} test images saved in:"
    )

    print(
        person_dir
    )


# ==============================
# Real-Time Recognition
# ==============================

def run_recognition(cap):

    print("\nStarting real-time face recognition...")
    print("Press Q to exit.")

    prev_time = time.time()

    while True:

        ret, frame = cap.read()

        if not ret:

            print(
                "Could not read frame."
            )

            break

        faces = app.get(frame)

        for face in faces:

            # Bounding box
            x1, y1, x2, y2 = face.bbox.astype(int)

            # Embedding
            embedding = face.embedding

            # Identify
            name, similarity = matcher.identify_face(
                embedding
            )

            # Color
            if name == "Unknown":

                color = (0, 0, 255)

            else:

                color = (0, 255, 0)

            # Draw box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            # Display name
            label = (
                f"{name} | {similarity:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        # ==============================
        # FPS
        # ==============================

        current_time = time.time()

        fps = 1 / max(
            current_time - prev_time,
            0.001
        )

        prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Q: Exit",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Real-Time Face Recognition",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ==============================
# Main
# ==============================

def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "Could not open webcam."
        )

        return

    print("\n")
    print("=" * 60)
    print("FACE RECOGNITION SYSTEM")
    print("=" * 60)
    print("C = Capture NEW test images")
    print("R = Start real-time recognition")
    print("Q = Exit")
    print("=" * 60)

    while True:

        key = input(
            "\nEnter your choice (C/R/Q): "
        ).strip().lower()

        # ==============================
        # Capture Test Images
        # ==============================

        if key == "c":

            capture_test_images(
                cap
            )

        # ==============================
        # Recognition
        # ==============================

        elif key == "r":

            run_recognition(
                cap
            )

            break

        # ==============================
        # Exit
        # ==============================

        elif key == "q":

            break

        else:

            print(
                "Invalid choice. Please enter C, R, or Q."
            )

    cap.release()

    cv2.destroyAllWindows()

    print(
        "Camera stopped."
    )


# ==============================
# Run
# ==============================

if __name__ == "__main__":

    main()