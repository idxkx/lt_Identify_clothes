from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
from model import ClothingClassifier
from database import db, Wardrobe
import uuid
import logging
import glob
import datetime as dt

app = Flask(__name__)

# 设置上传文件夹
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wardrobe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 确保日志目录存在
LOG_FOLDER = 'logs'
os.makedirs(LOG_FOLDER, exist_ok=True)

# 初始化应用
with app.app_context():
    db.create_all()

# 初始化衣物分类器
classifier = ClothingClassifier()

# 添加自定义模板过滤器
@app.template_filter('datetime')
def format_datetime(timestamp):
    """将时间戳转换为可读的日期时间格式"""
    time = dt.datetime.fromtimestamp(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S')

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
        # 生成唯一文件名，避免文件名冲突
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 预测图片中的衣物类型
        try:
            logging.info(f"开始处理上传的文件: {file.filename}, 保存为: {filepath}")
            result = classifier.predict(filepath)
            result['image_path'] = filepath
            
            # 保存到我的衣橱
            if request.form.get('save_to_wardrobe') == 'true':
                logging.info(f"保存到衣橱: {result['clothing_type']}")
                wardrobe_item = Wardrobe(
                    image_path=filepath,
                    clothing_type=result['clothing_type']
                )
                db.session.add(wardrobe_item)
                db.session.commit()
                result['saved_to_wardrobe'] = True
            
            return jsonify(result)
        except Exception as e:
            logging.error(f"识别失败: {str(e)}")
            return jsonify({'error': f'识别失败: {str(e)}'})

@app.route('/wardrobe')
def wardrobe():
    """我的衣橱主页"""
    # 获取所有分类
    clothing_types = db.session.query(Wardrobe.clothing_type).distinct().all()
    clothing_types = [t[0] for t in clothing_types]
    return render_template('wardrobe.html', clothing_types=clothing_types)

@app.route('/wardrobe/<clothing_type>')
def wardrobe_category(clothing_type):
    """衣橱分类页面"""
    items = Wardrobe.query.filter_by(clothing_type=clothing_type).all()
    return render_template('category.html', clothing_type=clothing_type, items=items)

@app.route('/api/wardrobe/items')
def api_wardrobe_items():
    """获取衣橱物品API"""
    clothing_type = request.args.get('type')
    if clothing_type:
        items = Wardrobe.query.filter_by(clothing_type=clothing_type).all()
    else:
        items = Wardrobe.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/wardrobe/delete/<int:item_id>', methods=['POST'])
def delete_wardrobe_item(item_id):
    """删除衣橱物品"""
    item = Wardrobe.query.get_or_404(item_id)
    # 删除关联的图片文件
    try:
        os.remove(item.image_path)
    except:
        pass  # 如果图片不存在就忽略
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('wardrobe'))

@app.route('/view-log')
def view_log():
    """查看日志文件列表"""
    log_files = []
    
    # 查找logs目录下的所有HTML日志文件
    for file in glob.glob(os.path.join('logs', 'clothing_recognition_*.html')):
        # 获取文件名和创建时间
        filename = os.path.basename(file)
        timestamp = os.path.getmtime(file)
        log_files.append({
            'path': file,
            'filename': filename,
            'timestamp': timestamp
        })
    
    # 按照时间戳降序排序，最新的文件排在前面
    log_files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('log_list.html', log_files=log_files)

@app.route('/view-log/<path:filename>')
def view_log_file(filename):
    """查看特定的日志文件"""
    # 构建完整的文件路径
    log_path = os.path.join('logs', filename)
    
    # 安全检查，确保只能访问logs目录下的html文件
    if not os.path.exists(log_path) or not log_path.endswith('.html') or '../' in filename:
        return "文件不存在或无法访问", 404
    
    # 直接返回HTML文件
    return send_file(log_path)

if __name__ == '__main__':
    app.run(debug=True) 