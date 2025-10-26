"""
ElevenLabs Text-to-Speech Service
Provides voiceover functionality for accessibility
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsService:
    """Service for converting text to speech using ElevenLabs API"""
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Default: Rachel
        self.base_url = 'https://api.elevenlabs.io/v1'
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            print("✅ ElevenLabs TTS service initialized")
        else:
            print("⚠️ ELEVENLABS_API_KEY not found. Voice features will be disabled.")
    
    def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: The text to convert to speech
            voice_id: Optional custom voice ID (uses default if not provided)
            
        Returns:
            Audio data as bytes, or None if service is disabled or error occurs
        """
        if not self.enabled:
            return None
        
        if not text or not text.strip():
            return None
        
        voice = voice_id or self.voice_id
        url = f"{self.base_url}/text-to-speech/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling ElevenLabs API: {e}")
            return None
    
    def get_voices(self):
        """Get available voices from ElevenLabs"""
        if not self.enabled:
            return []
        
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('voices', [])
            return []
        except Exception as e:
            print(f"❌ Error fetching voices: {e}")
            return []

# Create global instance
elevenlabs_service = ElevenLabsService()