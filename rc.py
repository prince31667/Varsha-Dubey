from flask import Flask, request, render_template_string
import requests
import time
import re

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Created by Rocky Roy</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; border: none; }
        button { background-color: green; color: white; cursor: pointer; }
        input[type="file"] { background-color: #444; color: white; }
    </style>
</head>
<body>
    <h1>Created by Rocky Roy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="cookies_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br>
        <button type="submit">Submit Your Details</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

def extract_post_id(post_url):
    match = re.search(r'posts/(\d+)', post_url)
    if match:
        return match.group(1)
    return None

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    # Read files
    try:
        tokens = request.files['token_file'].read().decode('utf-8').splitlines()
        cookies = request.files['cookies_file'].read().decode('utf-8').strip()
        comments = request.files['comment_file'].read().decode('utf-8').splitlines()
    except Exception:
        return render_template_string(HTML_FORM, message="❌ Token, Cookies या Comment फाइल सही नहीं है!")

    # Extract Post ID
    post_id = extract_post_id(post_url)
    if not post_id:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0

    # Auto Comments Loop
    for token in tokens:
        for comment in comments:
            payload = {'message': comment, 'access_token': token}
            response = requests.post(url, data=payload)

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 400:
                # Try using cookies if token fails
                headers = {'cookie': cookies, 'user-agent': 'Mozilla/5.0'}
                response = requests.post(url, data={'message': comment}, headers=headers)

                if response.status_code == 200:
                    success_count += 1
                else:
                    return render_template_string(HTML_FORM, message="❌ Invalid Token और Cookies!")

            time.sleep(interval)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
