"""
Sesli Input/Output Modülü
Metin-to-Speech ve Speech-to-Text
"""

import logging
from typing import Optional
import subprocess
import os

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
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.stt_available = True
            logger.info("Speech-to-Text başlatıldı")
        except Exception as e:
            logger.warning(f"Speech-to-Text yükleme hatası: {e}")
            self.recognizer = None
    
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
        
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                logger.info("Dinleniyor...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Google Speech Recognition kullan (ücretsiz)
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            logger.info(f"Tanınan metin: {text}")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Ses anlaşılamadı")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech Recognition hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"Dinleme hatası: {e}")
            return None
    
    def is_available(self) -> dict:
        """Kullanılabilir özellikleri kontrol et"""
        return {
            "tts": self.tts_available,
            "stt": self.stt_available,
            "both": self.tts_available and self.stt_available
        }
