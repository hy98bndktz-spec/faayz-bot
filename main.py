import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logger.error("❌ لم يتم العثور على التوكن في البيئة.")
    raise SystemExit("أضف TELEGRAM_BOT_TOKEN في إعدادات Render.")

PAIRS = ["BTC/USD", "ETH/USD", "EUR/USD"]

async def fetch_price(session, pair):
    base, quote = pair.split("/")
    base_map = {"BTC": "bitcoin", "ETH": "ethereum"}
    if base.upper() in base_map:
        cg_id = base_map[base.upper()]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies={quote.lower()}"
        async with session.get(url) as resp:
            data = await resp.json()
            return data.get(cg_id, {}).get(quote.lower())
    return None

def analyze(price):
    if not price:
        return "⚠️ لا توجد بيانات"
    price = float(price)
    if price > 1000:
        return "📈 صاعد بقوة"
    elif price > 1:
        return "📈 صاعد"
    else:
        return "📉 منخفض"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 أهلاً! أرسل /analyze لتحليل العملات.")

async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري تحليل الأسعار...")
    async with aiohttp.ClientSession() as session:
        results = []
        for pair in PAIRS:
            price = await fetch_price(session, pair)
            results.append(f"🔹 {pair}\n💰 {price}\n📊 {analyze(price)}")
        await update.message.reply_text("\n\n".join(results))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze_cmd))
    logger.info("🚀 البوت يعمل الآن!")
    app.run_polling()
