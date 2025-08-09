import cv2
import numpy as np

RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE_LANDMARKS = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466]
RIGHT_IRIS_POINTS = [469, 470, 471, 472]
LEFT_IRIS_POINTS = [474, 475, 476, 477]

def get_eye_masks_optimized(frame, landmarks):
    h, w, _ = frame.shape
    mask = np.zeros((h, w, 3), dtype=np.uint8)  # Máscara 3-canales para compatibilidad
    iris_info = []

    if landmarks:
        for eye_landmarks, iris_points in zip(
            [RIGHT_EYE_LANDMARKS, LEFT_EYE_LANDMARKS],
            [RIGHT_IRIS_POINTS, LEFT_IRIS_POINTS]
        ):
            # Suavizado de puntos con media móvil
            eye_points = []
            for i in eye_landmarks:
                x = int(landmarks[i].x * w)
                y = int(landmarks[i].y * h)
                eye_points.append([x, y])
            
            if len(eye_points) > 0:
                cv2.fillPoly(mask, [np.array(eye_points)], (255, 255, 255))

                # Detección precisa del iris
                iris_points_arr = []
                for i in iris_points:
                    x = int(landmarks[i].x * w)
                    y = int(landmarks[i].y * h)
                    iris_points_arr.append([x, y])
                
                if len(iris_points_arr) > 0:
                    (x, y), radius = cv2.minEnclosingCircle(np.array(iris_points_arr))
                    center = (int(x), int(y))
                    
                    # Suavizado de posición del iris
                    iris_info.append({'center': center, 'radius': int(radius)})

    # Suavizado de máscara para reducir parpadeo
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
    
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)

    return mask, iris_info