import json
import os
from pathlib import Path
from typing import Optional, List
from instagrapi import Client
from instagrapi.types import DirectThread, DirectMessage, Media, Comment
from config import config

# Try to import database module
try:
    from database import db
    HAS_DB = db.enabled
except:
    HAS_DB = False
    db = None


class InstagramHandler:
    """Instagram DM and Comment handler using instagrapi"""
    
    SESSION_FILE = "session.json"
    PROCESSED_FILE = "processed_comments.json"
    
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [1, 3]  # Random delay between actions
        self.logged_in = False
        self.processed_messages: set = set()  # Track processed message IDs
        self.processed_comments: set = set()  # Track processed comment IDs
        self._load_processed_comments()
    
    def _load_processed_comments(self):
        """Load processed comments from database or file"""
        # Try database first
        if HAS_DB and db:
            self.processed_comments = db.get_processed_comments()
            if self.processed_comments:
                print(f"📥 {len(self.processed_comments)} ta processed comment DBdan yuklandi")
                return
        
        # Fallback to file
        if os.path.exists(self.PROCESSED_FILE):
            try:
                with open(self.PROCESSED_FILE, 'r') as f:
                    self.processed_comments = set(json.load(f))
            except:
                self.processed_comments = set()
    
    def _save_processed_comments(self):
        """Save processed comments to file"""
        try:
            with open(self.PROCESSED_FILE, 'w') as f:
                json.dump(list(self.processed_comments), f)
        except Exception as e:
            print(f"⚠️ Kommentariyalar saqlanmadi: {e}")
    
    def login(self) -> bool:
        """
        Login to Instagram, using saved session if available
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Try to load session from database first
            if HAS_DB and db:
                db_session = db.load_session()
                if db_session:
                    print("📱 Session databazadan yuklanmoqda...")
                    try:
                        self.client.set_settings(db_session)
                        self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
                        self.logged_in = True
                        print("✅ Session databazadan muvaffaqiyatli yuklandi!")
                        return True
                    except Exception as e:
                        print(f"⚠️ DB sessiya yaroqsiz: {e}")
            
            # Try to load existing session from file
            if os.path.exists(self.SESSION_FILE):
                print("📱 Saqlangan sessiya topildi, yuklanmoqda...")
                try:
                    self.client.load_settings(self.SESSION_FILE)
                    self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
                    self.logged_in = True
                    print("✅ Sessiya muvaffaqiyatli yuklandi!")
                    # Save to DB for cloud use
                    self._save_session_to_db()
                    return True
                except Exception as e:
                    print(f"⚠️ Sessiya yaroqsiz, qaytadan kirish... ({e})")
                    os.remove(self.SESSION_FILE)
            
            # Fresh login
            print("🔐 Instagram ga kirish...")
            self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
            
            # Save session for future use
            self.client.dump_settings(self.SESSION_FILE)
            self._save_session_to_db()
            print("✅ Muvaffaqiyatli kirildi va sessiya saqlandi!")
            
            self.logged_in = True
            return True
            
        except Exception as e:
            print(f"❌ Instagram ga kirishda xatolik: {e}")
            self.logged_in = False
            return False
    
    def _save_session_to_db(self):
        """Save current session to database"""
        if HAS_DB and db:
            try:
                settings = self.client.get_settings()
                db.save_session(settings)
            except Exception as e:
                print(f"⚠️ Session DBga saqlanmadi: {e}")
    
    # ==================== DM Functions ====================
    
    def get_unread_threads(self) -> list[DirectThread]:
        """Get threads with unread messages"""
        if not self.logged_in:
            print("❌ Avval login qiling!")
            return []
        
        try:
            threads = self.client.direct_threads(amount=20)
            unread_threads = []
            
            for thread in threads:
                if thread.messages:
                    latest_message = thread.messages[0]
                    if (latest_message.user_id != self.client.user_id and 
                        str(latest_message.id) not in self.processed_messages):
                        unread_threads.append(thread)
            
            return unread_threads
            
        except Exception as e:
            print(f"❌ Xabarlarni olishda xatolik: {e}")
            return []
    
    def get_latest_message(self, thread: DirectThread) -> Optional[DirectMessage]:
        """Get the latest unprocessed message from a thread"""
        if thread.messages:
            message = thread.messages[0]
            if message.user_id != self.client.user_id:
                return message
        return None
    
    def send_message(self, thread_id: str, text: str) -> bool:
        """Send a message to a thread"""
        if not self.logged_in:
            print("❌ Avval login qiling!")
            return False
        
        try:
            self.client.direct_send(text, thread_ids=[thread_id])
            print(f"📤 Xabar yuborildi: {text[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Xabar yuborishda xatolik: {e}")
            return False
    
    def mark_as_processed(self, message_id: str):
        """Mark a message as processed"""
        self.processed_messages.add(str(message_id))
    
    def send_dm_to_user(self, user_id: int, text: str) -> bool:
        """
        Send a direct message to a user by their user ID
        
        Args:
            user_id: The user's Instagram ID
            text: The message text
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.logged_in:
            print("❌ Avval login qiling!")
            return False
        
        try:
            self.client.direct_send(text, user_ids=[user_id])
            print(f"📩 DM yuborildi (user_id: {user_id}): {text[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ DM yuborishda xatolik: {e}")
            return False
    
    # ==================== Comment Functions ====================
    
    def get_my_recent_posts(self, amount: int = 10) -> List[Media]:
        """
        Get my recent posts
        
        Args:
            amount: Number of posts to fetch
            
        Returns:
            List of Media objects
        """
        if not self.logged_in:
            print("❌ Avval login qiling!")
            return []
        
        try:
            user_id = self.client.user_id
            medias = self.client.user_medias(user_id, amount=amount)
            return medias
        except Exception as e:
            print(f"❌ Postlarni olishda xatolik: {e}")
            return []
    
    def get_new_comments(self, media: Media) -> List[Comment]:
        """
        Get new (unprocessed) comments for a post, sorted by time (newest first)
        
        Args:
            media: The Media object
            
        Returns:
            List of new Comment objects, newest first
        """
        if not self.logged_in:
            return []
        
        try:
            comments = self.client.media_comments(media.id, amount=30)
            new_comments = []
            
            for comment in comments:
                comment_id = str(comment.pk)
                # Skip own comments and already processed
                if (str(comment.user.pk) != str(self.client.user_id) and 
                    comment_id not in self.processed_comments):
                    new_comments.append(comment)
            
            # Sort by pk (higher pk = newer comment)
            new_comments.sort(key=lambda c: int(c.pk), reverse=True)
            
            return new_comments
            
        except Exception as e:
            print(f"❌ Kommentariyalarni olishda xatolik: {e}")
            return []
    
    def reply_to_comment(self, media_id: str, comment_id: str, text: str) -> bool:
        """
        Reply to a comment
        
        Args:
            media_id: The media ID
            comment_id: The comment ID to reply to
            text: Reply text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.logged_in:
            print("❌ Avval login qiling!")
            return False
        
        try:
            self.client.media_comment(media_id, text, replied_to_comment_id=comment_id)
            print(f"💬 Kommentariyaga javob yuborildi: {text[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Kommentariyaga javob berishda xatolik: {e}")
            return False
    
    def mark_comment_processed(self, comment_id: str):
        """Mark a comment as processed and save to database/file"""
        self.processed_comments.add(str(comment_id))
        
        # Save to database
        if HAS_DB and db:
            db.mark_comment_processed(str(comment_id))
        
        # Also save to file as backup
        self._save_processed_comments()
    
    def get_user_info(self, user_id: int) -> str:
        """Get username by user ID"""
        try:
            user = self.client.user_info(user_id)
            return user.username
        except:
            return f"user_{user_id}"
    
    def is_user_following(self, user_id: int) -> bool:
        """
        Check if a user is following our account
        
        Args:
            user_id: The user's Instagram ID
            
        Returns:
            True if following, False otherwise
        """
        if not self.logged_in:
            return False
        
        try:
            # Use friendship API to check relationship
            friendship = self.client.user_friendship_v1(user_id)
            is_following = friendship.followed_by
            print(f"   📊 Obuna holati: {'✅ Obuna' if is_following else '❌ Obuna emas'}")
            return is_following
        except Exception as e:
            print(f"⚠️ Obunani tekshirishda xatolik: {e}")
            # If we can't check, assume they're following to avoid blocking
            return True


# Singleton instance
instagram_handler = InstagramHandler()
