from flask import Flask, request, render_template, redirect
from bs4 import BeautifulSoup as bs
from flask_cors import CORS, cross_origin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import re
import requests
from urllib.parse import urlparse

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    if ".com" in path and "https://" not in path:
        path = "https://" + path

    hostname = urlparse(path).hostname

    if 'wsj' in hostname: 
        return redirect('https://facebook.com/l.php?u=' + path)
    elif request.headers.get('referer') is not None:
        try:
            if "/gen_" in path:
                return ('', 204)
            else:
                redirect_url = 'https://' + urlparse(urlparse(request.headers.get('referer')).path[1:]).hostname + '/' + path
                return redirect(redirect_url)
        except:
            return ('', 204)
    else:
        headers = {
            'User-Agent': request.headers.get('User-Agent'),
            'referer': 'https://google.com',
            'X-Forwarded-For': request.remote_addr,
            'Accept': 'text/html',
            'Accept-Language': request.headers.get('Accept-Language'),
            'Connection': 'keep-alive',
        }

        try: 
            response = requests.get(path, headers=headers)
            print(response.status_code)
            if response.status_code != 200:
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)
                driver.get(path)
                html = driver.page_source
                response.content = html
                driver.close()
        except:
            pass
            

        try:
            soup = bs(response.content, "html.parser")
            tags = soup.find_all()
            for tag in tags:
                if tag.has_attr('href'):
                    if "https:" not in tag.attrs['href']:
                        tag.attrs['href'] = 'https://' + hostname + tag.attrs['href']
        
            return soup.prettify()
        except:
            return ('', 204)


if __name__ == '__main__':
    app.run()

