import cv2
import numpy as np

# Precalcular listas de puntos para mejor rendimiento
RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE_LANDMARKS = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466]
RIGHT_IRIS_POINTS = [469, 470, 471, 472]
LEFT_IRIS_POINTS = [474, 475, 476, 477]

# Predefinir arrays para reutilizar
eye_landmarks_list = [RIGHT_EYE_LANDMARKS, LEFT_EYE_LANDMARKS]
iris_points_list = [RIGHT_IRIS_POINTS, LEFT_IRIS_POINTS]

def get_eye_masks_optimized(frame, landmarks):
    if not landmarks:
        return np.zeros_like(frame), []
    
    h, w, _ = frame.shape
    mask = np.zeros((h, w, 3), dtype=np.uint8)
    iris_info = []

    for eye_landmarks, iris_points in zip(eye_landmarks_list, iris_points_list):
        try:
            # Crear array de puntos para el ojo
            eye_points = np.array([(
                int(landmarks[i].x * w),
                int(landmarks[i].y * h)
            ) for i in eye_landmarks], dtype=np.int32)
            
            # Dibujar polígono del ojo
            cv2.fillPoly(mask, [eye_points], (255, 255, 255))
            
            # Procesar iris
            iris_points_arr = np.array([(
                landmarks[i].x * w,
                landmarks[i].y * h
            ) for i in iris_points], dtype=np.float32)
            
            if len(iris_points_arr) >= 3:
                (x, y), radius = cv2.minEnclosingCircle(iris_points_arr)
                iris_info.append({
                    'center': (int(x), int(y)), 
                    'radius': int(radius)
                })
        except IndexError:
            continue

    # Optimizar operaciones de máscara
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    kernel = np.ones((3, 3), np.uint8)
    return cv2.erode(mask, kernel, iterations=1), iris_info