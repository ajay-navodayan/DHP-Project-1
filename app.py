import os
from flask import Flask, render_template, request, redirect, url_for, session
from urllib.request import urlopen
from bs4 import BeautifulSoup
from authlib.integrations.flask_client import OAuth
import psycopg2
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
nltk.download('universal_tagset')
nltk.download('punkt')
nltk.download('udhr2')
nltk.download('averaged_perceptron_tagger')


app = Flask(__name__)
oauth = OAuth(app)


app.config['SECRET_KEY'] = "Ajay"
app.config['GITHUB_CLIENT_ID'] = "0c8472d74628a280b098"
app.config['GITHUB_CLIENT_SECRET'] = "e73226578453966ee7f05f020d7e156de847151b"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

github_admin_usernames = ["ajay-navodayan", "atmabodha"]



# Authentication function
def authenticate(username, password):
    return username == 'admin' and password == 'Ajay@123'
def connect_db():
    conn = psycopg2.connect(
        host='dpg-cnm807gcmk4c73age6k0-a', database='dhp2', user='dhp2_user', password='D7Jy5rPyMAHdS44bJbz2NSZf4M3FNpCV'
    )
    return conn



# Function to clean and analyze URL
def clean_and_analyze(url):
    html = urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')

    # Extract news text
    headlines = soup.find_all('h1', class_="article-heading")
    short_desc = soup.find_all('p', class_="article-short-desc")
    article_desc = soup.find('div', class_="article-description")
    text_elements = headlines + short_desc + article_desc.find_all('p')

    # Clean extracted text
    cleaned_text = ""
    for element in text_elements:
        cleaned_text += re.sub(r'<.*?>', '', str(element)) + "\n"

   
    return cleaned_text

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_url', methods=['POST'])
def submit_url():
    url = request.form['url']
    
    # Clean and analyze the URL
    clean_text = clean_and_analyze(url)
    
    words_list = word_tokenize(clean_text) 
    sent_list = sent_tokenize(clean_text)



    def words(string):
        punc_list = ['.', ',', '!', '?']
        word_lst = word_tokenize(clean_text)
        for i in word_lst:
            if i in punc_list:
                word_lst.remove(i)
        return len(word_lst) # Total Number of words after removing punctuation marks.
    
    dict_upos = {}
    list_new = pos_tag(words_list, tagset='universal')
    for i in list_new:
        if i[1] not in dict_upos.keys():
            dict_upos[i[1]] = 1
        else:
            dict_upos[i[1]] += 1
    dict_upos = dict_upos
    sent_count = len(sent_list)
    words_count = words(clean_text)
    pos_tag_count = sum(dict_upos.values())
    
 
    
    conn = connect_db()
    cur = conn.cursor()
    ######################################################
    #creating table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Articles (
            id SERIAL PRIMARY KEY,
            url VARCHAR(1000),
            text TEXT,
            word_count INTEGER,
            Sentence_count INTEGER,
            POS_tag_count INTEGER
             
        )
    """)
    ########################################################
    cur.execute("""
        INSERT INTO Articles (url, text,word_count,Sentence_count,POS_tag_count)
        VALUES (%s, %s, %s,%s,%s)
    """, (url, clean_text, words_count,sent_count,pos_tag_count))
    conn.commit()
    conn.close()
    
    # Passing analysis data to the template
    return render_template('analysis.html', url=url, num_sentences=sent_count, num_words=words_count, pos_tags=pos_tag_count, dict_upos=dict_upos, clean_text=clean_text)




@app.route('/admin', methods=['GET', 'POST'])
def admin():
   
    if request.method == 'POST':
        if authenticate(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('url_history'))
        else:
            error = 'Invalid username or password'
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear entire session
    return redirect(url_for('index'))

@app.route('/admin/history')
def url_history():
    # Check if session exists
    if not session:
        return render_template('index.html')
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT url, text FROM Articles")
    data = cur.fetchall()
    conn.close()
    return render_template('history.html', data=data)



# Default route
@app.route('/index1')
def index1():
    is_admin = False
    github_token = session.get('github_token')
    if github_token:
        github = oauth.create_client('github')
        resp = github.get('user').json()
        username = resp.get('login')
        if username in github_admin_usernames:
            is_admin = True
    return render_template('index1.html', logged_in=github_token is not None, is_admin=is_admin)


# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    session['github_token'] = token
    resp = github.get('user').json()
    print(f"\n{resp}\n")

    if 'login' in resp:
        username = resp['login']
        if username in github_admin_usernames:
            # Fetch URL history from the database
             conn = connect_db()
             cur = conn.cursor()
             cur.execute("SELECT url, text FROM Articles")
             data = cur.fetchall()
             conn.close()

            # Render history.html template with fetched data
             return render_template("history.html", data=data)
        else:
            return "You are not authorized ."
    else:
        return "incorrect username."



if __name__ == '__main__':
    app.run(debug=True)
