"""
Sesli Input/Output Modülü
Metin-to-Speech ve Speech-to-Text
"""

import logging
from typing import Optional
import subprocess
import os
from io import BytesIO

logger = logging.getLogger(__name__)


class VoiceHandler:
    """Sesli giriş ve çıkış yönetimi"""
    
    def __init__(self):
        """Başlat"""
        self.tts_available = False
        self.stt_available = False
        
        # Text-to-Speech - gTTS veya espeak kullan
        try:
            import gtts
            self.gtts = gtts
            self.tts_available = True
            logger.info("Google Text-to-Speech başlatıldı")
        except:
            # Fallback: espeak sistem aracı
            try:
                result = subprocess.run(['which', 'espeak'], capture_output=True)
                if result.returncode == 0:
                    self.tts_available = True
                    logger.info("espeak Text-to-Speech hazır")
            except:
                logger.warning("TTS (gtts/espeak) bulunamadı")
        
        # Speech-to-Text
        # Speech-to-Text: do not import optional `speech_recognition` at startup
        # to avoid startup warnings in environments where it's not installed.
        self.recognizer = None
        self.stt_available = False
    
    def speak(self, text: str, language: str = "tr") -> bool:
        """
        Metni sesle konuş
        
        Args:
            text: Konuşulacak metin
            language: Dil (tr, en)
            
        Returns:
            Başarı durumu
        """
        if not self.tts_available:
            logger.warning("TTS hazır değil")
            return False

    def synthesize(self, text: str, language: str = "tr") -> Optional[bytes]:
        """
        Metni ses dosyasına çevir ve bayt olarak döndür (TTS oynatma için).
        Geri dönen mp3, Streamlit'in audio oynatıcısında play/pause/seek yapılabilir.
        """
        if not self.tts_available:
            logger.warning("TTS hazır değil")
            return None

        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang='tr' if language == 'tr' else 'en', slow=False)
            audio_file = '/tmp/speech_summary.mp3'
            tts.save(audio_file)

            with open(audio_file, 'rb') as f:
                data = f.read()

            # Temizle
            try:
                os.remove(audio_file)
            except OSError:
                pass

            logger.info("Metin TTS olarak üretildi (bayt)")
            return data
        except Exception as e:
            logger.error(f"TTS oluşturma hatası: {e}")
            return None
        
        try:
            # Çok uzun metinleri böl
            max_length = 500
            if len(text) > max_length:
                text = text[:max_length]
            
            # gtts ile dene
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='tr' if language == 'tr' else 'en', slow=False)
                audio_file = '/tmp/speech.mp3'
                tts.save(audio_file)
                
                # mpv veya ffplay ile oynat
                try:
                    subprocess.run(['mpv', '--no-video', audio_file], timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    try:
                        subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_file], timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except:
                        logger.warning("Audio player bulunamadı (mpv/ffplay)")
                        return False
                
                logger.info("Metin seslendirildi (gTTS)")
                return True
            except:
                # Fallback: espeak kullan
                lang_code = 'tr' if language == 'tr' else 'en'
                subprocess.run(['espeak', f'-v{lang_code}', text], timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info("Metin seslendirildi (espeak)")
                return True
            
        except Exception as e:
            logger.error(f"Seslendir hatası: {e}")
            return False
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """
        Mikrofonda dinle ve metne çevir
        
        Args:
            timeout: Bekleme süresi (saniye)
            
        Returns:
            Tanınan metin
        """
        if not self.stt_available or not self.recognizer:
            logger.warning("STT hazır değil")
            return None
        # STT is disabled or not configured; return None
        return None
    
    def is_available(self) -> dict:
        """Kullanılabilir özellikleri kontrol et"""
        return {
            "tts": self.tts_available,
            "stt": self.stt_available,
            "both": self.tts_available and self.stt_available
        }
