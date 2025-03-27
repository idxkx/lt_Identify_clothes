import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import logging
import datetime
import codecs
import sys

# 生成带时间戳的日志文件名
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"clothing_recognition_{timestamp}.html"

# 确保日志目录存在
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_path = os.path.join(logs_dir, log_file)

# 创建HTML日志文件，并写入HTML头
with codecs.open(log_path, 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>服装识别日志</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .log-entry { margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .info { color: #0066cc; }
        .warning { color: #ff9900; }
        .error { color: #cc0000; }
        .log-time { color: #666; font-size: 0.9em; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>服装识别系统日志</h1>
    <p>开始时间: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    <div id="log-entries">
""")

# 自定义日志处理器，将日志写入HTML文件
class HtmlLogHandler(logging.Handler):
    def __init__(self, log_file):
        logging.Handler.__init__(self)
        self.log_file = log_file
        
    def emit(self, record):
        try:
            msg = self.format(record)
            level_class = 'info'
            if record.levelname == 'WARNING':
                level_class = 'warning'
            elif record.levelname == 'ERROR':
                level_class = 'error'
                
            log_entry = f"""<div class="log-entry {level_class}">
    <span class="log-time">{datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')}</span> - 
    <span class="log-level">{record.levelname}</span>: {msg}
</div>
"""
            with codecs.open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            self.handleError(record)

# 配置日志
logger = logging.getLogger('clothing_recognition')
logger.setLevel(logging.INFO)

# 添加控制台输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# 添加HTML文件输出
html_handler = HtmlLogHandler(log_path)
html_handler.setLevel(logging.INFO)
html_format = logging.Formatter('%(message)s')
html_handler.setFormatter(html_format)
logger.addHandler(html_handler)

# 注册应用结束时的处理函数
import atexit

def close_log_file():
    with codecs.open(log_path, 'a', encoding='utf-8') as f:
        f.write("""
    </div>
    <p>结束时间: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</body>
</html>""")
    logger.info("日志文件已关闭")

atexit.register(close_log_file)

# 记录初始日志
logger.info("服装识别系统启动")
logger.info(f"日志文件保存在: {log_path}")

class ClothingClassifier:
    """衣物分类器类，负责加载模型和进行预测"""
    
    def __init__(self):
        # 加载预训练模型
        logger.info("正在初始化衣物分类器...")
        self.model = MobileNetV2(weights='imagenet')
        logger.info("MobileNetV2模型加载成功")
        
        # 衣物类别映射
        self.clothing_categories = {
            'jersey': '上衣',
            'kimono': '上衣',
            'cardigan': '上衣',
            'jacket': '上衣',
            'vestment': '上衣',
            'suit': '上衣',
            'gown': '上衣',
            'sweater': '上衣',
            'shirt': '上衣',
            'tee_shirt': '上衣',
            'blouse': '上衣',
            'hoodie': '上衣',
            
            'jean': '裤子',
            'tights': '裤子',
            'swimming_trunks': '裤子',
            'trouser': '裤子',
            'pants': '裤子',
            'legging': '裤子',
            
            'miniskirt': '裙子',
            'skirt': '裙子',
            'dress': '裙子',
            'overskirt': '裙子',
            
            'diaper': '内衣',
            'brassiere': '内衣',
            'lingerie': '内衣',
            'underpants': '内衣',
            'boxer': '内衣',
            
            'purse': '包包',
            'backpack': '包包',
            'handbag': '包包',
            'baggage': '包包',
            'suitcase': '包包',
            
            'wallet': '配饰',
            'sunglasses': '配饰',
            'bow_tie': '配饰',
            'sock': '配饰',
            'necklace': '配饰',
            'sunglass': '配饰',
            'mask': '配饰',
            'cap': '配饰',
            'hat': '配饰',
            'tie': '配饰',
            'scarf': '配饰',
            'glove': '配饰',
            'watch': '配饰',
            'jewelry': '配饰'
        }
        logger.info(f"已配置 {len(self.clothing_categories)} 个衣物分类映射")
    
    def map_to_clothing_type(self, prediction_classes):
        """将ImageNet类别映射到衣物类型"""
        for class_name in prediction_classes:
            for key in self.clothing_categories:
                if key in class_name.lower():
                    logger.info(f"找到匹配: ImageNet类别 '{class_name}' 匹配到关键词 '{key}', 映射到衣物类型 '{self.clothing_categories[key]}'")
                    return self.clothing_categories[key]
        
        # 如果没有匹配到任何衣物类别
        logger.warning(f"未找到匹配: ImageNet类别 {prediction_classes} 未能匹配到任何已知衣物类型")
        return "未识别到衣物"
    
    def predict(self, img_path):
        """预测图片中的衣物类型"""
        logger.info(f"开始处理图片: {img_path}")
        
        # 加载并预处理图像
        try:
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            logger.info("图片预处理成功")
        except Exception as e:
            logger.error(f"图片预处理失败: {str(e)}")
            raise
        
        # 进行预测
        try:
            logger.info("开始模型预测...")
            preds = self.model.predict(x)
            predictions = decode_predictions(preds, top=5)[0]
            logger.info("模型预测成功")
            
            # 记录原始预测结果
            logger.info("原始预测结果:")
            for i, (imagenet_id, label, score) in enumerate(predictions):
                logger.info(f"  Top {i+1}: {label} (ID: {imagenet_id}) - 置信度: {score*100:.2f}%")
            
            # 提取预测类别名称
            prediction_classes = [pred[1] for pred in predictions]
            
            # 映射到衣物类型
            clothing_type = self.map_to_clothing_type(prediction_classes)
            logger.info(f"最终识别结果: {clothing_type}")
            
            return {
                'clothing_type': clothing_type,
                'predictions': [{'label': p[1], 'score': float(p[2])} for p in predictions]
            }
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            raise 