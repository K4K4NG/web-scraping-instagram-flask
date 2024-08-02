from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import youtube_dl

app = Flask(__name__)

@app.route('/')
def home(error=None, result=None, form_id=None):
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web Scraping Application</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                color: #333;
            }
            .container {
                max-width: 1200px; /* Adjusted width */
                margin: 50px auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                display: flex;
                flex-wrap: nowrap; /* Prevent wrapping */
                gap: 20px; /* Space between cards */
                overflow-x: auto; /* Enable horizontal scrolling if needed */
            }
            h1 {
                text-align: center;
                color: #007BFF;
                width: 100%; /* Full width to center the title */
                margin-bottom: 20px; /* Space below the title */
            }
            .form-card {
                flex: 1 1 300px; /* Adjust width of each card */
                padding: 20px;
                border-radius: 8px;
                background: #fff;
                box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
            }
            .form-card h2 {
                font-size: 18px;
                color: #007BFF;
                margin-bottom: 15px; /* Space between title and form */
            }
            form {
                margin: 0;
            }
            label {
                font-weight: bold;
                display: block;
                margin-bottom: 8px;
            }
            input[type="text"] {
                width: calc(100% - 22px);
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #ccc;
                box-sizing: border-box;
            }
            input[type="submit"] {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #28a745;
                color: #fff;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            input[type="submit"]:hover {
                background-color: #218838;
            }
            .result {
                padding: 15px;
                border-radius: 5px;
                background-color: #e9ecef;
                margin-top: 10px;
                border: 1px solid #ccc;
            }
            .error {
                color: red;
                font-weight: bold;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="form-card">
                <h2>Instagram Photo Scraper</h2>
                <form action="/scrape" method="post">
                    <label for="url">Enter URL for Instagram Photo:</label>
                    <input type="text" id="url" name="url">
                    <input type="submit" value="Scrape">
                    {% if form_id == 'scrape' %}
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        {% if result %}
                            <div class="result">{{ result|safe }}</div>
                        {% endif %}
                    {% endif %}
                </form>
            </div>
            <div class="form-card">
                <h2>Instagram Profile Scraper</h2>
                <form action="/scrape_instagram" method="post">
                    <label for="username">Enter Instagram Username:</label>
                    <input type="text" id="username" name="username">
                    <input type="submit" value="Scrape Instagram Profile">
                    {% if form_id == 'scrape_instagram' %}
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        {% if result %}
                            <div class="result">{{ result|safe }}</div>
                        {% endif %}
                    {% endif %}
                </form>
            </div>
            <div class="form-card">
                <h2>YouTube Video Downloader</h2>
                <form action="/download_youtube" method="post">
                    <label for="youtube_url">Enter YouTube URL:</label>
                    <input type="text" id="youtube_url" name="youtube_url">
                    <input type="submit" value="Download YouTube Video">
                    {% if form_id == 'download_youtube' %}
                        {% if error %}
                            <div class="error">{{ error }}</div>
                        {% endif %}
                        {% if result %}
                            <div class="result">{{ result|safe }}</div>
                        {% endif %}
                    {% endif %}
                </form>
            </div>
        </div>
    </body>
    </html>
    ''', error=error, result=result, form_id=form_id)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    if not url:
        return home(error="URL cannot be empty.", form_id='scrape')
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        caption = soup.find('meta', property='og:description')['content']
        result = f"Caption: {caption}"
    except Exception as e:
        result = f"Error: {str(e)}"
    return home(result=result, form_id='scrape')

@app.route('/scrape_instagram', methods=['POST'])
def scrape_instagram():
    username = request.form['username']
    if not username:
        return home(error="Username cannot be empty.", form_id='scrape_instagram')
    try:
        url = f"https://www.instagram.com/{username}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        followers_tag = soup.find('meta', attrs={'property': 'og:description', 'content': True})
        followers_count = following_count = post_count = "N/A"
        if followers_tag:
            followers_content = followers_tag['content']
            followers_count = followers_content.split(',')[0].split()[0]
            following_count = followers_content.split(',')[1].split()[0]
            post_count = followers_content.split(',')[2].split()[0]
        result = f"Pengguna: {username}<br>Pengikut: {followers_count}<br>Mengikuti: {following_count}<br>Jumlah Postingan: {post_count}"
    except Exception as e:
        result = f"Error: {str(e)}"
    return home(result=result, form_id='scrape_instagram')

@app.route('/download_youtube', methods=['POST'])
def download_youtube():
    url = request.form['youtube_url']
    if not url:
        return home(error="YouTube URL cannot be empty.", form_id='download_youtube')
    try:
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        result = f"Video from {url} has been downloaded."
    except Exception as e:
        result = f"Error: {str(e)}"
    return home(result=result, form_id='download_youtube')

if __name__ == '__main__':
    app.run(debug=True)
    