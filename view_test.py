from flask import Flask, render_template, request ,jsonify, template_rendered
import json

app = Flask(__name__)

@app.route('/')
def first_view():
    return render_template('index.html')

@app.route('/question_view',methods=['GET','POST'])
def question_view():
    if request.method == 'POST':
        result = request.get_json()
        breakpoint()
        print(result)
    return render_template('index-3_copy.html')

@app.route('/result_view',methods=['POST'])
def result_view():
    # id = []
    # for i in range(5):
    #     print('id값 : ','flexRadioDefault'+str(i+1))
    #     data = request.form['flexRadioDefault'+str(i+1)]
    #     id.append(data)
    
    
    return render_template('blog-details.html')

if __name__ == '__main__':
    app.run()