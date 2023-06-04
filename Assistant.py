import pickle
import random
import json
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
import translationModule as tm
import requests
from datetime import datetime
from google.transliteration import transliterate_text

import speech_recognition
import speechsynthesis as ss

recognizer = speech_recognition.Recognizer()
user_lang='en'

def languageSelection():
    global user_lang
    try:
        with speech_recognition.Microphone() as source:
            ss.synthesize("Choose a language",user_lang)
            print("listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print("User Input : ",text)
            if(text=='English'):
                user_lang='en'
            elif(text=='Hindi'):
                user_lang='hi'
            elif(text=='Malayalam'):
                user_lang='ml'
            elif(text=='Tamil'):
                user_lang='ta'

            if(user_lang=='hi'):
                ss.synthesize("Selected Language - hindi",user_lang)
            elif(user_lang=='ml'):
                ss.synthesize("Selected Language - Malayalam",user_lang)
            elif(user_lang=='ta'):
                ss.synthesize("Selected Language - Tamil",user_lang)
            elif(user_lang=='en'):
                ss.synthesize('Selected Language - English',user_lang)
            
            ss.synthesize("Call me Dexter to activate me",user_lang)
            return user_lang
            
    except:
        ss.synthesize('please try again',user_lang)

with open("intents.json") as file:
    data = json.load(file)

    model = keras.models.load_model('chat_model')

    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    with open('label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)


def LiveStatus():
    try:
        with speech_recognition.Microphone() as source:

            ss.synthesize("Please tell me the train number",user_lang)
            print("listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
            trainno = recognizer.recognize_google(audio)
            print("User Input :"+trainno)
            ss.synthesize("Please tell me the number of days it has been since the train started",user_lang)
            print("listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
            startday = recognizer.recognize_google(audio)
            print("User Input :"+startday)

            url = "https://irctc1.p.rapidapi.com/api/v1/liveTrainStatus"

            querystring = {"trainNo":trainno,"startDay":startday
                        
                        }

            headers = {
                "X-RapidAPI-Key": "04e5a6cacamsh77eb2b74c7b64c3p12f470jsn346ace63076b",
                "X-RapidAPI-Host": "irctc1.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers, params=querystring).json()

            trainname = response['data']['train_name']
            stationname = []
            distance_to_next_station = []
            time_to_station = []
            for i in range(3):
                stationname.append(
                    response['data']['upcoming_stations'][i]['station_name'])
                distance_to_next_station.append(
                    response['data']['upcoming_stations'][i]['distance_from_current_station_txt'])
                time_to_station.append(response['data']['upcoming_stations'][i]['eta'])
            
            for i in range(3):
                print("Train "+trainname+ " will be arriving at "+stationname[i]+" station on "+time_to_station[i]+". "+distance_to_next_station[i])
                ss.synthesize("Train "+trainname+ " will be arriving at "+stationname[i]+" station on "+time_to_station[i]+". "+distance_to_next_station[i],user_lang)
            
    except:
        ss.synthesize("something went wrong. please try again")
        

def chat():

    max_len = 20
    
    global user_lang

    try:
        while True:
            with speech_recognition.Microphone() as source:
                print('listening....')
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                print("User Input :"+text)
                if ("Dexter" in text):
                    ss.synthesize("Hi I am Dexter How may I help you today?",user_lang)
                    while ("exit" not in text):
                        print('listening....')
                        recognizer.adjust_for_ambient_noise(
                            source, duration=0.5)
                        audio = recognizer.listen(source)
                        text = recognizer.recognize_google(audio)
                        print("User Input :"+text)
                        if text != 'exit':

                            if(user_lang!='en'):
                                text=transliterate_text(text,lang_code=user_lang)
                                print('transliterated text :'+text)
                                text = tm.translator(text,user_lang,"en")
                                print(text)


                            result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
                                                                                            truncating='post', maxlen=max_len))
                            tag = lbl_encoder.inverse_transform(
                                [np.argmax(result)])

                            if tag == "TrainLiveStatus":
                                LiveStatus()        

                            elif tag=="Date":
                                today = datetime.now().strftime("%A%d/%m/%Y")
                                ss.synthesize(today,user_lang)
            
                            elif tag=="Time":
                                now =  datetime.now().strftime("%I:%M:%p")
                                ss.synthesize(now,user_lang)

                            elif tag=="Language":
                                user_lang = languageSelection()    
                            else:
                                for i in data['intents']:
                                    if i['tag'] == tag:
                                        resp = np.random.choice(i['responses'])
                                        print(resp)
                                        ss.synthesize(resp,user_lang)

                        else:
                            ss.synthesize("Have a good day",user_lang)

                    break
                else:
                    ss.synthesize('Please call me Dexter',user_lang)
    except:
        ss.synthesize("Sorry I Couldnt Hear that. Please Call me Dexter again",user_lang)
        chat()

user_lang = languageSelection()
chat()
