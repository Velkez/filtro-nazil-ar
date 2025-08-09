import cv2
import os
import numpy as np

def create_comparative_image(image_path1, image_path2, output_dir="../images"):
    """
    Crea una imagen comparativa combinando dos imágenes una al lado de la otra.
    Redimensiona automáticamente las imágenes para que tengan la misma altura
    y añade títulos a cada una.
    
    Args:
        image_path1 (str): Ruta a la primera imagen (izquierda).
        image_path2 (str): Ruta a la segunda imagen (derecha).
        output_dir (str): Directorio donde se guardará la imagen combinada.
    """
    try:
        # Cargar las dos imágenes
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)

        if img1 is None:
            print(f"Error: No se pudo cargar la imagen desde {image_path1}")
            return
        if img2 is None:
            print(f"Error: No se pudo cargar la imagen desde {image_path2}")
            return
        
        # Obtener las dimensiones de las imágenes
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        
        # Redimensionar la imagen más pequeña para que coincida con la altura de la más grande
        if h1 != h2:
            new_height = max(h1, h2)
            if h1 < new_height:
                img1 = cv2.resize(img1, (int(w1 * new_height / h1), new_height))
            else:
                img2 = cv2.resize(img2, (int(w2 * new_height / h2), new_height))
        
        # Dibujar los títulos en cada imagen
        font = cv2.FONT_HERSHEY_TRIPLEX
        font_scale = 1.5
        font_thickness = 4
        text_color = (255, 255, 255) # Blanco
        stroke_color = (0, 0, 0) # Negro
        position_y = 150

        # Texto para la imagen 1 (izquierda)
        text1 = "Sin Nazil"
        text_size1 = cv2.getTextSize(text1, font, font_scale, font_thickness)[0]
        text_x1 = (img2.shape[1] - text_size1[0]) // 2
        # Dibujar el contorno negro
        cv2.putText(img2, text1, (text_x1, position_y), font, font_scale, stroke_color, font_thickness + 2, cv2.LINE_AA)
        # Dibujar el texto blanco
        cv2.putText(img2, text1, (text_x1, position_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        
        # Texto para la imagen 2 (derecha)
        text2 = "Con Nazil"
        text_size2 = cv2.getTextSize(text2, font, font_scale, font_thickness)[0]
        text_x2 = (img1.shape[1] - text_size2[0]) // 2
        # Dibujar el contorno negro
        cv2.putText(img1, text2, (text_x2, position_y), font, font_scale, stroke_color, font_thickness + 2, cv2.LINE_AA)
        # Dibujar el texto blanco
        cv2.putText(img1, text2, (text_x2, position_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
        
        # Unir las dos imágenes horizontalmente
        comparative_image = np.hstack((img1, img2))
        
        # Crear el directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar la imagen combinada con un nombre único basado en el timestamp del flujo
        flow_name = os.path.basename(os.path.dirname(image_path1))
        output_path = os.path.join(output_dir, f"comparativa_{flow_name}.png")
        cv2.imwrite(output_path, comparative_image)
        
        print(f"Imagen comparativa guardada en: {output_path}")

    except Exception as e:
        print(f"Error al crear la imagen comparativa: {e}")

if __name__ == "__main__":
    # Ejemplo de uso (esto no se ejecutará en la aplicación principal)
    # Asume que ya tienes las fotos 'con-nazil.png' y 'sin-nazil.png' en una carpeta de flujo
    # Ejemplo de ruta de flujo: '../capturas/flujo_1678886400'
    flow_dir_example = '../capturas/flujo_1678886400'
    image_con_nazil = os.path.join(flow_dir_example, 'con-nazil.png')
    image_sin_nazil = os.path.join(flow_dir_example, 'sin-nazil.png')
    
    if os.path.exists(image_con_nazil) and os.path.exists(image_sin_nazil):
        create_comparative_image(image_con_nazil, image_sin_nazil) # Orden corregido para ejemplo
    else:
        print("No se encontraron las imágenes de ejemplo para ejecutar el script.")

