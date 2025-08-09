import cv2
import numpy as np
import os

# Cargar textura solo una vez al inicio
texture_loaded = False
textura = None
TEXTURE_PATH = "../assets/ojos_irrita2.png"

if os.path.exists(TEXTURE_PATH):
    textura = cv2.imread(TEXTURE_PATH, cv2.IMREAD_UNCHANGED)
    if textura is not None:
        texture_loaded = True
else:
    print("Advertencia: No se encontró la textura. Usando color rojo plano.")

def aplicar_filtro_irritado(frame, mask, iris_info):
    if mask is None or mask.size == 0 or not iris_info:
        return frame

    final_frame = frame.copy()
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    
    # Crear máscara de exclusión de pupila
    pupil_exclusion = np.zeros_like(mask_gray)
    for iris in iris_info:
        center = iris['center']
        radius_pupil = int(iris['radius'] * 1.2)
        cv2.circle(pupil_exclusion, center, radius_pupil, 255, -1)
    
    # Crear máscara de esclera
    esclera_mask = cv2.subtract(mask_gray, pupil_exclusion)
    
    # Optimizar suavizado
    blurred_mask = cv2.GaussianBlur(esclera_mask, (15, 15), 0)
    blurred_mask_float = blurred_mask.astype(np.float32) / 955.0

    if texture_loaded and textura is not None:
        for iris in iris_info:
            center = iris['center']
            radius = int(iris['radius'] * 1.5)
            size_of_texture = int(radius * 2.5)
            
            # Calcular región de interés
            x_start = max(0, center[0] - size_of_texture // 2)
            y_start = max(0, center[1] - size_of_texture // 2)
            x_end = min(frame.shape[1], x_start + size_of_texture)
            y_end = min(frame.shape[0], y_start + size_of_texture)

            if x_end <= x_start or y_end <= y_start:
                continue
                
            region = final_frame[y_start:y_end, x_start:x_end]
            sub_mask = blurred_mask_float[y_start:y_end, x_start:x_end]
            
            # Redimensionar textura una sola vez
            resized_texture = cv2.resize(textura, (region.shape[1], region.shape[0]))
            
            if resized_texture.shape[2] == 4:
                alpha = resized_texture[:, :, 3] / 255.0
                texture_rgb = resized_texture[:, :, :3]
                
                # Mezcla vectorizada
                combined_alpha = sub_mask * alpha
                for c in range(3):
                    region[:, :, c] = region[:, :, c] * (1 - combined_alpha) + texture_rgb[:, :, c] * combined_alpha
            else:
                for c in range(3):
                    region[:, :, c] = region[:, :, c] * (1 - sub_mask) + resized_texture[:, :, c] * sub_mask
    else:
        # Aplicación de color optimizada
        rojo_capa = np.array([0, 0, 255], dtype=np.uint8)
        for c in range(3):
            final_frame[:, :, c] = (final_frame[:, :, c] * (1 - blurred_mask_float) + 
                                    rojo_capa[c] * blurred_mask_float)

    return final_frame.astype(np.uint8)