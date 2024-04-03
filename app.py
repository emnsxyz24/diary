import os
from os.path import join, dirname
from bson import ObjectId
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}))
    for article in articles:
        article['_id'] = str(article['_id'])
    return jsonify({'articles': articles})

@app.route('/diary/delete', methods=['POST'])
def delete_diary():
    id_receive = request.form["post_id"]
    img_receive = request.form["imgURI"]
    profile_receive = request.form["profileURI"]
    os.remove(img_receive)
    os.remove(profile_receive)
    
    db.diary.delete_one(
        {'_id': ObjectId(id_receive)}
    )
    return jsonify({'msg': 'Delete done!'})

@app.route('/diary', methods=['POST'])
def save_diary():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]
    
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    mytime_post = today.strftime('%Y.%m.%d')
    
    
    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]
    filename = 'static/post-{}.{}'.format(mytime, extension)
    # filename_mongo = 'static/post-{}.{}'.format(mytime, extension)
    file.save(filename)

    profile = request.files["profile_give"]
    extension = profile.filename.split('.')[-1]
    profilename = 'static/profile-{}.{}'.format(mytime, extension)
    # profilename_mongo = 'static/profile-{}.{}'.format(mytime, extension)
    
    profile.save(profilename)
    
    
    doc = {
    'file': filename,
    'profile':profilename,
    'title': title_receive.strip(),
    'content': content_receive.strip(),
    'post_time':mytime_post
    }
    db.diary.insert_one(doc)

    return jsonify({'msg':'Upload complete!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
