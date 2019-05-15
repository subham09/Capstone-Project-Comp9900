from flask import Flask, render_template, request
import pyodbc
import pandas as pd
from chatterbot import ChatBot
import re, math
from collections import Counter
from operator import itemgetter
from chatterbot.trainers import ChatterBotCorpusTrainer



app = Flask(__name__)



english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(english_bot)
trainer.train("chatterbot.corpus.english")

#english_bot.set_trainer(ChatterBotCorpusTrainer)

#english_bot.train("chatterbot.corpus.english")











@app.route("/")

def home():

    return render_template("index.html")



@app.route("/get")

def get_bot_response():

    userText = request.args.get('msg')
    #print(userText)

    conn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER=.\SQLEXPRESS;'
                      'DATABASE=chatbot;'
                      'Trusted_Connection=yes;')
    #connect('DRIVER={SQL Server};'
                      #'SERVER=.\SQLEXPRESS;'
                      #'DATABASE=chatbot;'
                      #'Trusted_Connection=no;'
                      #'UID=seungbot50;PWD=seungbot50')

    sql_query = "select * from chatbot.dbo.Keywords$"
    df = pd.read_sql(sql_query,conn)

    WORD = re.compile(r'\w+')

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

    def text_to_vector(text):
        words = WORD.findall(text)
        return Counter(words)
    text1 = userText
    l = []
    vector1 = text_to_vector(text1)
    for i in range(len(df.index)):
        text2 = df.at[i,'question']
        ide = df.at[i,'id']
        vector2 = text_to_vector(text2)
        cosine = get_cosine(vector1, vector2)
        l.append((int(ide),cosine))
    maxi = max(l,key=lambda item:item[1])
    print(maxi[1])

    max_cosine_id = max(l,key=itemgetter(1))[0]
    df.set_index("id",inplace=True)
    if maxi[1] < 0.5:
        return str(english_bot.get_response(userText))
    #print(df.loc[[max_cosine_id],["answer"]].values[0][0])


    #return df.loc[[max_cosine_id],["answer"]].values[0][0]
    return df.loc[[max_cosine_id],["answer"]].values[0][0]





if __name__ == "__main__":

    app.run(port=4000)


