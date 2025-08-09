import cv2
import numpy as np

class UIManager:
    def __init__(self, frame_path):
        # Cargar la imagen del marco con transparencia
        self.frame_img = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
        if self.frame_img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen del marco: {frame_path}")
        
        # Preprocesar la imagen para un rendimiento más rápido
        self.current_size = None
        self.cached_bgr = None
        self.cached_alpha = None
        
    def apply_frame(self, background):
        """Superpone el marco sobre el fondo manteniendo la transparencia"""
        h, w = background.shape[:2]
        
        # Solo redimensionar si el tamaño ha cambiado
        if self.current_size != (w, h) or self.cached_bgr is None:
            resized_frame = cv2.resize(self.frame_img, (w, h))
            
            # Separar canales solo una vez
            if resized_frame.shape[2] == 4:
                b, g, r, a = cv2.split(resized_frame)
                self.cached_bgr = cv2.merge((b, g, r))
                self.cached_alpha = a.astype(float) / 255.0
            else:
                self.cached_bgr = resized_frame
                self.cached_alpha = np.ones((h, w), dtype=float)
            
            self.current_size = (w, h)
        
        # Convertir a flotante para operaciones de mezcla
        bg_float = background.astype(float)
        
        # Crear máscara de transparencia invertida
        alpha_inv = 1.0 - self.cached_alpha
        
        # Aplicar transparencia usando multiplicación vectorizada
        for c in range(3):
            bg_float[:, :, c] = (bg_float[:, :, c] * alpha_inv + 
                                 self.cached_bgr[:, :, c] * self.cached_alpha)
        
        return bg_float.astype(np.uint8)