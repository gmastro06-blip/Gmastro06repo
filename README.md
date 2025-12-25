# TibiaBot - Pixel Bot Educativo (Inspirado en TibiaPilotNG)

**Advertencia importante**:  
Este bot es **únicamente para fines educativos** y su uso está pensado para **Open Tibia Servers (OTS)** donde esté permitido.  
El uso de bots en el Tibia oficial viola las reglas de CipSoft y puede resultar en **baneo permanente** de tu cuenta.  
Los autores no se responsabilizan por el mal uso de este software.

## Descripción
Bot pixel-based escrito en Python que automatiza tareas en Tibia mediante lectura de pantalla (sin inyección de código).  
Incluye módulos principales como Cavebot, Healing, Targeting, Refiller, Depositer y Macros.

## Estructura del proyecto

TibiaBot/
├── main.py                  # Archivo principal
├── config.json              # Configuración global
├── requirements.txt         # Dependencias
├── README.md                # Este archivo
│
├── modules/                 # Módulos del bot
│   ├── init.py
│   ├── utils.py
│   ├── healer.py
│   ├── targeting.py
│   ├── cavebot.py
│   ├── refiller.py
│   ├── depositer.py
│   └── macros.py
│
├── templates/               # Imágenes para detección (template matching)
│   └── (capturas propias del juego)
│
├── waypoints/               # Rutas predefinidas (JSON)
│   └── ejemplo_minocults.json
│
├── logs/                    # Logs automáticos (opcional)
└── screenshots/             # Capturas de debug (opcional)


## Instalación

1. Clona o descarga este proyecto.
2. Abre una terminal en la carpeta `TibiaBot/`.
3. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate    # En Linux/Mac
   venv\Scripts\activate       # En Windows

   Instala las dependencias:Bashpip install -r requirements.txtSi tienes problemas de permisos:Bashpip install --user -r requirements.txt

Configuración inicial