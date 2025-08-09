import cv2
import mediapipe as mp
import numpy as np
import time
from esclera_detector import get_eye_masks_optimized
from filtro_esclera_aplicador import aplicar_filtro_irritado
from ui_manager import UIManager

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

    # Crear UI Manager con la imagen del marco
    try:
        ui = UIManager("../assets/Nazil_MARCO.png")  # Actualizar con ruta real
    except FileNotFoundError as e:
        print(f"Error UI: {e}")
        ui = None

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    # Configuración de resolución de la cámara
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Crear ventana ajustable y configurar callback de ratón
    cv2.namedWindow('Filtro de Esclera', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Filtro de Esclera', mouse_callback)
    
    # Variables para medir FPS
    prev_frame_time = 0
    new_frame_time = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Variables para control de pantalla completa
    fullscreen = False
    window_position = None
    window_size = None
    
    print("Presiona 'q' para salir en la ventana.")
    print("Haz clic en cualquier parte de la pantalla para activar/desactivar el filtro.")
    print("Presiona 'F' para alternar pantalla completa")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Medir FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        
        # Orientación vertical (modo retrato)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.flip(frame, 1)
        
        h, w, _ = frame.shape
        
        # Procesar en tamaño completo para mejor precisión
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar con MediaPipe en el frame completo
        results_face = face_mesh.process(rgb_frame)
        
        final_frame = frame.copy()

        if results_face.multi_face_landmarks and filtro_activo_global:
            for face_id, landmarks_face in enumerate(results_face.multi_face_landmarks):
                # Usar landmarks directamente sin escalado manual
                mask, iris_info = get_eye_masks_optimized(final_frame, landmarks_face.landmark)
                final_frame = aplicar_filtro_irritado(final_frame, mask, iris_info)

        # Aplicar UI si está disponible
        if ui:
            final_frame = ui.apply_frame(final_frame)
        
        # Mostrar FPS
        cv2.putText(final_frame, f"FPS: {int(fps)}", (10, 30), font, 0.7, (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(final_frame, f"Filtro: {'ON' if filtro_activo_global else 'OFF'}", 
                   (10, 70), font, 0.7, (0, 255, 0) if filtro_activo_global else (0, 0, 255), 2)
        cv2.putText(final_frame, f"Pantalla: {'Completa' if fullscreen else 'Normal'}", 
                   (10, 110), font, 0.7, (200, 200, 0), 2)

        cv2.imshow('Filtro de Esclera', final_frame)
        
        # Manejar teclas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('f') or key == ord('F'):
            fullscreen = not fullscreen
            
            if fullscreen:
                # Guardar posición y tamaño actual antes de cambiar
                window_position = cv2.getWindowImageRect('Filtro de Esclera')
                
                # Cambiar a pantalla completa
                cv2.setWindowProperty('Filtro de Esclera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                # Restaurar tamaño y posición original
                cv2.setWindowProperty('Filtro de Esclera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                
                # Restaurar posición y tamaño si estaban guardados
                if window_position:
                    x, y, width, height = window_position
                    cv2.resizeWindow('Filtro de Esclera', width, height)
                    cv2.moveWindow('Filtro de Esclera', x, y)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()