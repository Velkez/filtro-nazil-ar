import cv2
import os
import time
import uuid

class CaptureManager:
    def __init__(self):
        self.base_capture_dir = "../capturas/"
        os.makedirs(self.base_capture_dir, exist_ok=True)
        self.current_flow_id = None
        self.flow_capture_dir = None
        self.captured_images_paths = []

    def start_new_flow_capture(self):
        """Prepara una nueva carpeta de captura para un flujo."""
        self.current_flow_id = str(uuid.uuid4())
        self.flow_capture_dir = os.path.join(self.base_capture_dir, f"{self.current_flow_id}-fotos-nazil")
        os.makedirs(self.flow_capture_dir, exist_ok=True)
        self.captured_images_paths = []
        return self.flow_capture_dir

    def capture_frame(self, frame, filter_state, frame_type):
        """
        Captura el frame y lo guarda con un nombre específico en la carpeta del flujo.
        
        Args:
            frame: El frame de la cámara para capturar.
            filter_state: Booleano, True si el filtro está activo.
            frame_type: 'sin_nazil' o 'con_nazil'.
        """
        if not self.flow_capture_dir:
            self.start_new_flow_capture()
        
        filename = f"{self.current_flow_id}-{frame_type}.jpg"
        filepath = os.path.join(self.flow_capture_dir, filename)
        
        cv2.imwrite(filepath, frame)
        self.captured_images_paths.append(filepath)
        
        print(f"Captura guardada: {filepath}")
        return filepath
        
    def get_captured_image_count(self):
        """Retorna el número de imágenes capturadas en el flujo actual."""
        return len(self.captured_images_paths)