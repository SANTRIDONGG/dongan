import os
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

app = Flask(__name__)

DATA_FOLDER = 'data'
os.makedirs(DATA_FOLDER, exist_ok=True)

def list_news():
    files = [f for f in os.listdir(DATA_FOLDER) if f.startswith('news_') and f.endswith('.json')]
    news_list = []
    for fn in files:
        filepath = os.path.join(DATA_FOLDER, fn)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            news_id = fn[5:-5]
            title = "Berita " + news_id
            if '<h1>' in content:
                start = content.find('<h1>') + 4
                end = content.find('</h1>')
                if end > start:
                    title = content[start:end]
            news_list.append({'id': news_id, 'title': title})
        except:
            continue
    return sorted(news_list, key=lambda x: x['id'])

@app.route('/')
def dashboard():
    return redirect(url_for('admin_news'))

@app.route('/admin/news')
def admin_news():
    news_list = list_news()
    return render_template('admin_news.html', news_list=news_list)

@app.route('/admin/news/new')
def new_news():
    return redirect(url_for('edit_news', news_id='new'))

@app.route('/admin/news/edit/<news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    filepath = os.path.join(DATA_FOLDER, f'news_{news_id}.json') if news_id != 'new' else None

    if request.method == 'POST':
        data = request.json
        content = data.get('content', '')
        if news_id == 'new':
            import time
            news_id = str(int(time.time()))
            filepath = os.path.join(DATA_FOLDER, f'news_{news_id}.json')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'status': 'success', 'news_id': news_id})

    content = ''
    if filepath and os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    return render_template('editor.html', content=content, news_id=news_id)

@app.route('/news/<news_id>')
def news_detail(news_id):
    filepath = os.path.join(DATA_FOLDER, f'news_{news_id}.json')
    if not os.path.isfile(filepath):
        return "Berita tidak ditemukan", 404
    with open(filepath, 'r', encoding='utf-8') as f:
        content_html = f.read()
    return render_template('news_detail.html', content=content_html, idpage=news_id)

if __name__ == '__main__':
    app.run(debug=True)
