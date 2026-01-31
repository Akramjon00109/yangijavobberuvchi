"""
Telegram Bot for subscription verification
Run separately: python telegram_bot.py
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config


class TelegramSubscriptionBot:
    """Telegram bot for checking channel subscription and providing content"""
    
    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.channel = config.TELEGRAM_CHANNEL
        self.content_link = config.TELEGRAM_CONTENT_LINK
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Check subscription
        is_subscribed = await self._check_subscription(update, context, user.id)
        
        if is_subscribed:
            await self._send_content(update)
        else:
            await self._ask_subscription(update)
    
    async def _check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
        """Check if user is subscribed to the channel"""
        try:
            member = await context.bot.get_chat_member(chat_id=self.channel, user_id=user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            print(f"Obunani tekshirishda xatolik: {e}")
            return False
    
    async def _ask_subscription(self, update: Update):
        """Ask user to subscribe first"""
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga qo'shilish", url=f"https://t.me/{self.channel.replace('@', '')}")],
            [InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Salom! 👋\n\n"
            f"Ma'lumotlarni olish uchun avval kanalimizga obuna bo'ling:\n"
            f"👉 {self.channel}\n\n"
            f"Obuna bo'lgandan keyin \"✅ Obuna bo'ldim\" tugmasini bosing.",
            reply_markup=reply_markup
        )
    
    async def _send_content(self, update: Update):
        """Send content link to subscribed user"""
        message = update.message or update.callback_query.message
        
        keyboard = [
            [InlineKeyboardButton("🎁 Kontentni olish", url=self.content_link)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "✅ Rahmat, siz kanalimizga obuna bo'lgansiz!\n\n"
            "🎁 Mana sizning kontentingiz:\n"
            f"👉 {self.content_link}\n\n"
            "Qo'shimcha savollar bo'lsa, yozing!"
        )
        
        if update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.reply_text(text, reply_markup=reply_markup)
    
    async def check_subscription_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle subscription check button"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        is_subscribed = await self._check_subscription(update, context, user_id)
        
        if is_subscribed:
            await self._send_content(update)
        else:
            await query.answer("❌ Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)
    
    def run(self):
        """Run the bot"""
        if not self.token or self.token == "your_telegram_bot_token":
            print("❌ TELEGRAM_BOT_TOKEN .env faylida kiritilmagan!")
            return
        
        print("=" * 50)
        print("🤖 Telegram Subscription Bot")
        print(f"   📢 Kanal: {self.channel}")
        print("=" * 50)
        print("\n🚀 Bot ishga tushdi. To'xtatish uchun Ctrl+C")
        
        app = Application.builder().token(self.token).build()
        
        # Handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CallbackQueryHandler(self.check_subscription_callback, pattern="check_subscription"))
        
        # Run
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    bot = TelegramSubscriptionBot()
    bot.run()


if __name__ == "__main__":
    main()
