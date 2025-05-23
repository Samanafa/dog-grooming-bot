
import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from datetime import datetime
import json

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

(
    STORE, GROOMER, NAME, BREED, AGE,
    CHECKIN_TESTA, CHECKIN_ZAMPE, CHECKIN_TRONCO, CHECKIN_CODA,
    CHECKOUT_TESTA, CHECKOUT_ZAMPE, CHECKOUT_TRONCO, CHECKOUT_CODA
) = range(13)

user_data = {}
store_keyboard = [["PC1", "BS1"]]
groomer_keyboard = [["Davide Raffi", "Valentina Peveri"],
                    ["Manar Orabi", "Stefani Petrova"],
                    ["Asia Aronica"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data.clear()
    await update.message.reply_text("🏪 In che negozio stai lavorando?",
                                    reply_markup=ReplyKeyboardMarkup(store_keyboard, one_time_keyboard=True))
    return STORE

async def get_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["store"] = update.message.text
    await update.message.reply_text("👤 Chi sei?",
                                    reply_markup=ReplyKeyboardMarkup(groomer_keyboard, one_time_keyboard=True))
    return GROOMER

async def get_groomer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["groomer"] = update.message.text
    await update.message.reply_text("🐶 Come si chiama il cane?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["dog_name"] = update.message.text
    await update.message.reply_text("🔤 Che razza è?")
    return BREED

async def get_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["breed"] = update.message.text
    await update.message.reply_text("📅 Quanti anni ha?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["age"] = update.message.text
    await update.message.reply_text("📷 Carica la foto di CHECK-IN - TESTA")
    return CHECKIN_TESTA

async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, next_state: int):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    os.makedirs("photos", exist_ok=True)
    filename = f"{user_data['dog_name']}_{key}.jpg".replace(" ", "_")
    await file.download_to_drive(os.path.join("photos", filename))
    user_data[key] = f"photos/{filename}"
    return next_state

async def get_checkin_testa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-IN - ZAMPE")
    return await save_photo(update, context, "checkin_testa", CHECKIN_ZAMPE)

async def get_checkin_zampe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-IN - TRONCO")
    return await save_photo(update, context, "checkin_zampe", CHECKIN_TRONCO)

async def get_checkin_tronco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-IN - CODA")
    return await save_photo(update, context, "checkin_tronco", CHECKIN_CODA)

async def get_checkin_coda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-OUT - TESTA")
    return await save_photo(update, context, "checkin_coda", CHECKOUT_TESTA)

async def get_checkout_testa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-OUT - ZAMPE")
    return await save_photo(update, context, "checkout_testa", CHECKOUT_ZAMPE)

async def get_checkout_zampe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-OUT - TRONCO")
    return await save_photo(update, context, "checkout_zampe", CHECKOUT_TRONCO)

async def get_checkout_tronco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📷 CHECK-OUT - CODA")
    return await save_photo(update, context, "checkout_tronco", CHECKOUT_CODA)

async def get_checkout_coda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_photo(update, context, "checkout_coda", ConversationHandler.END)
    dati = {
        "data": datetime.now().isoformat(),
        "negozio": user_data.get("store"),
        "operatore": user_data.get("groomer"),
        "nome_cane": user_data.get("dog_name"),
        "razza": user_data.get("breed"),
        "eta": user_data.get("age"),
        "check_in": {
            "testa": user_data.get("checkin_testa"),
            "zampe": user_data.get("checkin_zampe"),
            "tronco": user_data.get("checkin_tronco"),
            "coda": user_data.get("checkin_coda")
        },
        "check_out": {
            "testa": user_data.get("checkout_testa"),
            "zampe": user_data.get("checkout_zampe"),
            "tronco": user_data.get("checkout_tronco"),
            "coda": user_data.get("checkout_coda")
        }
    }
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            contenuto = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        contenuto = []
    contenuto.append(dati)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(contenuto, f, ensure_ascii=False, indent=4)
    await update.message.reply_text("💾 Dati salvati in 'data.json' ✅\nGrazie per il tuo lavoro! 🐶")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operazione annullata.")
    return ConversationHandler.END

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_store)],
            GROOMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_groomer)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_breed)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            CHECKIN_TESTA: [MessageHandler(filters.PHOTO, get_checkin_testa)],
            CHECKIN_ZAMPE: [MessageHandler(filters.PHOTO, get_checkin_zampe)],
            CHECKIN_TRONCO: [MessageHandler(filters.PHOTO, get_checkin_tronco)],
            CHECKIN_CODA: [MessageHandler(filters.PHOTO, get_checkin_coda)],
            CHECKOUT_TESTA: [MessageHandler(filters.PHOTO, get_checkout_testa)],
            CHECKOUT_ZAMPE: [MessageHandler(filters.PHOTO, get_checkout_zampe)],
            CHECKOUT_TRONCO: [MessageHandler(filters.PHOTO, get_checkout_tronco)],
            CHECKOUT_CODA: [MessageHandler(filters.PHOTO, get_checkout_coda)],
        },
        fallbacks=[CommandHandler("fine", cancel)]
    )
    app.add_handler(conv)
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
