import time
import signal
from datetime import datetime
from config import config
from gemini_ai import GeminiAI
from instagram_handler import InstagramHandler


class InstagramAIBot:
    """Instagram Comment Bot with Keyword Detection (ManyChat-like)"""
    
    def __init__(self):
        self.running = False
        self.instagram = InstagramHandler()
        self.ai: GeminiAI = None
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
    
    def _shutdown(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Bot to'xtatilmoqda...")
        self.running = False
    
    def start(self):
        """Start the bot"""
        print("=" * 50)
        print("🤖 Instagram Keyword Bot")
        print("   💬 Kommentariya + 📩 DM")
        print("=" * 50)
        
        # Show keywords
        print(f"\n🔑 Kalit so'zlar: {', '.join(config.get_keywords())}")
        
        # Validate configuration
        if not config.validate():
            print("\n❌ .env faylini to'g'ri to'ldiring!")
            return
        
        # Initialize AI
        print("\n🧠 Gemini AI ishga tushmoqda...")
        self.ai = GeminiAI()
        print("✅ Gemini AI tayyor!")
        
        # Login to Instagram
        print("\n📱 Instagram ga ulanmoqda...")
        if not self.instagram.login():
            print("❌ Instagram ga kirib bo'lmadi!")
            return
        
        # Start main loop
        self.running = True
        print(f"\n🚀 Bot ishga tushdi! Har 60 sekundda tekshiriladi.")
        print("   To'xtatish uchun Ctrl+C bosing.\n")
        
        self._main_loop()
    
    def _main_loop(self):
        """Main comment processing loop - 1 comment per minute"""
        while self.running:
            try:
                self._check_comments()
                
                # Wait 60 seconds before next check
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Xatolik: {e}")
                time.sleep(5)
        
        print("👋 Bot to'xtadi. Xayr!")
    
    def _check_comments(self):
        """Check and respond to ONE new comment only"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 💬 Kommentariya tekshirilmoqda...", end=" ")
        
        try:
            posts = self.instagram.get_my_recent_posts(amount=10)
            
            if not posts:
                print("Post topilmadi.")
                return
            
            for post in posts:
                new_comments = self.instagram.get_new_comments(post)
                
                if new_comments:
                    self._process_comment(post, new_comments[0])
                    return
            
            print("Yangi kommentariya yo'q.")
                
        except Exception as e:
            print(f"Xatolik: {e}")
    
    # Symbol to keyword mappings (for special characters)
    SYMBOL_MAPPINGS = {
        '+': 'plus',
        '➕': 'plus',
    }
    
    def _find_keyword(self, text: str) -> str:
        """Find which keyword is in the text, return keyword or empty string"""
        text_lower = text.lower()
        
        # First check for symbol mappings
        for symbol, keyword in self.SYMBOL_MAPPINGS.items():
            if symbol in text:
                if keyword in config.get_keywords():
                    return keyword
        
        # Then check regular keywords
        for keyword in config.get_keywords():
            if keyword.strip() in text_lower:
                return keyword
        return ""
    
    def _process_comment(self, post, comment):
        """Process a single comment - keyword or AI response"""
        username = comment.user.username
        user_id = comment.user.pk
        comment_text = comment.text or ""
        
        print(f"\n   💬 @{username}: {comment_text[:50]}...")
        
        if not comment_text:
            self.instagram.mark_comment_processed(comment.pk)
            return
        
        # Check for keywords
        matched_keyword = self._find_keyword(comment_text)
        if matched_keyword:
            self._process_keyword_comment(post, comment, username, user_id, matched_keyword)
        else:
            self._process_regular_comment(post, comment, username)
        
        self.instagram.mark_comment_processed(comment.pk)
    
    def _process_keyword_comment(self, post, comment, username, user_id, keyword: str):
        """Process keyword-triggered comment - check follow status first"""
        content_link = config.get_content_link(keyword)
        print(f"   🔑 Kalit so'z: '{keyword}' → {content_link}")
        
        # Check if user is following
        print(f"   👀 Obuna tekshirilmoqda...")
        is_following = self.instagram.is_user_following(user_id)
        
        if not is_following:
            # User is NOT following - ask them to follow first
            print(f"   ❌ Obuna emas - obuna bo'lishni so'rash")
            reply_text = f"@{username} {config.FOLLOW_FIRST_REPLY}"
            self.instagram.reply_to_comment(str(post.pk), str(comment.pk), reply_text)
            print(f"   ✅ Obuna bo'lish so'raldi!")
        else:
            # User IS following - send DM with content link
            print(f"   ✅ Obuna! DM yuborilmoqda...")
            
            # 1. Reply to comment
            reply_text = f"@{username} {config.KEYWORD_REPLY}"
            self.instagram.reply_to_comment(str(post.pk), str(comment.pk), reply_text)
            
            # 2. Send DM with keyword-specific content link
            dm_text = f"{config.DM_MESSAGE}\n\n👉 {content_link}"
            
            time.sleep(2)  # Small delay before DM
            self.instagram.send_dm_to_user(user_id, dm_text)
            print(f"   ✅ Kommentga javob + DM yuborildi!")
    
    def _process_regular_comment(self, post, comment, username):
        """Process regular comment with AI response"""
        print("   🤔 AI javob tayyorlanmoqda...")
        
        ai_response = self.ai.generate_response(
            comment.text,
            context="Instagram postidagi kommentariya. Qisqa javob bering."
        )
        
        response = f"@{username} {ai_response}"
        
        if len(response) > 2000:
            response = response[:1997] + "..."
        
        if self.instagram.reply_to_comment(str(post.pk), str(comment.pk), response):
            print(f"   ✅ AI javob yuborildi!")


def main():
    """Entry point"""
    bot = InstagramAIBot()
    bot.start()


if __name__ == "__main__":
    main()
