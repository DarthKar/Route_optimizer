# 🗺️ Route Optimizer

Route Optimizer es una aplicación desarrollada en **Python** que permite optimizar rutas geográficas de manera sencilla e interactiva mediante una interfaz construida con **Streamlit**.  
Ideal para planificar entregas, recorridos o rutas de transporte en función de coordenadas y distancias.

---

## 🚀 Características principales

- Interfaz web intuitiva con **Streamlit**  
- Cálculo automático de rutas óptimas  
- Visualización de coordenadas en mapa  
- Soporte para múltiples puntos de inicio y destino  
- Compatible con cualquier sistema operativo (Windows, macOS, Linux)

---

## 🧰 Requisitos previos

Para ejecutar la aplicacion son necesarios los siguientes paquetes:
- **Python 3.9+**  
- **pip** (administrador de paquetes de Python)

#### 🪟 Windows
```bash
# 1. Clonar el repositorio
git clone https://github.com/DarthKar/Route_optimizer.git
cd Route_optimizer

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt
```
#### 🍎 macOS
```bash
# 1. Clonar el repositorio
git clone https://github.com/DarthKar/Route_optimizer.git
cd Route_optimizer

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar entorno virtual
source venv/bin/activate

# 4. Instalar dependencias
pip3 install -r requirements.txt
```
#### 🐧 Linux (Ubuntu/Debian)
```bash
# 1. Instalar Python y pip si no están instalados
sudo apt update
sudo apt install python3 python3-venv python3-pip -y

# 2. Clonar el repositorio
git clone https://github.com/DarthKar/Route_optimizer.git
cd Route_optimizer

# 3. Crear entorno virtual
python3 -m venv venv

# 4. Activar entorno virtual
source venv/bin/activate

# 5. Instalar dependencias
pip install -r requirements.txt
```
Finalmente ejecute el archivo main.py y corra el siguiente comando:
```bash
streamlit run main.py
```
