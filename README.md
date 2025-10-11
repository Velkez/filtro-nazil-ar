# Filtro Nazil AR

Este proyecto es un filtro de realidad aumentada desarrollado como parte de una activación publicitaria para Nazil, una marca de gotas para los ojos.

La aplicación utiliza la cámara web para detectar los rostros de los usuarios y aplica un efecto de "ojos irritados". Luego, simula el efecto del producto mostrando los ojos sin la irritación, creando una imagen comparativa visual del antes y el después.

https://github.com/user-attachments/assets/6141ce16-cbf2-4bb6-87f6-4bec417e9b69


## Requisitos

### Hardware
- **Cámara web:** Necesaria para la detección de rostros y la aplicación del filtro.
- **CPU decente:** El procesamiento de video en tiempo real consume bastantes recursos.
- **GPU (Recomendado):** Una tarjeta gráfica dedicada (NVIDIA o AMD) mejorará significativamente el rendimiento del filtro, ya que la detección de puntos faciales (face mesh) puede ser acelerada por hardware.

### Software
- **Python 3.10**
- **Pip** (manejador de paquetes de Python)
- **Git** (para clonar el repositorio)

## Guía de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/Velkez/filtro-nazil-ar.git
    cd filtro-nazil-ar
    ```

2.  **Crear un entorno virtual:**
    Es una buena práctica para aislar las dependencias del proyecto.
    ```bash
    python -m venv venv
    ```

3.  **Activar el entorno virtual:**
    - En Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - En macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Una vez que las dependencias estén instaladas, puedes ejecutar la aplicación principal con el siguiente comando:

```bash
python src/filtro_esclera.py
```

Esto abrirá una ventana que mostrará la imagen de la cámara. Sigue las instrucciones en pantalla para interactuar con el filtro.
