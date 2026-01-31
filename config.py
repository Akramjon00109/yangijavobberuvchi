import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration from environment variables"""
    
    # Instagram credentials
    INSTAGRAM_USERNAME: str = os.getenv("INSTAGRAM_USERNAME", "")
    INSTAGRAM_PASSWORD: str = os.getenv("INSTAGRAM_PASSWORD", "")
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Bot settings
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "30"))
    
    # System prompt for AI
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "Siz Instagram orqali mijozlarga yordam beruvchi yordamchisiz. "
        "Har doim o'zbek tilida, do'stona va professional tarzda javob bering. "
        "Qisqa va aniq javoblar bering."
    )
    
    # Keyword trigger settings
    KEYWORD_REPLY: str = os.getenv("KEYWORD_REPLY", "Ma'lumotni direktingizga yubordik! ✉️")
    FOLLOW_FIRST_REPLY: str = os.getenv("FOLLOW_FIRST_REPLY", "Avval sahifamizga obuna bo'ling, keyin qayta yozing!")
    DM_MESSAGE: str = os.getenv("DM_MESSAGE", "Salom! Ma'lumot uchun quyidagi linkni bosing:")
    DEFAULT_CONTENT_LINK: str = os.getenv("DEFAULT_CONTENT_LINK", "https://t.me/malumotniberuvchibot")
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL: str = os.getenv("TELEGRAM_CHANNEL", "")
    TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME", "")
    TELEGRAM_CONTENT_LINK: str = os.getenv("TELEGRAM_CONTENT_LINK", "")
    
    # Keyword-Content mappings
    CONTENT_MAPPINGS: dict = {}
    
    @classmethod
    def load_content_mappings(cls):
        """Load keyword-content mappings from CONTENT_* env vars"""
        cls.CONTENT_MAPPINGS = {}
        for key, value in os.environ.items():
            if key.startswith("CONTENT_"):
                keyword = key.replace("CONTENT_", "").lower()
                cls.CONTENT_MAPPINGS[keyword] = value
        
        if cls.CONTENT_MAPPINGS:
            print(f"📦 Kalit so'z-kontent mappinglar yuklandi: {list(cls.CONTENT_MAPPINGS.keys())}")
    
    @classmethod
    def get_content_link(cls, keyword: str) -> str:
        """Get content link for a specific keyword"""
        keyword_lower = keyword.lower().strip()
        return cls.CONTENT_MAPPINGS.get(keyword_lower, cls.DEFAULT_CONTENT_LINK)
    
    @classmethod
    def get_keywords(cls) -> list:
        """Get list of all keywords from content mappings"""
        return list(cls.CONTENT_MAPPINGS.keys())
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        errors = []
        
        if not cls.INSTAGRAM_USERNAME:
            errors.append("INSTAGRAM_USERNAME kiritilmagan")
        if not cls.INSTAGRAM_PASSWORD:
            errors.append("INSTAGRAM_PASSWORD kiritilmagan")
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY kiritilmagan")
        
        if errors:
            print("❌ Konfiguratsiya xatolari:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        # Load content mappings
        cls.load_content_mappings()
        
        # Telegram settings warning (optional)
        if not cls.TELEGRAM_BOT_TOKEN:
            print("⚠️ TELEGRAM_BOT_TOKEN kiritilmagan - TG bot ishlamaydi")
        
        return True


config = Config()
