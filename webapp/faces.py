import cv2
import face_recognition
import numpy as np
import pickle
import os

known_face_encodings = []
known_face_metadata = []

ratio = float(os.environ.get('FACE_RATIO', 0.25))
face_loc_model = os.environ.get('FACE_LOC_MODEL', 'hog')
face_loc_ntu = int(os.environ.get('FACE_LOC_NTU', 1))


def load_known_faces(filename,logger):
    global known_face_encodings, known_face_metadata
    logger.info("Load model from disk: %s" % filename)
    try:
        with open(filename, "rb") as face_data_file:
            known_face_encodings, known_face_metadata = pickle.load(face_data_file)
            logger.info("Known faces loaded from disk.")
    except FileNotFoundError as e:
        logger.critical("No model face found")
        pass



def find_and_mark_faces(frame, logger):
    small_frame = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
    face_locations = face_recognition.face_locations(small_frame, face_loc_ntu,face_loc_model )
    names = []
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_metadata[best_match_index]
        names.append(name)

        logger.info("face_locations = %s, names = %s", face_locations, names)

        for (top, right, bottom, left), name in zip(face_locations, names):
            # Green
            color = (0, 153, 51)
            if name == "Unknown":
                # Red
                color = (0, 0, 255)
            add_name_box(frame, left, top, bottom, right, name, color)

    return frame


def add_name_box(frame, left, top, bottom, right, name, color):
    inv_ratio = 1.0 / ratio
    top = int(top * inv_ratio)
    right = int(right * inv_ratio)
    bottom = int(bottom * inv_ratio)
    left = int(left * inv_ratio)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
