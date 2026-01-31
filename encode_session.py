"""
Script to encode session.json to base64 for Render environment variable
Run: python encode_session.py
Then copy the output to Render > Environment > SESSION_DATA
"""
import base64
import json
import os

SESSION_FILE = "session.json"

def encode_session():
    if not os.path.exists(SESSION_FILE):
        print(f"❌ {SESSION_FILE} topilmadi!")
        print("   Avval lokal kompyuterda botni ishga tushiring va login qiling.")
        return
    
    try:
        with open(SESSION_FILE, 'r') as f:
            session_data = f.read()
        
        # Encode to base64
        encoded = base64.b64encode(session_data.encode('utf-8')).decode('utf-8')
        
        print("=" * 50)
        print("✅ Session kodlandi!")
        print("=" * 50)
        print("\n📋 Quyidagi qiymatni Render > Environment > SESSION_DATA ga qo'shing:\n")
        print(encoded)
        print("\n" + "=" * 50)
        print(f"📊 Uzunlik: {len(encoded)} belgi")
        print("=" * 50)
        
        # Also save to file
        with open("session_encoded.txt", 'w') as f:
            f.write(encoded)
        print(f"\n💾 session_encoded.txt ga ham saqlandi")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    encode_session()
