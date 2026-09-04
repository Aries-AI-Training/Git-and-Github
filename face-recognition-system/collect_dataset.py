import cv2
import os

def collect_images():
    # 1. Ask for the participant name (Open-ended for any person!)
    name = input("Enter the person's name: ").strip().lower()
    if not name:
        print("Error: Name cannot be empty!")
        return

    # Create directory if it doesn't exist
    save_dir = os.path.join("dataset", name)
    os.makedirs(save_dir, exist_ok=True)

    # 2. Initialize Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return

    # Load Haar Cascade face detector for visual feedback
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    print(f"\n--- 📸 Dataset Collection for '{name}' 📸 ---")
    print("1. Press 's' (Save) to capture and save an image.")
    print("2. Change face angles (left/right, up/down), expressions, lighting, and distance.")
    print("3. Press 'q' (Quit) when you are done.")
    print("---------------------------------------------\n")

    count = 0
    # Determine the starting number to avoid overwriting existing images
    existing_files = [f for f in os.listdir(save_dir) if f.endswith('.jpg')]
    if existing_files:
        numbers = [int(f.split('_')[-1].split('.')[0]) for f in existing_files if '_' in f]
        if numbers:
            count = max(numbers)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from webcam!")
            break

        # Create a copy for displaying bounding boxes
        display_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces for visual guide
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        for (x, y, w, h) in faces:
            # Draw green bounding box
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Overlay image counter
        cv2.putText(display_frame, f"Saved: {count} images", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Dataset Collection - Press 's' to Save, 'q' to Quit", display_frame)

        key = cv2.waitKey(1) & 0xFF
        
        # Save the original frame (without the green bounding box) when 's' is pressed
        if key == ord('s'):
            count += 1
            img_name = f"image_{count:03d}.jpg"
            img_path = os.path.join(save_dir, img_name)
            
            cv2.imwrite(img_path, frame)
            print(f"✅ Saved: {img_path}")
            
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n🎉 Finished! Total saved images for '{name}': {count}")

if __name__ == "__main__":
    collect_images()