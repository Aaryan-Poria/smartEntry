import cv2
import face_recognition
import os

# Load known images
known_encodings = []
known_names = []

known_dir = "known_images"
for file in os.listdir(known_dir):
    path = os.path.join(known_dir, file)
    img = cv2.imread(path)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_img)
    
    if encodings:  # Ensure at least one face is detected
        known_encodings.append(encodings[0])
        known_names.append(file.split('.')[0])  # Store name without extension

# Compare test images
test_dir = "test_images"
for file in os.listdir(test_dir):
    path = os.path.join(test_dir, file)
    test_img = cv2.imread(path)
    rgb_test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
    test_encodings = face_recognition.face_encodings(rgb_test_img)

    if test_encodings:  # Ensure at least one face is detected
        test_encoding = test_encodings[0]
        results = face_recognition.compare_faces(known_encodings, test_encoding)
        
        if True in results:
            match_index = results.index(True)
            print(f"Test image '{file}' matches '{known_names[match_index]}'")
        else:
            print(f"Test image '{file}' does not match any known person.")

