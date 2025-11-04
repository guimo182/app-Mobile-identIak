# IDENTIKAI (Demo)

https://www.figma.com/proto/7QvFD7JcIUKNBiO3vWLGbv/One-Credit-Card-App-UI--Community-?node-id=1-2&t=EckDgyqdzaWobnaT-1&starting-point-node-id=1%3A2

Aplicativo web *responsivo* (Flask + HTML/CSS/JS) que simula un flujo de **registro/validación facial** para marcar asistencia.  
No realiza reconocimiento biométrico real; guarda una captura y registra la asistencia en SQLite.

## Estructura
```
identikai-app/
├─ app.py
├─ requirements.txt
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ login.html
│  ├─ signup.html
│  ├─ face.html
│  └─ success.html
├─ static/
│  ├─ css/styles.css
│  ├─ js/face.js
│  └─ img/logo.svg
└─ uploads/               # capturas guardadas
```

## Instalación (entorno virtual)
```bash
# 1) Crear y activar entorno
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Ejecutar (desarrollo)
python app.py  # o FLASK_APP=app.py flask run

# 4) Abrir en el navegador
http://127.0.0.1:5000
```

## Flujo
1. **Inicio** (`/`): landing con CTA “Probar en móvil”.
2. **Login** (`/login`) o **Registro** (`/signup`).
3. **Registro facial** (`/face`): acceso a cámara del navegador, marco guía y botón “Registrar asistencia”.
4. **Éxito** (`/success`).  
Las capturas se guardan en `uploads/` y se registra un evento en `identikai.db` (tabla `attendance`).

> Para un reconocimiento real, conecta `/api/verify` con un servicio de verificación facial (por ejemplo, un modelo ONNX/TensorFlow, o un proveedor externo) y almacena una plantilla biométrica cumpliendo normatividad de datos personales.
