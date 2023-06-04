from googletrans import Translator

def translator(text,src,dest):
    trans = Translator()
    translation = trans.translate(text,src=src,dest=dest)
    return(translation.text)
