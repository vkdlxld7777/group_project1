from flask import Flask, render_template, request ,jsonify, template_rendered
from db_controll import db_crud as conn
import random
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
db = conn()
book_emotion = pd.read_csv('/Users/vkdlx/Desktop/coding/group_project1/lib/book_emotion.csv')
category_mat = np.array(pd.read_csv('/Users/vkdlx/Desktop/coding/group_project1/lib/category_mat.csv').drop(columns='Unnamed: 0'))
author_mat = np.array(pd.read_csv('/Users/vkdlx/Desktop/coding/group_project1/lib/author_mat.csv').drop(columns='Unnamed: 0'))
keyword_mat = np.array(pd.read_csv('/Users/vkdlx/Desktop/coding/group_project1/lib/keyword_mat.csv').drop(columns='Unnamed: 0'))
avg_score = np.array(pd.read_csv('/Users/vkdlx/Desktop/coding/group_project1/lib/avg_score.csv').drop(columns='Unnamed: 0')).reshape(-1,)

def emotion_func(emotion): # emotion은 0-6까지 숫자로 변환된 감정
    emotion_sim = np.where(book_emotion['emotion']==emotion, 1, 0)
    return emotion_sim

def res(category_mat, author_mat, keyword_mat, avg_score,
        idx, emotion,
        w1=.1, w2=.1, w3=.35, w4=.1, top_n=5):
    category_sim = category_mat[idx]
    author_sim = author_mat[idx]
    keyword_sim = keyword_mat[idx]
    emotion_sim = emotion_func(emotion)
    w5 = 1 - (w1+w2+w3+w4)

    score = pd.Series(w1*category_sim + w2*author_sim + w3*keyword_sim + w4*emotion_sim + w5*avg_score)
    score.index = book_emotion.index
    top_pick = score.nlargest(top_n+1).index[1:]

    return top_pick


@app.route('/')
def first_view():
    return render_template('index.html')

@app.route('/question_view')
def question_view():
    item = [i[0] for i in db.get_category()]
    item = set(item)
    item = list(item)
    return render_template('category_sub.html',item=item)

@app.route('/category_result_view',methods=['POST'])
def category_result_view():
    select = request.form['radio']
    item = db.category_book_list(select)
    if len(item)>50:
        book_list = random.sample(item,50)
    else:
        book_list = item
    return render_template('book_select_sub.html',item = book_list)

@app.route('/book_result_view',methods=['POST'])
def book_result_view():
    select = request.form['radio']
    item = db.select_book_detail(select)
    return render_template('emotion_view_sub.html',item = item[0])

@app.route('/emotion_result_view',methods=['POST'])
def emotion_result_view():
    emotion = int(request.form['radio'])
    book = request.form['isbn']
    item_list = [i[1] for i in db.itemlist_extra()]
    idx = item_list.index(book)
    top_pick = res(category_mat, author_mat, keyword_mat, avg_score, 
                idx=idx, emotion=emotion)
    result = []
    
    for i in top_pick:
        data = item_list[i]
        db_data = list(db.select_book_detail(data)[0])
        response = requests.get(f'https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={db_data[1]}')
        soup = BeautifulSoup(response.text, 'html.parser')
        find_image = soup.find("img",id="CoverMainImage")
        if find_image.attrs['src'] != '':
            db_data.append(find_image.attrs['src'])
        else:
            db_data.append('')
        result.append(db_data)
    return render_template('recomm_book.html',item = result)

if __name__ == '__main__':
    app.run()