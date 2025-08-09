import cv2
import numpy as np
import os

TEXTURE_PATH = "../assets/ojos_irrita2.png"
texture_loaded = False
textura = None

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
    
    # Crear máscara para excluir la pupila (esclera solamente)
    esclera_mask = np.zeros_like(mask_gray)
    
    # Crear máscara de pluma suavizada que excluye la pupila
    pupil_exclusion = np.zeros_like(frame, dtype=np.uint8)
    for iris in iris_info:
        center = iris['center']
        radius_pupil = int(iris['radius'] * 1.2)
        cv2.circle(pupil_exclusion, center, radius_pupil, (255, 255, 255), -1)
    
    # Combinar máscaras: esclera completa menos pupila
    pupil_exclusion_gray = cv2.cvtColor(pupil_exclusion, cv2.COLOR_BGR2GRAY)
    esclera_mask = cv2.subtract(mask_gray, pupil_exclusion_gray)
    
    # Suavizado adicional de máscara
    blurred_mask = cv2.GaussianBlur(esclera_mask, (15, 15), 0)
    blurred_mask_float = blurred_mask.astype(np.float32) / 1055.0

    if texture_loaded and textura is not None:
        # Aplicar textura con suavizado
        for iris in iris_info:
            center = iris['center']
            radius = int(iris['radius'] * 1.5)
            size_of_texture = int(radius * 2.5)
            
            # Ajustar posición según rotación
            x_start = max(0, center[0] - size_of_texture // 2)
            y_start = max(0, center[1] - size_of_texture // 2)
            x_end = min(frame.shape[1], x_start + size_of_texture)
            y_end = min(frame.shape[0], y_start + size_of_texture)

            if x_end > x_start and y_end > y_start:
                sub_frame = final_frame[y_start:y_end, x_start:x_end]
                sub_mask = blurred_mask_float[y_start:y_end, x_start:x_end]
                
                # Asegurar tamaño válido
                if sub_mask.shape[0] > 0 and sub_mask.shape[1] > 0:
                    resized_texture = cv2.resize(textura, (sub_frame.shape[1], sub_frame.shape[0]))
                    
                    if resized_texture.shape[2] == 4:  # Textura con canal alpha
                        alpha_channel = resized_texture[:, :, 3] / 255.0
                        texture_rgb = resized_texture[:, :, :3]
                        
                        # Mezcla suavizada con canal alpha
                        for c in range(0, 3):
                            sub_frame[:, :, c] = (
                                sub_frame[:, :, c] * (1 - sub_mask * alpha_channel) + 
                                texture_rgb[:, :, c] * sub_mask * alpha_channel
                            )
                    else:
                        # Mezcla suavizada sin canal alpha
                        for c in range(0, 3):
                            sub_frame[:, :, c] = (
                                sub_frame[:, :, c] * (1 - sub_mask) + 
                                resized_texture[:, :, c] * sub_mask
                            )
    else:
        # Aplicar color rojo con suavizado (solo en área de esclera)
        rojo_capa = np.zeros_like(frame)
        rojo_capa[:] = (0, 0, 255)
        for c in range(0, 3):
            final_frame[:, :, c] = (
                final_frame[:, :, c] * (1 - blurred_mask_float) + 
                rojo_capa[:, :, c] * blurred_mask_float
            )

    return final_frame.astype(np.uint8)