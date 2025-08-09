import os
os.environ["MEDIAPIPE_GPU"] = "1"

import cv2
import mediapipe as mp
import numpy as np
import time
import urllib.request

print("=== Probando FaceMesh con GPU ===")

# Descargar imagen de prueba
url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=400&q=80"
urllib.request.urlretrieve(url, "test_face.jpg")

face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True
)

# Cargar imagen real
image = cv2.imread("test_face.jpg")
if image is None:
    print("Error cargando imagen")
    exit()

# Prueba de rendimiento con imagen real
start_time = time.time()
results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
elapsed = time.time() - start_time

if results.multi_face_landmarks:
    print(f"Rostro detectado en {elapsed:.4f} segundos")
    print(f"FPS aproximado: {1/elapsed:.2f}")
    
    # Dibujar landmarks
    for landmarks in results.multi_face_landmarks:
        for landmark in landmarks.landmark:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
    
    cv2.imwrite("resultado.jpg", image)
    print("Resultado guardado en resultado.jpg")
else:
    print("No se detectaron rostros")