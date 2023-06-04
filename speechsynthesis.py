from gtts import gTTS
import translationModule as em
from playsound import playsound
import os

def synthesize(text,user_lang):
    
    translatedtxt = em.translator(text,src="en",dest=user_lang)
    language = user_lang
    print(translatedtxt)
    audio = gTTS(text=translatedtxt, lang=language, slow=False,tld='co.in' )
    
    audio.save("response.mp3")
    playsound("response.mp3")
    os.remove("response.mp3")
