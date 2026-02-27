import cv2
import time
import os
import numpy as np
import shutil
from comparative_image_creator import create_comparative_image # Importar el nuevo script

class FlowManager:
    def __init__(self):
        # Estados: INITIAL, FILTER_ON_COUNTDOWN, FILTER_ON_TAKEN, FILTER_OFF_COUNTDOWN, FILTER_OFF_TAKEN
        self.state = "INITIAL"
        self.countdown_start = 0
        self.countdown_duration = 5
        self.tracked_faces = {}
        self.max_faces = 3
        self.max_distance_threshold = 1.5  # metros
        self.frame_size = (0, 0) # Ancho y alto del frame
        self.capture_requested = False
        self.last_click_time = 0
        
        # Atributos para la gestión de archivos
        self.current_flow_dir = None
        self.captured_images = {} # Almacena los nombres de archivo de las fotos tomadas en el flujo
        
        # Cargar imágenes de botones
        self.initial_button = self.load_image("../assets/toca la pantalla para continuar.png")
        self.filter_off_button = self.load_image("../assets/sin nazil boton.png")
        self.filter_on_button = self.load_image("../assets/con nazil boton.png")

    def load_image(self, path):
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                # Redimensionar al cargar para no hacerlo en cada frame
                h, w = img.shape[:2]
                if w > 600 or h > 200:
                    ratio = min(600 / w, 200 / h)
                    img = cv2.resize(img, (int(w * ratio), int(h * ratio)))
                return img
        print(f"Warning: No se pudo cargar {path}")
        return None

    def handle_click(self):
        current_time = time.time()
        self.last_click_time = current_time
        print(f"[DEBUG] Click detectado, estado: {self.state}")

        if self.state == "INITIAL":
            # El primer clic inicia un nuevo flujo, crea la carpeta
            self.state = "FILTER_ON_COUNTDOWN"
            self.countdown_start = current_time
            self.start_new_flow()
            print(f"[DEBUG] Cambiado a FILTER_ON_COUNTDOWN, tracked_faces: {self.tracked_faces}")
        elif self.state == "FILTER_ON_TAKEN":
            # El segundo clic va a la cuenta regresiva sin filtro
            self.state = "FILTER_OFF_COUNTDOWN"
            self.countdown_start = current_time
        elif self.state == "FILTER_OFF_TAKEN":
            # El clic final reinicia el flujo
            self.state = "INITIAL"
            self.tracked_faces = {} # Reiniciar el seguimiento de rostros al final del flujo
            self.finalize_flow() # Limpiar la información del flujo después de completarlo

    def update(self, frame, face_landmarks_list):
        h, w = frame.shape[:2]
        self.frame_size = (w, h)
        current_time = time.time()
        self.capture_requested = False # Reiniciar el flag de captura

        # Manejar reinicio si los rostros desaparecen y el flujo ya está en marcha
        if self.state != "INITIAL" and self.should_reset_flow(face_landmarks_list):
            print("Rostro(s) perdido(s). Reiniciando el flujo.")
            self.state = "INITIAL"
            self.tracked_faces = {}
            self.delete_incomplete_flow_photos() # Eliminar fotos del flujo incompleto

        display_frame = frame.copy()
        
        # Lógica de estados actualizada
        if self.state == "INITIAL":
            self.draw_button(display_frame, self.initial_button)
            self.track_faces(face_landmarks_list, self.frame_size) # Solo rastrear en el estado inicial
        
        elif self.state == "FILTER_ON_COUNTDOWN":
            remaining = max(0, self.countdown_duration - int(current_time - self.countdown_start))
            self.draw_countdown(display_frame, remaining)
            self.draw_button(display_frame, self.filter_off_button) 
            if remaining == 0:
                self.state = "FILTER_ON_TAKEN"
                self.capture_requested = True
                # Guardar la foto inmediatamente aquí
                if self.get_capture_type() and self.current_flow_dir:
                    self.save_photo(frame, self.get_capture_type())
                
        elif self.state == "FILTER_ON_TAKEN":
            self.draw_capture_message(display_frame)
            self.draw_button(display_frame, self.filter_off_button)

        elif self.state == "FILTER_OFF_COUNTDOWN":
            remaining = max(0, self.countdown_duration - int(current_time - self.countdown_start))
            self.draw_countdown(display_frame, remaining)
            self.draw_button(display_frame, self.filter_on_button) 
            if remaining == 0:
                self.state = "FILTER_OFF_TAKEN"
                self.capture_requested = True
                # Guardar la foto inmediatamente aquí
                if self.get_capture_type() and self.current_flow_dir:
                    self.save_photo(frame, self.get_capture_type())

        elif self.state == "FILTER_OFF_TAKEN":
            self.draw_capture_message(display_frame)
            self.draw_button(display_frame, self.filter_on_button)
            
        return display_frame

    def start_new_flow(self):
        """Crea una carpeta para el nuevo flujo."""
        self.current_flow_dir = f"../capturas/flujo_{int(time.time())}"
        os.makedirs(self.current_flow_dir, exist_ok=True)
        self.captured_images = {}
        print(f"Nuevo flujo iniciado. Fotos se guardarán en: {self.current_flow_dir}")

    def save_photo(self, frame, capture_type):
        """Guarda una foto en la carpeta del flujo actual."""
        if self.current_flow_dir and capture_type not in self.captured_images:
            file_name = f"{capture_type}.png"
            file_path = os.path.join(self.current_flow_dir, file_name)
            cv2.imwrite(file_path, frame)
            self.captured_images[capture_type] = file_path
            print(f"Foto '{capture_type}' guardada en: {file_path}")

    def delete_incomplete_flow_photos(self):
        """Elimina la carpeta si el flujo fue interrumpido."""
        if self.current_flow_dir and os.path.exists(self.current_flow_dir):
            try:
                shutil.rmtree(self.current_flow_dir)
                print(f"Flujo incompleto eliminado: {self.current_flow_dir}")
            except OSError as e:
                print(f"Error al eliminar la carpeta {self.current_flow_dir}: {e}")
        self.current_flow_dir = None
        self.captured_images = {}

    def finalize_flow(self):
        """Finaliza el flujo de manera exitosa, manteniendo las fotos y creando la comparativa."""
        if self.current_flow_dir and len(self.captured_images) == 2:
            print(f"Flujo completado con éxito. Fotos guardadas en: {self.current_flow_dir}")
            
            # Llamar al nuevo script para crear la imagen comparativa
            # Asegurarse de que las fotos existan antes de llamar a la función
            path_con_nazil = self.captured_images.get('con-nazil')
            path_sin_nazil = self.captured_images.get('sin-nazil')

            if path_con_nazil and path_sin_nazil:
                # Corregir el orden para que "Sin Nazil" esté a la izquierda
                create_comparative_image(path_sin_nazil, path_con_nazil)
        
        self.current_flow_dir = None
        self.captured_images = {}

    def get_active_filter_state(self):
        """Determina si el filtro debe estar activo según el estado actual."""
        return self.state in ["FILTER_ON_COUNTDOWN", "FILTER_ON_TAKEN"]

    def should_capture(self):
        """Indica si se debe tomar una captura en el loop principal."""
        return self.capture_requested

    def get_capture_type(self):
        """Retorna el tipo de captura ('sin_nazil' o 'con_nazil')."""
        if self.state == "FILTER_ON_TAKEN":
            return "con-nazil"
        elif self.state == "FILTER_OFF_TAKEN":
            return "sin-nazil"
        return None

    def should_reset_flow(self, face_landmarks_list):
        """
        Reinicia el flujo si el número de rostros detectados cambia
        o si alguno de los rostros rastreados desaparece.
        """
        if self.state == "INITIAL":
            return False

        current_face_count = len(face_landmarks_list)
        tracked_face_count = len(self.tracked_faces)

        if current_face_count < tracked_face_count:
            return True

        return False

    def track_faces(self, face_landmarks_list, frame_size):
        """
        Rastrea y fija los rostros al inicio del flujo,
        respetando el límite de 3 personas y la distancia.
        """
        if len(self.tracked_faces) == self.max_faces:
            return

        for idx, face in enumerate(face_landmarks_list):
            if idx in self.tracked_faces:
                continue

            # Calcular el tamaño del rostro para estimar la distancia
            x_coords = [landmark.x for landmark in face]
            face_width = (max(x_coords) - min(x_coords)) * frame_size[0]

            # Umbral de tamaño para ~1.5m (ajustar si es necesario)
            # 0.2 es una estimación. Se puede necesitar calibración.
            size_threshold = frame_size[0] * 0.2 
            
            if face_width >= size_threshold:
                self.tracked_faces[idx] = True
            
            if len(self.tracked_faces) == self.max_faces:
                break
    
    def should_apply_filter_to_face(self, face_id):
        """Aplica el filtro solo a los rostros rastreados."""
        return face_id in self.tracked_faces

    def draw_button(self, frame, button_img):
        if button_img is None:
            return
        
        h, w = frame.shape[:2]
        button_h, button_w, _ = button_img.shape
        x_pos = (w - button_w) // 2
        y_pos = h - button_h - 260 # 20 píxeles de margen inferior
        
        # Superponer imagen con transparencia
        roi = frame[y_pos:y_pos+button_h, x_pos:x_pos+button_w]
        if button_img.shape[2] == 4:
            alpha_channel = button_img[:, :, 3] / 255.0
            for c in range(0, 3):
                roi[:, :, c] = (roi[:, :, c] * (1 - alpha_channel) +
                                 button_img[:, :, c] * alpha_channel)
        else:
            roi[:] = button_img
        
    def draw_countdown(self, frame, remaining_time):
        h, w = frame.shape[:2]
        text = f"Foto en: {remaining_time}"
        # Se ha cambiado la fuente a TRIPLEX y el grosor a 3
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_TRIPLEX, 1, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 150 
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 3)

    def draw_capture_message(self, frame):
        h, w = frame.shape[:2]
        text = "¡Foto tomada!"
        # Se ha cambiado la fuente a TRIPLEX y el grosor a 3
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_TRIPLEX, 1, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 150
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 0), 3)
