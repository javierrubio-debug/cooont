"""
Bot de Telegram para recopilar evidencias de formaciones y generar PPTs.
"""

import os
import re
import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from ppt_generator import generate_ppt

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Storage ───────────────────────────────────────────────────────────────────
DATA_FILE = Path("evidencias.json")

def load_data() -> list:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_data(data: list):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ── Parsers ───────────────────────────────────────────────────────────────────
def parse_evidencia(text: str) -> dict | None:
    """
    Intenta extraer campos de un mensaje como:
    12/03 V3 EUSKALTEL VALLADOLID (LUIS Y SONSOLES) 24 PAX FORMADAS X17 SERIES
    12/03/2026 - FABIO - SEVILLA - VDF KONECTA SEVILLA - X17 SERIES - 8 SESIONES
    """
    if not text:
        return None

    text_upper = text.upper()

    # Detectar si parece una evidencia
    keywords = ["SERIES", "PAX", "SESIONES", "FORMAD", "TRAINER", "FORMADOR"]
    if not any(k in text_upper for k in keywords):
        return None

    resultado = {
        "fecha": None,
        "formador": None,
        "cliente": None,
        "contacto": None,
        "producto": None,
        "pax": None,
        "sesiones": None,
        "texto_original": text.strip()
    }

    # Fecha
    fecha_match = re.search(r"(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)", text)
    if fecha_match:
        resultado["fecha"] = fecha_match.group(1)

    # Formador (nombre al inicio o tras guión)
    formador_match = re.search(
        r"[-–]\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]+)\s*[-–]", text
    )
    if formador_match:
        resultado["formador"] = formador_match.group(1).title()

    # PAX
    pax_match = re.search(r"(\d+)\s*PAX", text_upper)
    if pax_match:
        resultado["pax"] = pax_match.group(1)

    # Sesiones
    ses_match = re.search(r"(\d+)\s*SESIONES?", text_upper)
    if ses_match:
        resultado["sesiones"] = ses_match.group(1)

    # Producto (XNN Series)
    prod_match = re.search(r"(X\d+\s*(?:SERIES|PRO|ULTRA)?)", text_upper)
    if prod_match:
        resultado["producto"] = prod_match.group(1).title()

    # Contacto (entre paréntesis)
    contacto_match = re.search(r"\(([^)]+)\)", text)
    if contacto_match:
        resultado["contacto"] = contacto_match.group(1).title()

    # Cliente: texto entre producto/pax/sesiones y otros campos
    # Simplificado: tomar todo en mayúsculas que parezca nombre de empresa
    cliente_match = re.search(
        r"(?:SEVILLA|MADRID|BARCELONA|VALLADOLID|BILBAO|VALENCIA|GRANADA|"
        r"MÁLAGA|ZARAGOZA|MURCIA|ALICANTE|CÓRDOBA|VIGO|GIJÓN|VITORIA).*?(?=\s*[-–(]|X\d|\d+\s*PAX|\d+\s*SES|$)",
        text_upper
    )
    if cliente_match:
        resultado["cliente"] = cliente_match.group(0).strip().title()

    return resultado


