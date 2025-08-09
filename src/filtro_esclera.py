import cv2
import mediapipe as mp
import numpy as np
import time
from esclera_detector import get_eye_masks_optimized
from filtro_esclera_aplicador import aplicar_filtro_irritado

# Inicializamos los módulos de MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=4,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True
)

# Variable global para controlar el estado del filtro
filtro_activo_global = False

def mouse_callback(event, x, y, flags, param):
    """Callback para manejar eventos de ratón (activar/desactivar filtro con click)"""
    global filtro_activo_global
    if event == cv2.EVENT_LBUTTONDOWN:
        filtro_activo_global = not filtro_activo_global
        print(f"Filtro {'activado' if filtro_activo_global else 'desactivado'} por click.")

def main():
    global filtro_activo_global

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    # Configuración de resolución de la cámara a 1080p
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Crear ventana ajustable y configurar callback de ratón
    cv2.namedWindow('Filtro de Esclera', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Filtro de Esclera', mouse_callback)
    
    print("Presiona 'q' para salir en la ventana.")
    print("Haz clic en cualquier parte de la pantalla para activar/desactivar el filtro.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Rotar el frame 90 grados (orientación vertical - modo retrato)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Aplicar efecto espejo horizontal (conservando orientación vertical)
        frame = cv2.flip(frame, 1)
        
        h_orig, w_orig, _ = frame.shape
        
        # Procesar en resolución original para mejor precisión
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_face = face_mesh.process(rgb_frame)
        
        final_frame = frame.copy()

        if results_face.multi_face_landmarks:
            for face_id, landmarks_face in enumerate(results_face.multi_face_landmarks):
                landmarks_face_orig = landmarks_face.landmark
                
                if filtro_activo_global:
                    # Usar resolución completa para mejor precisión
                    mask, iris_info = get_eye_masks_optimized(frame, landmarks_face_orig)
                    final_frame = aplicar_filtro_irritado(final_frame, mask, iris_info)
                    cv2.putText(final_frame, "Filtro Activo", (10 + face_id * 150, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(final_frame, "Filtro Inactivo", (10 + face_id * 150, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(final_frame, "Esperando rostro...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow('Filtro de Esclera', final_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()