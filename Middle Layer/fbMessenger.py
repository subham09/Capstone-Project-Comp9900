from flask import Flask, render_template, request
import pyodbc
import pandas as pd
from chatterbot import ChatBot
import re, math
from collections import Counter
from operator import itemgetter
from chatterbot.trainers import ChatterBotCorpusTrainer
#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import requests
import speech_recognition as sr
#from converter import Converter
import urllib
#import speech_recognition as sr
import subprocess
import os

app = Flask(__name__)
ACCESS_TOKEN = 'EAAFZBnUq24o4BAPN3zSBMi32hIg1jT7velgVXwW26ggZAENUlWRtSRmRSNRwXwa95tOW7u3ZCnxkTN7WtwSn7O7oSMP1WgQC436SgvPriQBJaZBDekyZBRZCMpmeduxnFllzbRJcZA3SNkZB3zLzF43sTdqJthUcAo2vVDlg6Xzqsr2wAbva5mQE'
VERIFY_TOKEN = 'subham'
bot = Bot(ACCESS_TOKEN)

##english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
##trainer = ChatterBotCorpusTrainer(english_bot)
##trainer.train("chatterbot.corpus.english")

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    #print(message['message'])
                    response_sent_text = get_message(message['message'].get('text'))
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    print(message['message'].get('attachments')[0]['payload']['url'])
                    response_sent_nontext = get_message_audio(message['message'].get('attachments')[0]['payload']['url'])
                    print(response_sent_nontext)
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def get_cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

def text_to_vector(WORD, text):
        words = WORD.findall(text)
        return Counter(words)


#chooses a random message to send to the user
def get_message_audio(audio):
    url = audio
    mp4file = urllib.request.urlopen(url)

    with open("test.mp4", "wb") as handle:
        handle.write(mp4file.read())

    cmdline = ['avconv',
           '-i',
           'test.mp4',
           '-vn',
           '-f',
           'wav',
           'test.wav']
    subprocess.call(cmdline)

    r = sr.Recognizer()
    with sr.AudioFile('test.wav') as source:
        audio = r.record(source)

    command = r.recognize_google(audio)
    print (command)
    
    os.remove("test.mp4")
    os.remove("test.wav")
    return get_message(command)

def get_message(userText):
    conn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER=.\SQLEXPRESS;'
                      'DATABASE=chatbot;'
                      'Trusted_Connection=yes;')
    sql_query = "select * from chatbot.dbo.Keywords$"
    df = pd.read_sql(sql_query,conn)
    WORD = re.compile(r'\w+')

    text1 = userText
    l = []
    vector1 = text_to_vector(WORD,text1)
    for i in range(len(df.index)):
        text2 = df.at[i,'question']
        ide = df.at[i,'id']
        vector2 = text_to_vector(WORD,text2)
        cosine = get_cosine(vector1, vector2)
        l.append((int(ide),cosine))
    maxi = max(l,key=lambda item:item[1])[1]
    #print(maxi)
    max_cosine_id = max(l,key=itemgetter(1))[0]
    df.set_index("id",inplace=True)
##    if maxi > .4:
##        return_ans = df.loc[[max_cosine_id],["answer"]].values[0][0]
##    else:
##        return_ans = str(english_bot.get_response(userText))
##    print("cosine", max(l,key=lambda item:item[1]))
    # return selected item to the user
    return df.loc[[max_cosine_id],["answer"]].values[0][0]

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
