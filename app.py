from flask import Flask, render_template, request, jsonify
import os
from model import ClothingClassifier

app = Flask(__name__)

# 设置上传文件夹
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 初始化衣物分类器
classifier = ClothingClassifier()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '未选择文件'})
    
    if file:
        # 保存上传的文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # 预测图片中的衣物类型
        try:
            result = classifier.predict(filename)
            result['image_path'] = filename
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'识别失败: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True) 