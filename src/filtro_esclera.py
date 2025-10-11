import cv2
import mediapipe as mp
import time
from esclera_detector import get_eye_masks_optimized
from filtro_esclera_aplicador import aplicar_filtro_irritado
from ui_manager import UIManager
from flow_manager import FlowManager
from capture_manager import CaptureManager

# Inicializamos los módulos de MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=4, # Aumentado para detectar un rostro extra, aunque el flujo solo use 3
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True
)

def main():
    # Inicializar administradores
    flow_manager = FlowManager()
    capture_manager = CaptureManager()

    # Crear UI Manager con la imagen del marco
    try:
        ui = UIManager("../assets/Nazil_MARCO.png")
    except FileNotFoundError as e:
        print(f"Error UI: {e}")
        ui = None

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    cv2.namedWindow('Filtro de Esclera', cv2.WINDOW_NORMAL)
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            flow_manager.handle_click()
    
    cv2.setMouseCallback('Filtro de Esclera', mouse_callback)
    
    prev_frame_time = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    fullscreen = False
    rotation_state = 1  # 0: sin rotar, 1: 90°, 2: 180°, 3: 270°

    print("Presiona 'q' para salir en la ventana.")
    print("Haz clic en cualquier parte de la pantalla para seguir el flujo.")
    print("Presiona 'F' para alternar pantalla completa")
    print("Presiona 'G' para rotar la cámara")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Medir FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # Aplicar rotación según el estado
        if rotation_state == 1:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation_state == 2:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation_state == 3:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # Para rotation_state == 0, no rotar

        frame = cv2.flip(frame, 1)
        
        h, w, _ = frame.shape
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_face = face_mesh.process(rgb_frame)
        face_landmarks_list = results_face.multi_face_landmarks or []
        
        # Lógica para reiniciar la captura si se pierde un rostro
        if flow_manager.state != "INITIAL" and len(face_landmarks_list) < len(flow_manager.tracked_faces):
            flow_manager.state = "INITIAL"
            flow_manager.tracked_faces = {}

        # Sincronizar el seguimiento de rostros con el estado inicial
        if flow_manager.state == "INITIAL":
            flow_manager.track_faces(face_landmarks_list, (w, h))

        # Determinar si el filtro debe estar activo
        filtro_activo = flow_manager.get_active_filter_state()
        
        display_frame = frame.copy()

        # Aplicar filtro si está activo y a los rostros rastreados
        if filtro_activo and face_landmarks_list:
            for face_id, landmarks_face in enumerate(face_landmarks_list):
                if flow_manager.should_apply_filter_to_face(face_id):
                    mask, iris_info = get_eye_masks_optimized(display_frame, landmarks_face.landmark)
                    if mask is not None and iris_info:
                        display_frame = aplicar_filtro_irritado(display_frame, mask, iris_info)
        
        # Manejar captura de pantalla antes de aplicar la UI del flujo
        if flow_manager.should_capture():
            capture_frame = frame.copy()
            
            # Aplicar filtro en el frame de captura si es necesario
            if flow_manager.get_capture_type() == "con-nazil" and face_landmarks_list:
                for face_id, landmarks_face in enumerate(face_landmarks_list):
                    if flow_manager.should_apply_filter_to_face(face_id):
                        mask, iris_info = get_eye_masks_optimized(capture_frame, landmarks_face.landmark)
                        if mask is not None and iris_info:
                            capture_frame = aplicar_filtro_irritado(capture_frame, mask, iris_info)

            # Aplicar el marco a la captura
            if ui:
                capture_frame = ui.apply_frame(capture_frame)

            # Iniciar nueva captura si es el primer paso del flujo
            if capture_manager.get_captured_image_count() == 0:
                capture_manager.start_new_flow_capture()
            
            capture_manager.capture_frame(capture_frame, filtro_activo, flow_manager.get_capture_type())

        # Aplicar UI principal si está disponible (este es el primer cambio importante)
        if ui:
            display_frame = ui.apply_frame(display_frame)

        # Actualizar el flujo y aplicar la UI (botones, contadores) sobre el marco
        # Esto asegura que los elementos se vean por encima del marco.
        display_frame = flow_manager.update(display_frame, face_landmarks_list)
        
        # Mostrar información de debug sobre el marco
        cv2.putText(display_frame, f"FPS: {int(fps)}", (10, 30), font, 0.7, (100, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(display_frame, f"Filtro: {'ON' if filtro_activo else 'OFF'}", 
                    (10, 70), font, 0.7, (0, 255, 0) if filtro_activo else (0, 0, 255), 2)
        cv2.putText(display_frame, f"Estado: {flow_manager.state}", 
                    (10, 110), font, 0.7, (255, 255, 0), 2)
        cv2.putText(display_frame, f"Rostros rastreados: {len(flow_manager.tracked_faces)}",
                    (10, 150), font, 0.7, (255, 100, 0), 2)


        cv2.imshow('Filtro de Esclera', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('f') or key == ord('F'):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty('Filtro de Esclera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty('Filtro de Esclera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        elif key == ord('g') or key == ord('G'):
            rotation_state = (rotation_state + 1) % 4

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

