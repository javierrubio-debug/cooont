# 🤖 Bot de Evidencias de Formaciones

Bot de Telegram que recopila evidencias de formaciones y genera PPTs automáticamente.

---

## 🚀 Despliegue en Railway (gratis, 5 minutos)

### 1. Sube el código a GitHub

1. Ve a [github.com](https://github.com) → **New repository** → nombre: `formaciones-bot`
2. Sube todos estos archivos:
   - `bot.py`
   - `ppt_generator.py`
   - `generate_ppt.js`
   - `requirements.txt`
   - `package.json`
   - `Dockerfile`

### 2. Despliega en Railway

1. Ve a [railway.app](https://railway.app) e inicia sesión con GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Selecciona `formaciones-bot`
4. Railway detectará el `Dockerfile` automáticamente

### 3. Añade tu token de Telegram

En Railway, ve a tu proyecto → **Variables** → **New Variable**:

```
TELEGRAM_TOKEN = TU_TOKEN_AQUI
```

4. Click **Deploy** — ¡listo! 🎉

---

## 💬 Cómo usarlo

Una vez desplegado, añade el bot a tu grupo de Telegram y empieza a enviar evidencias:

### Formato automáticamente reconocido:
```
12/03/2026 - FABIO - SEVILLA - VDF KONECTA SEVILLA - X17 SERIES - 8 SESIONES
12/03 EUSKALTEL VALLADOLID (LUIS Y SONSOLES) 24 PAX FORMADAS X17 SERIES
```

### Comandos disponibles:
| Comando | Acción |
|---------|--------|
| `/start` | Bienvenida e instrucciones |
| `/evidencias` | Ver todas las evidencias guardadas |
| `/generar` | Generar y descargar la PPT |
| `/borrar` | Borrar todas las evidencias |
| `/ayuda` | Ver formatos de texto aceptados |

### Flujo típico:
1. El formador manda una foto con el pie de foto → ✅ Bot confirma y guarda
2. Al final del día/semana → `/generar` → 📊 PPT lista para descargar

---

## 📁 Estructura del proyecto

```
formaciones-bot/
├── bot.py              # Lógica del bot de Telegram
├── ppt_generator.py    # Puente Python → Node.js
├── generate_ppt.js     # Generación de la PPT con PptxGenJS
├── requirements.txt    # Dependencias Python
├── package.json        # Dependencias Node
└── Dockerfile          # Para despliegue en Railway/Render
```
