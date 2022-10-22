#from crypt import methods
#import json
from json import encoder
import re
#from tkinter import SW
import pandas as pd
from flask import Flask, request, jsonify
from flasgger import LazyJSONEncoder, swag_from, LazyString, Swagger
import gradio as gr
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, StopWordRemoverFactory, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import csv
from database import insertTextFile, insertTextString, checkTableFile, checkTableText
from unidecode import unidecode

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

kamus = pd.read_csv("new_kamusalay.csv", names=["sebelum","sesudah"], encoding="latin-1")

swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API TESTER'),
        'version': LazyString(lambda: '1'),
        'description': LazyString(lambda: 'API Tester for challenge')
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers":[],
    "specs": [
        {
            "endpoint":"docs",
            "route":"/docs.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True
        }
    ],
    "static_url_path":"/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,config=swagger_config)
factory = StopWordRemoverFactory()
stopwords = factory.get_stop_words()
with open('stopword.csv', newline='') as csvfile:
    data_stopword_id = list(csv.reader(csvfile))

#data_stopword_id
stopword_more = [item for sublist in data_stopword_id for item in sublist]
data_stopwords = stopwords + stopword_more
dictionary = ArrayDictionary(data_stopwords)
stopword = StopWordRemover(dictionary)

def _stopword_removal(content):
  text_add_space = re.sub(r" ","  ",str(content))
  tweet_remove = stopword.remove(text_add_space)
  text_remove_space = re.sub(r"  "," ",str(tweet_remove))
  tweet_clear = text_remove_space.strip()
  return tweet_clear

def lowerCase(i): return i.lower()

 
def text_proccesing(tweet):
    tweet = re.sub(r"rt", "", tweet)
    tweet = re.sub(r"user", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r"www.\S+", "", tweet)
    tweet = re.sub("@[A-Za-z0-9_]+","", tweet)
    tweet = re.sub("#[A-Za-z0-9_]+","", tweet)
    tweet = re.sub(r'[^\x00-\x7f]',r'', tweet)
    tweet = re.sub(r"[^\w\d\s]+", "", tweet)
    # tweet = re.sub(r'[^A-Za-z0-9]', "", tweet)
    # tweet = re.sub(r"x[A-Za-z0-9./]+", "", tweet)
    tweet = re.sub(' +', ' ', tweet)
    #tweet = tweet.strip()
    return tweet

def file_processing(tweet):
    tweet = re.sub(r"rt", "", tweet)
    tweet = re.sub(r"user", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r"www.\S+", "", tweet)
    tweet = re.sub("@[A-Za-z0-9_]+","", tweet)
    tweet = re.sub("#[A-Za-z0-9_]+","", tweet)
    tweet = re.sub(r'[^\x00-\x7f]',r'', tweet)
    tweet = re.sub(r"[^\w\d\s]+", "", tweet)
    tweet = re.sub(r"\\x[A-Za-z0-9./]+", "", unidecode(tweet))
    return tweet

def normalize(tweet):
    words=tweet.split()
    clearwords=""
    for i in words:
        x=0
        for idx, data in enumerate(kamus["sebelum"]):
            if (i == data):
                clearwords += kamus["sesudah"][idx]+" "
                print ("normalisasi:", data,"=",kamus["sesudah"][idx])
                x=1
                break
        if(x==0):
            clearwords += i + " "
    return clearwords

def dataCleansing(tweet):
    a=tweet
    tweet=lowerCase(tweet)
    tweet=text_proccesing(tweet)
    tweet=normalize(tweet)
    tweet=_stopword_removal(tweet)
    insertTextString (a, tweet)
    return tweet

def clean_file(df):
    df["a"]=df["Tweet"]
    df["Tweet"]=df["Tweet"].apply(lowerCase)
    df["Tweet"]=df["Tweet"].apply(file_processing)
    df["Tweet"]=df["Tweet"].apply(normalize)
    df["Tweet"]=df["Tweet"].apply(_stopword_removal)
    a=pd.DataFrame(df[["a","Tweet"]])
    insertTextFile(a)

# tweet = "test www.google.com http:asd https: USER Ya akan bani\ntaplak \n dkk \xf0\x9f\x98\x84\xf0\x9f\x98\x84\xf0\x9f\x98\x84 membuang  hahah kalo bgt #jokowi3 ?? saya'"
# hasil = dataCleansing(tweet)
# print(hasil)

@swag_from("docs/swagger_text.yml", methods=['POST'])
@app.route("/text/", methods=['POST'])
def text_cleansing():
    tweet = request.get_json()
    clean_text = dataCleansing(tweet ['text'])
    return jsonify(clean_text)

@swag_from("docs/swagger_file.yml", methods=['POST'])
@app.route("/file/", methods=['POST'])
def file_cleansing():
    file = request.files['file']
    df = pd.read_csv(file, encoding=('ISO-8859-1'))
    clean_file(df)
    return jsonify({"result":"file berhasil diupload ke database"})
    

# #gradio_ui = gr.Interface(
#     fn=cleansing,
#     title="Simple Interface",
#     inputs=[gr.Textbox(label="input text")],
#     outputs=[gr.Textbox(label="output text")]
# #)

#gradio_ui.launch()

if __name__ == '__main__':
 app.run(port=1234, debug=True)
