import time
import google.generativeai as genai
from config import config


class GeminiAI:
    """Gemini AI integration for generating responses with retry logic"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.system_prompt = config.SYSTEM_PROMPT
        self.last_request_time = 0
        self.min_request_interval = 60  # Minimum 60 seconds between requests
    
    def generate_response(self, user_message: str, context: str = "", max_retries: int = 5) -> str:
        """
        Generate a response for the user's message with retry logic
        
        Args:
            user_message: The message from the user
            context: Optional conversation context
            max_retries: Maximum number of retry attempts
            
        Returns:
            AI-generated response in Uzbek
        """
        # Rate limiting - wait if needed
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            print(f"   ⏳ Rate limit uchun {wait_time:.0f}s kutilmoqda...")
            time.sleep(wait_time)
        
        prompt = f"""
{self.system_prompt}

{f"Kontekst: {context}" if context else ""}

Foydalanuvchi: {user_message}

Javob (qisqa va do'stona):"""

        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    return response.text.strip()
                
                return "Rahmat! Savolingizga tez orada javob beramiz."
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
                    retry_delay = (attempt + 1) * 30  # 30, 60, 90, 120, 150 seconds
                    print(f"   ⚠️ Rate limit. {retry_delay}s kutish... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ Gemini AI xatosi: {e}")
                    break
        
        # Better fallback message
        return "Rahmat! Savolingiz qabul qilindi. Tez orada javob beramiz! 🙏"


# Singleton instance
gemini_ai = GeminiAI() if config.GEMINI_API_KEY else None
