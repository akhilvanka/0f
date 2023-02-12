from flask import Flask, request, render_template
from bs4 import BeautifulSoup as bs
from flask_cors import CORS, cross_origin
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
    # Adds the fickle https:// tag to the front of the url JUST in case
    if "https://" not in path:
        path = "https://" + path

    headers = {
        'User-Agent': request.headers.get('User-Agent'),
        'referer': 'https://google.com',
        'Accept': request.headers.get('Accept'),
        'Accept-Language': request.headers.get('Accept-Language'),
    }

    try: 
        response = requests.get(path, headers=headers)
    except:
        pass
        
    hostname = urlparse(path).hostname

    try:
        soup = bs(response.content, "html.parser")
        tags = soup.find_all()
        for tag in tags:
            if tag.has_attr('href'):
                if "https://" not in tag.attrs['href']:
                    tag.attrs['href'] = 'https://' + hostname + tag.attrs['href']
        
        # Per Domain cleanup
        if "economist" in hostname:
            for div in soup.find_all("div", {'class':'e5tfikp1'}): 
                div.decompose()
            soup.find('div', class_='e5tfikp2').decompose()
        return soup.prettify()
    except:
        return ('', 204)


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=8080)