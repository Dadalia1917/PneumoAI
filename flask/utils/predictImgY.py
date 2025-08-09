import json
import time
from ultralytics import YOLO
import os
import logging

class ImagePredictor:
    def __init__(self, weights_path, img_path, save_path="./runs/result.jpg", conf=0.5):
        """
        初始化ImagePredictor类
        :param weights_path: 权重文件路径
        :param img_path: 输入图像路径
        :param save_path: 结果保存路径
        :param conf: 置信度阈值
        """
        self.model = YOLO(weights_path)
        self.conf = conf
        self.img_path = img_path
        self.save_path = save_path
        # 确保save_path的目录存在
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        # 标签列表
        self.labels = ['正常', '肺炎']  # 中文标签（用于分类模型）
        self.labels_en = ['NORMAL', 'PNEUMONIA']  # 英文标签，用于匹配模型输出（分类模型）

    def predict(self):
        """
        预测图像并保存结果
        """
        start_time = time.time()  # 开始计时
        elapsed_time = 0  # 确保此变量始终被定义

        try:
            # 安全模式加载模型(禁用half精度)，避免一些模型架构问题
            results = self.model(source=self.img_path, conf=self.conf)

            elapsed_time = time.time() - start_time  # 计算用时

            all_results = {
                'labels': [],  # 存储所有标签
                'confidences': [],  # 存储所有置信度
                'allTime': f"{elapsed_time:.3f}秒"
            }

            # 检查是否有结果
            if len(results) == 0:
                print("预测失败，未获得结果。")
                all_results = {
                    'labels': '预测失败',
                    'confidences': "0.00%",
                    'allTime': f"{elapsed_time:.3f}秒"
                }
                return all_results

            # 自动检测模型类型并处理结果
            model_result = results[0]
            
            # 判断是分类模型还是检测模型
            if hasattr(model_result, 'probs') and model_result.probs is not None:
                # 分类模型处理
                print("处理分类模型结果")
                cls_idx = int(model_result.probs.top1)
                cls_conf = float(model_result.probs.top1conf)
                
                if cls_conf >= self.conf:
                    try:
                        # 使用中文标签（如果索引在范围内）
                        if cls_idx < len(self.labels):
                            label = self.labels[cls_idx]
                        else:
                            label = f"类别{cls_idx}"
                            
                        all_results['labels'].append(label)
                        all_results['confidences'].append(f"{cls_conf * 100:.2f}%")
                    except Exception as e:
                        print(f"处理分类标签时出错: {e}")
                        all_results['labels'].append(f"类别{cls_idx}")
                        all_results['confidences'].append(f"{cls_conf * 100:.2f}%")
            
            elif hasattr(model_result, 'boxes') and model_result.boxes is not None:
                # 检测模型处理
                print("处理检测模型结果")
                if len(model_result.boxes) > 0:
                    try:
                        # 获取所有检测框的类别和置信度
                        for box in model_result.boxes:
                            idx = int(box.cls[0])
                            conf = float(box.conf[0])
                            
                            # 获取类别名称（从模型中）
                            if hasattr(model_result, 'names') and idx in model_result.names:
                                label = model_result.names[idx]
                            else:
                                label = f"类别{idx}"
                                
                            all_results['labels'].append(label)
                            all_results['confidences'].append(f"{conf * 100:.2f}%")
                    except Exception as e:
                        print(f"处理检测框时出错: {e}")
            else:
                print("无法识别的模型类型或结果格式")
                
            # 保存可视化结果
            try:
                model_result.save(filename=self.save_path)
                print(f"结果已保存到 {self.save_path}")
            except Exception as e:
                print(f"保存结果图像时出错: {e}")

            # 如果没有识别出任何标签，则认为是预测失败
            if not all_results['labels']:
                print("未达到置信度阈值或未检测到目标。")
                all_results = {
                    'labels': '预测失败',
                    'confidences': "0.00%",
                    'allTime': f"{elapsed_time:.3f}秒"
                }
            
            return all_results

        except Exception as e:
            elapsed_time = time.time() - start_time  # 确保在异常情况下也计算用时
            print(f"预测过程中发生异常: {e}")
            return {
                'labels': '预测失败',
                'confidences': "0.00%",
                'allTime': f"{elapsed_time:.3f}秒"
            }


if __name__ == '__main__':
    # 初始化预测器
    predictor = ImagePredictor("../weights/yolov8-cls.pt", "../test.jpg", save_path="../runs/result.jpg", conf=0.1)

    # 执行预测
    result = predictor.predict()
    labels_str = json.dumps(result['labels'])  # 将列表转换为 JSON 格式的字符串
    confidences_str = json.dumps(result['confidences'])  # 将列表转换为 JSON 格式的字符串
    print(labels_str)
    print(confidences_str)
    print(result['allTime'])