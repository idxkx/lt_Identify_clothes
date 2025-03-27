import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os

class ClothingClassifier:
    """衣物分类器类，负责加载模型和进行预测"""
    
    def __init__(self):
        # 加载预训练模型
        self.model = MobileNetV2(weights='imagenet')
        
        # 衣物类别映射
        self.clothing_categories = {
            'diaper': '内衣',
            'jersey': '上装',
            'kimono': '上装',
            'cardigan': '上装',
            'jacket': '上装',
            'brassiere': '内衣',
            'tights': '下装',
            'miniskirt': '下装',
            'running_shoe': '鞋子',
            'sandal': '鞋子',
            'wallet': '配饰',
            'purse': '包包',
            'backpack': '包包',
            'sunglasses': '配饰',
            'jean': '下装',
            'vestment': '上装',
            'suit': '上装',
            'bow_tie': '配饰',
            'sock': '配饰',
            'swimming_trunks': '下装',
            'gown': '上装',
            'necklace': '配饰',
            'sunglass': '配饰',
            'mask': '配饰',
            'cap': '配饰',
            'hat': '配饰'
        }
    
    def map_to_clothing_type(self, prediction_classes):
        """将ImageNet类别映射到衣物类型"""
        for class_name in prediction_classes:
            for key in self.clothing_categories:
                if key in class_name.lower():
                    return self.clothing_categories[key]
        
        # 如果没有匹配到任何衣物类别
        return "未识别到衣物"
    
    def predict(self, img_path):
        """预测图片中的衣物类型"""
        # 加载并预处理图像
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        # 进行预测
        preds = self.model.predict(x)
        predictions = decode_predictions(preds, top=5)[0]
        
        # 提取预测类别名称
        prediction_classes = [pred[1] for pred in predictions]
        
        # 映射到衣物类型
        clothing_type = self.map_to_clothing_type(prediction_classes)
        
        return {
            'clothing_type': clothing_type,
            'predictions': [{'label': p[1], 'score': float(p[2])} for p in predictions]
        } 