import json
import time
from ultralytics import RTDETR


class ImagePredictor:
    def __init__(self, weights_path, img_path, save_path="./runs/result.jpg", conf=0.5):
        """
        初始化ImagePredictor类
        :param weights_path: 权重文件路径
        :param img_path: 输入图像路径
        :param save_path: 结果保存路径
        :param conf: 置信度阈值
        """
        self.model = RTDETR(weights_path)
        self.conf = conf
        self.img_path = img_path
        self.save_path = save_path
        # 课堂行为标签列表
        self.labels = ['举手', '阅读', '写字', '玩手机', '低头', '趴桌子']  # 中文标签
        self.labels_en = ['hand-raising', 'reading', 'writing', 'using phone', 'bowing the head', 'leaning over the table']  # 英文标签，用于匹配模型输出

    def predict(self):
        """
        预测图像并保存结果
        """
        start_time = time.time()  # 开始计时

        try:
            # 执行预测
            results = self.model(source=self.img_path, conf=self.conf, half=True, save_conf=True)

            end_time = time.time()  # 结束计时
            elapsed_time = end_time - start_time  # 计算用时

            all_results = {
                'labels': [],  # 存储所有标签
                'confidences': [],  # 存储所有置信度
                'allTime': f"{elapsed_time:.3f}秒"
            }

            # 检查是否有检测结果
            if len(results) == 0 or not results[0].boxes:
                print("未检测到目标，请换一张图片。")
                all_results = {
                    'labels': '预测失败',
                    'confidences': "0.00%",
                    'allTime': f"{elapsed_time:.3f}秒"
                }
                return all_results

            for result in results:
                # 提取置信度和标签
                boxes = result.boxes
                if not boxes.conf.numel() or not boxes.cls.numel():
                    continue

                # 获取标签名称和对应置信度
                for conf, cls in zip(boxes.conf, boxes.cls):
                    label = self.labels[int(cls)]  # 使用中文标签显示
                    all_results['labels'].append(label)
                    all_results['confidences'].append(f"{conf * 100:.2f}%")

                # 在图像上绘制检测框和标签
                result.save(filename=self.save_path)  # 保存带有检测框和标签的结果图

            return all_results

        except Exception as e:
            print(f"预测过程中发生异常: {e}")
            return {
                'labels': '预测失败',
                'confidences': "0.00%",
                'allTime': f"{elapsed_time:.3f}秒"
            }


if __name__ == '__main__':
    # 初始化预测器
    predictor = ImagePredictor("../weights/helmet_best.pt", "../test.jpg", save_path="../runs/result.jpg", conf=0.1)

    # 执行预测
    result = predictor.predict()
    labels_str = json.dumps(result['labels'])  # 将列表转换为 JSON 格式的字符串
    confidences_str = json.dumps(result['confidences'])  # 将列表转换为 JSON 格式的字符串
    print(labels_str)
    print(confidences_str)
    print(result['allTime'])