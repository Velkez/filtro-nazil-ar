# Filtro Nazil AR

Este proyecto es un filtro de realidad aumentada desarrollado como parte de una activación publicitaria para Nazil, una marca de gotas para los ojos.

La aplicación utiliza la cámara web para detectar los rostros de los usuarios y aplica un efecto de "ojos irritados". Luego, simula el efecto del producto mostrando los ojos sin la irritación, creando una imagen comparativa visual del antes y el después.

<div align="center">
  <video src="https://github.com/user-attachments/assets/9f9320cc-7a68-48f7-8f13-ec5b50ae7465" width="250" height="444" controls></video>
</div>

<img width="1917" height="928" alt="{E7AC86A1-61C4-475A-8074-7AE7E9D37C7C}" src="https://github.com/user-attachments/assets/f3985d63-591a-4973-8bd1-a6bf7873cce2" />


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