# ── Handlers ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Bot de Evidencias de Formaciones*\n\n"
        "Envía mensajes con fotos de las formaciones y los recopilaré automáticamente.\n\n"
        "📋 *Comandos:*\n"
        "/evidencias — Ver todas las evidencias guardadas\n"
        "/generar — Generar PPT con todas las evidencias\n"
        "/borrar — Borrar todas las evidencias\n"
        "/ayuda — Ver formato esperado",
        parse_mode="Markdown"
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *Formato recomendado para evidencias:*\n\n"
        "`12/03/2026 - NOMBRE - CIUDAD - CLIENTE - PRODUCTO - N SESIONES`\n\n"
        "Ejemplos:\n"
        "• `12/03 V3 EUSKALTEL VALLADOLID (LUIS Y SONSOLES) 24 PAX FORMADAS X17 SERIES`\n"
        "• `12/03/2026 - FABIO - SEVILLA - VDF KONECTA SEVILLA - X17 SERIES - 8 SESIONES`\n\n"
        "Puedes enviar fotos con el texto en el pie de foto, o texto solo.",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa mensajes con o sin fotos."""
    message = update.message
    if not message:
        return

    text = message.caption or message.text or ""
    has_photo = bool(message.photo)

    parsed = parse_evidencia(text)

    if not parsed and not has_photo:
        return  # Ignorar mensajes sin relevancia

    # Descargar foto si existe
    photo_file_id = None
    if has_photo:
        photo = message.photo[-1]  # Mayor resolución
        photo_file_id = photo.file_id

    # Si no se pudo parsear el texto, guardamos lo que tenemos
    if not parsed:
        parsed = {
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "formador": None,
            "cliente": None,
            "contacto": None,
            "producto": None,
            "pax": None,
            "sesiones": None,
            "texto_original": text.strip()
        }

    parsed["photo_file_id"] = photo_file_id
    parsed["timestamp"] = datetime.now().isoformat()
    parsed["chat_id"] = message.chat_id
    parsed["message_id"] = message.message_id

    # Guardar
    data = load_data()
    data.append(parsed)
    save_data(data)

    # Confirmar al usuario
    resumen = []
    if parsed.get("fecha"):      resumen.append(f"📅 {parsed['fecha']}")
    if parsed.get("formador"):   resumen.append(f"👤 {parsed['formador']}")
    if parsed.get("cliente"):    resumen.append(f"🏢 {parsed['cliente']}")
    if parsed.get("producto"):   resumen.append(f"📱 {parsed['producto']}")
    if parsed.get("pax"):        resumen.append(f"👥 {parsed['pax']} pax")
    if parsed.get("sesiones"):   resumen.append(f"🔁 {parsed['sesiones']} sesiones")
    if has_photo:                resumen.append("📸 Foto guardada")

    total = len(data)
    msg = f"✅ *Evidencia #{total} guardada*\n\n" + "\n".join(resumen)

    keyboard = [[InlineKeyboardButton("📊 Generar PPT ahora", callback_data="generar_ppt")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)


async def ver_evidencias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("📭 No hay evidencias guardadas todavía.")
        return

    lines = [f"📋 *{len(data)} evidencias guardadas:*\n"]
    for i, e in enumerate(data, 1):
        parts = []
        if e.get("fecha"):    parts.append(e["fecha"])
        if e.get("formador"): parts.append(e["formador"])
        if e.get("cliente"):  parts.append(e["cliente"])
        foto = "📸" if e.get("photo_file_id") else "📝"
        lines.append(f"{foto} *#{i}* {' · '.join(parts) if parts else e.get('texto_original','')[:40]}")

    keyboard = [[InlineKeyboardButton("📊 Generar PPT", callback_data="generar_ppt")]]
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cmd_generar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _generar_ppt(update, context)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "generar_ppt":
        await _generar_ppt(update, context)


async def _generar_ppt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    data = load_data()

    if not data:
        await message.reply_text("📭 No hay evidencias para generar la PPT.")
        return

    wait_msg = await message.reply_text("⏳ Generando PPT, un momento...")

    # Descargar fotos
    for e in data:
        if e.get("photo_file_id") and not e.get("photo_path"):
            try:
                photo_file = await context.bot.get_file(e["photo_file_id"])
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                await photo_file.download_to_drive(tmp.name)
                e["photo_path"] = tmp.name
            except Exception as ex:
                logger.warning(f"No se pudo descargar foto: {ex}")

    # Generar PPT
    try:
        output_path = generate_ppt(data)
        await wait_msg.delete()
        with open(output_path, "rb") as f:
            fecha_str = datetime.now().strftime("%d%m%Y")
            await message.reply_document(
                document=f,
                filename=f"Formaciones_{fecha_str}.pptx",
                caption=f"📊 PPT generada con {len(data)} evidencias · {datetime.now().strftime('%d/%m/%Y')}"
            )
    except Exception as ex:
        logger.error(f"Error generando PPT: {ex}")
        await wait_msg.edit_text(f"❌ Error al generar la PPT: {ex}")


async def borrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, borrar todo", callback_data="confirm_borrar"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel_borrar"),
        ]
    ]
    await update.message.reply_text(
        "⚠️ ¿Seguro que quieres borrar todas las evidencias?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def callback_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_borrar":
        save_data([])
        await query.edit_message_text("🗑️ Todas las evidencias han sido borradas.")
    else:
        await query.edit_message_text("✅ Operación cancelada.")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("❌ Falta la variable de entorno TELEGRAM_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("evidencias", ver_evidencias))
    app.add_handler(CommandHandler("generar", cmd_generar))
    app.add_handler(CommandHandler("borrar", borrar))
    app.add_handler(CallbackQueryHandler(callback_borrar, pattern="^(confirm|cancel)_borrar$"))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    logger.info("🤖 Bot iniciado y escuchando...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
