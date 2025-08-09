import os
import time
import uuid
import cv2

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.session_id = None
        self.capture_count = 0
        self.base_dir = "../capturas/"
        
    def start_new_session(self):
        """Inicia una nueva sesión con ID único"""
        self.session_id = str(uuid.uuid4())
        self.capture_count = 0
        self.current_session = {
            "id": self.session_id,
            "start_time": time.time(),
            "captures": []
        }
        
        # Crear directorio para la sesión
        session_dir = f"{self.base_dir}{self.session_id}-fotos-nazil/"
        os.makedirs(session_dir, exist_ok=True)
        
        return session_dir
    
    def record_capture(self, frame, is_filtered, session_dir):
        """Registra una captura en la sesión actual"""
        self.capture_count += 1
        
        # Determinar nombre del archivo
        prefix = "con-nazil" if is_filtered else "sin-nazil"
        filename = f"{self.session_id}-{prefix}.jpg"
        filepath = os.path.join(session_dir, filename)
        
        # Guardar imagen
        cv2.imwrite(filepath, frame)
        
        # Registrar en la sesión
        self.current_session["captures"].append({
            "path": filepath,
            "timestamp": time.time(),
            "is_filtered": is_filtered
        })
        
        return filepath
    
    def end_session(self):
        """Finaliza la sesión actual"""
        self.current_session["end_time"] = time.time()
        self.session_id = None
        self.capture_count = 0