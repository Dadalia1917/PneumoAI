import json
import os
import subprocess

import cv2
import requests
from flask import Flask, Response, request
from flask_socketio import SocketIO, emit
from ultralytics import YOLO

from utils import predictImgY, chatApi


# Flask 应用设置
class VideoProcessingApp:
    def __init__(self, host='0.0.0.0', port=5000):
        """初始化 Flask 应用并设置路由"""
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")  # 初始化 SocketIO
        self.host = host
        self.port = port
        self.setup_routes()
        self.data = {}  # 存储接收参数
        self.paths = {
            'download': './runs/video/download.mp4',
            'output': './runs/video/output.mp4',
            'camera_output': "./runs/video/camera_output.avi",
            'video_output': "./runs/video/camera_output.avi"
        }
        self.recording = False  # 标志位，判断是否正在录制视频
        # API密钥配置
        self.DeepSeek = 'sk-e81dacdd9f93432b831de696176df1a6'
        self.Qwen = 'sk-lluefpkltgpoobuybmjbsjfpqmrngxpaqfpkesbqwwmhgykz'

    def setup_routes(self):
        """设置所有路由"""
        self.app.add_url_rule('/file_names', 'file_names', self.file_names, methods=['GET'])
        self.app.add_url_rule('/predictImg', 'predictImg', self.predictImg, methods=['POST'])
        self.app.add_url_rule('/predictVideo', 'predictVideo', self.predictVideo)
        self.app.add_url_rule('/predictCamera', 'predictCamera', self.predictCamera)
        self.app.add_url_rule('/stopCamera', 'stopCamera', self.stopCamera, methods=['GET'])
        self.app.add_url_rule('/test_think_mode', 'test_think_mode', self.test_think_mode, methods=['POST'])

        # 添加 WebSocket 事件
        @self.socketio.on('connect')
        def handle_connect():
            print("WebSocket connected!")
            emit('message', {'data': 'Connected to WebSocket server!'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("WebSocket disconnected!")

    def run(self):
        """启动 Flask 应用"""
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

    def file_names(self):
        """模型列表接口"""
        weight_items = [{'value': name, 'label': name} for name in self.get_file_names("./weights")]
        return json.dumps({'weight_items': weight_items})

    def predictImg(self):
        """图片预测接口"""
        data = request.get_json()
        # 打印完整请求数据
        print("接收到的完整请求数据:", data)
        print("原始thinkMode值:", data.get('thinkMode'), "类型:", type(data.get('thinkMode')))
        
        # 处理thinkMode的各种可能情况
        think_mode_value = data.get('thinkMode')
        if think_mode_value is None:
            think_mode_result = False
        elif isinstance(think_mode_value, bool):
            think_mode_result = think_mode_value
        elif isinstance(think_mode_value, str):
            think_mode_result = think_mode_value.lower() == 'true'
        else:
            think_mode_result = bool(think_mode_value)
        
        self.data.clear()
        self.data.update({
            "username": data['username'], "weight": data['weight'],
            "conf": data['conf'], "startTime": data['startTime'],
            "inputImg": data['inputImg'], "ai": data['ai'],
            "thinkMode": think_mode_result
        })
        # 打印处理后的thinkMode值
        print("处理后thinkMode值:", self.data["thinkMode"], "类型:", type(self.data["thinkMode"]))
        print(self.data)
        predict = predictImgY.ImagePredictor(weights_path=f'./weights/{self.data["weight"]}',
                                            img_path=self.data["inputImg"], save_path='./runs/result.jpg',
                                            conf=float(self.data["conf"]))
        # 执行预测
        results = predict.predict()
        uploadedUrl = self.upload('./runs/result.jpg')
        if results['labels'] != '预测失败':
            self.data["status"] = 200
            self.data["message"] = "预测成功"
            self.data["outImg"] = uploadedUrl
            self.data["allTime"] = results['allTime']
            self.data["confidence"] = json.dumps(results['confidences'])
            self.data["label"] = json.dumps(results['labels'])
        else:
            self.data["status"] = 400
            self.data["message"] = "该图片无法识别，请重新上传！"
        
        # 根据选择的AI模型生成建议
        if self.data["status"] == 200:
            chat = chatApi.ChatAPI(
                deepseek_api_key=self.DeepSeek,
                qwen_api_key=self.Qwen
            )
            list_input = self.process_list(results['labels'])
            text = "我用YOLO检测出"
            for i in list_input:
                text += i
                text += "，"
            text += "请你作为一名经验丰富的医学专家，针对这个诊断结果，提供专业的医疗建议，包括可能的治疗方案、康复措施、注意事项等。如果诊断为正常，请给出健康维护的建议。只需回答我要的结果，不需要额外说明。"
            messages = [
                {"role": "user", "content": text}
            ]
            
            if self.data["ai"] == 'Deepseek-R1':
                self.socketio.emit('message', {'data': '已检测完成，正在生成DeepSeekAI建议！'})
                self.data["suggestion"] = chat.deepseek_request(messages)
            elif self.data["ai"] == 'Qwen':
                self.socketio.emit('message', {'data': '已检测完成，正在生成QwenAI建议！'})
                self.data["suggestion"] = chat.qwen_request(messages)
            elif self.data["ai"] == 'Deepseek-R1-LAN':
                self.socketio.emit('message', {'data': '已检测完成，正在生成局域网Deepseek-R1建议！'})
                self.data["suggestion"] = chat.lan_deepseek_request(messages)
            elif self.data["ai"] == 'Deepseek-R1-Local':
                self.socketio.emit('message', {'data': '已检测完成，正在生成本地Deepseek-R1建议！'})
                self.data["suggestion"] = chat.local_deepseek_request(messages)
            elif self.data["ai"] == 'Gemma3-Local':
                self.socketio.emit('message', {'data': '已检测完成，正在生成本地Gemma3建议！'})
                self.data["suggestion"] = chat.local_gemma_request(messages)
            elif self.data["ai"] == 'Gemma3-LAN':
                self.socketio.emit('message', {'data': '已检测完成，正在生成局域网Gemma3建议！'})
                self.data["suggestion"] = chat.lan_gemma_request(messages)
            elif self.data["ai"] == 'Qwen3.0-Local':
                self.socketio.emit('message', {'data': '已检测完成，正在生成本地qwen3.0建议！'})
                self.data["suggestion"] = chat.local_qwen3_request(messages, think_mode=bool(self.data.get("thinkMode", False)))
            elif self.data["ai"] == 'Qwen3.0-LAN':
                self.socketio.emit('message', {'data': '已检测完成，正在生成局域网qwen3.0建议！'})
                self.data["suggestion"] = chat.lan_qwen3_request(messages, think_mode=bool(self.data.get("thinkMode", False)))
            elif self.data["ai"] == 'Qwen2.5-VL-Local':
                self.socketio.emit('message', {'data': '已检测完成，正在生成本地qwen2.5-VL建议！'})
                self.data["suggestion"] = chat.local_qwen25vl_request(messages)
            elif self.data["ai"] == 'Qwen2.5-VL-LAN':
                self.socketio.emit('message', {'data': '已检测完成，正在生成局域网qwen2.5-VL建议！'})
                self.data["suggestion"] = chat.lan_qwen25vl_request(messages)
            else:
                # 当选择"不使用AI"或未选择时，设置为空字符串
                self.data["suggestion"] = ""
        else:
            self.data["suggestion"] = ""
        path = self.data["inputImg"].split('/')[-1]
        if os.path.exists('./' + path):
            os.remove('./' + path)
        return json.dumps(self.data, ensure_ascii=False)

    def predictVideo(self):
        """视频预测接口"""
        self.data.clear()
        
        # 打印原始请求参数
        print("视频预测原始请求参数:", request.args)
        print("视频预测原始thinkMode值:", request.args.get('thinkMode'), "类型:", type(request.args.get('thinkMode')))
        
        # 处理thinkMode的各种可能情况
        think_mode_value = request.args.get('thinkMode')
        if think_mode_value is None:
            think_mode_result = False
        elif isinstance(think_mode_value, bool):
            think_mode_result = think_mode_value
        elif isinstance(think_mode_value, str):
            think_mode_result = think_mode_value.lower() == 'true'
        else:
            think_mode_result = bool(think_mode_value)
            
        self.data.update({
            "username": request.args.get('username'),
            "weight": request.args.get('weight'),
            "conf": request.args.get('conf'),
            "startTime": request.args.get('startTime'),
            "ai": request.args.get('ai'),
            "thinkMode": think_mode_result
        })
        
        # 打印处理后的thinkMode值
        print("视频预测处理后thinkMode值:", self.data["thinkMode"], "类型:", type(self.data["thinkMode"]))
        
        if not all([self.data["username"], self.data["weight"], self.data["conf"]]):
            return json.dumps({"status": 400, "message": "参数不完整", "code": -1})
            
        self.socketio.emit('message', {'data': '正在加载，请稍等！'})
        model = YOLO(f'./weights/{self.data["weight"]}')
        
        # 下载视频文件
        video_url = request.args.get('inputVideo')
        if not video_url:
            return json.dumps({"status": 400, "message": "未上传视频", "code": -1})
            
        # 使用download方法下载视频
        os.makedirs(os.path.dirname(self.paths['download']), exist_ok=True)
        try:
            with requests.get(video_url, stream=True) as response:
                response.raise_for_status()
                with open(self.paths['download'], 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            print(f"视频已成功下载并保存到 {self.paths['download']}")
        except requests.RequestException as e:
            print(f"视频下载失败: {e}")
            return json.dumps({"status": 400, "message": f"视频下载失败: {str(e)}", "code": -1})
            
        self.data["inputVideo"] = video_url
        
        cap = cv2.VideoCapture(self.paths['download'])
        if not cap.isOpened():
            return json.dumps({"status": 400, "message": "无法打开视频文件", "code": -1})
            
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_writer = cv2.VideoWriter(
            self.paths['video_output'],
            cv2.VideoWriter_fourcc(*'XVID'),
            30,
            (frame_width, frame_height)
        )
        
        all_labels = []  # 存储所有检测到的标签

        def generate():
            try:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.resize(frame, (640, 480))
                    results = model.predict(source=frame, conf=float(self.data['conf']), show=False)
                    
                    # 检查是否有结果
                    if len(results) == 0:
                        continue
                        
                    # 获取结果并绘制
                    result = results[0]
                    processed_frame = result.plot()
                    video_writer.write(processed_frame)
                    
                    # 收集当前帧的标签 - 适配分类模型
                    if hasattr(result, 'probs') and result.probs is not None:
                        # 分类模型处理
                        cls_idx = int(result.probs.top1)
                        cls_conf = float(result.probs.top1conf)
                        
                        # 只有置信度大于阈值才收集标签
                        if cls_conf >= float(self.data['conf']):
                            # 使用中文标签
                            label = ['正常', '肺炎'][cls_idx]
                            all_labels.append(label)
                    elif hasattr(result, 'boxes') and len(result.boxes) > 0:
                        # 检测模型处理(兼容)
                        current_labels = result.names
                        current_boxes = result.boxes
                        for box in current_boxes:
                            label_id = int(box.cls[0])
                            if label_id in current_labels:
                                all_labels.append(current_labels[label_id])
                    
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': '处理完成，正在保存！'})
                
                # 处理AI建议
                if self.data.get("ai") and all_labels:
                    chat = chatApi.ChatAPI(
                        deepseek_api_key=self.DeepSeek,
                        qwen_api_key=self.Qwen
                    )
                    unique_labels = self.process_list(all_labels)
                    text = "我用YOLO检测出"
                    for label in unique_labels:
                        text += label + "，"
                    text += "请你作为一名经验丰富的医学专家，针对这个诊断结果，提供专业的医疗建议，包括可能的治疗方案、康复措施、注意事项等。如果诊断为正常，请给出健康维护的建议。只需回答我要的结果，不需要额外说明。"
                    messages = [{"role": "user", "content": text}]
                    
                    suggestion = ""
                    if self.data["ai"] == 'Deepseek-R1':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成DeepSeekAI建议！'})
                        suggestion = chat.deepseek_request(messages)
                    elif self.data["ai"] == 'Qwen':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成QwenAI建议！'})
                        suggestion = chat.qwen_request(messages)
                    elif self.data["ai"] == 'Deepseek-R1-LAN':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成局域网Deepseek-R1建议！'})
                        suggestion = chat.lan_deepseek_request(messages)
                    elif self.data["ai"] == 'Deepseek-R1-Local':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成本地Deepseek-R1建议！'})
                        suggestion = chat.local_deepseek_request(messages)
                    elif self.data["ai"] == 'Gemma3-Local':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成本地Gemma3建议！'})
                        suggestion = chat.local_gemma_request(messages)
                    elif self.data["ai"] == 'Gemma3-LAN':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成局域网Gemma3建议！'})
                        suggestion = chat.lan_gemma_request(messages)
                    elif self.data["ai"] == 'Qwen3.0-Local':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成本地qwen3.0建议！'})
                        suggestion = chat.local_qwen3_request(messages, think_mode=bool(self.data.get("thinkMode", False)))
                    elif self.data["ai"] == 'Qwen3.0-LAN':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成局域网qwen3.0建议！'})
                        suggestion = chat.lan_qwen3_request(messages, think_mode=bool(self.data.get("thinkMode", False)))
                    elif self.data["ai"] == 'Qwen2.5-VL-Local':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成本地qwen2.5-VL建议！'})
                        suggestion = chat.local_qwen25vl_request(messages)
                    elif self.data["ai"] == 'Qwen2.5-VL-LAN':
                        self.socketio.emit('message', {'data': '已检测完成，正在生成局域网qwen2.5-VL建议！'})
                        suggestion = chat.lan_qwen25vl_request(messages)
                    
                    if suggestion:
                        print(f"生成AI建议成功，长度: {len(suggestion)}，前100个字符: {suggestion[:100]}")
                        self.data["suggestion"] = suggestion
                        # 确保直接发送字符串，不要嵌套在data字段中
                        self.socketio.emit('suggestion', suggestion)
                        print("已发送suggestion事件到前端")
                        # 再发送一条消息通知前端
                        self.socketio.emit('message', {'data': 'AI建议生成完成，请查看页面底部！'})
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(self.paths['output']), exist_ok=True)
                
                for progress in self.convert_avi_to_mp4(self.paths['video_output']):
                    self.socketio.emit('progress', {'data': progress})
                
                try:
                    uploadedUrl = self.upload(self.paths['output'])
                    self.data["outVideo"] = uploadedUrl
                    self.save_data(json.dumps(self.data), 'http://localhost:9999/videoRecords')
                except Exception as e:
                    print(f"上传文件或保存记录时发生错误: {str(e)}")
                finally:
                    self.cleanup_files([self.paths['download'], self.paths['output'], self.paths['video_output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def predictCamera(self):
        """摄像头视频流处理接口"""
        self.data.clear()
        self.data.update({
            "username": request.args.get('username'), "weight": request.args.get('weight'),
            "conf": request.args.get('conf'), "startTime": request.args.get('startTime')
        })
        self.socketio.emit('message', {'data': '正在加载，请稍等！'})
        model = YOLO(f'./weights/{self.data["weight"]}')
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.paths['camera_output']), exist_ok=True)
        
        video_writer = cv2.VideoWriter(self.paths['camera_output'], cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
        self.recording = True
        
        # 用于收集所有的标签
        all_labels = []

        def generate():
            try:
                while self.recording:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    results = model.predict(source=frame, imgsz=640, conf=float(self.data['conf']), show=False)
                    
                    # 检查是否有结果
                    if len(results) == 0:
                        continue
                        
                    # 获取结果并绘制
                    result = results[0]
                    processed_frame = result.plot()
                    
                    # 收集当前帧的标签 - 适配分类模型
                    if hasattr(result, 'probs') and result.probs is not None:
                        # 分类模型处理
                        cls_idx = int(result.probs.top1)
                        cls_conf = float(result.probs.top1conf)
                        
                        # 只有置信度大于阈值才收集标签
                        if cls_conf >= float(self.data['conf']):
                            # 使用中文标签
                            label = ['正常', '肺炎'][cls_idx]
                            all_labels.append(label)
                    elif hasattr(result, 'boxes') and len(result.boxes) > 0:
                        # 检测模型处理(兼容)
                        current_labels = result.names
                        current_boxes = result.boxes
                        for box in current_boxes:
                            label_id = int(box.cls[0])
                            if label_id in current_labels:
                                all_labels.append(current_labels[label_id])
                    
                    if self.recording and video_writer:
                        video_writer.write(processed_frame)
                    
                    _, jpeg = cv2.imencode('.jpg', processed_frame)
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            finally:
                self.cleanup_resources(cap, video_writer)
                self.socketio.emit('message', {'data': '处理完成，正在保存！'})
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(self.paths['output']), exist_ok=True)
                
                for progress in self.convert_avi_to_mp4(self.paths['camera_output']):
                    self.socketio.emit('progress', {'data': progress})
                
                try:
                    uploadedUrl = self.upload(self.paths['output'])
                    self.data["outVideo"] = uploadedUrl
                    self.save_data(json.dumps(self.data), 'http://localhost:9999/cameraRecords')
                except Exception as e:
                    print(f"上传文件或保存记录时发生错误: {str(e)}")
                finally:
                    self.cleanup_files([self.paths['camera_output'], self.paths['output']])

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stopCamera(self):
        """停止摄像头预测"""
        self.recording = False
        return json.dumps({"status": 200, "message": "预测成功", "code": 0})

    def test_think_mode(self):
        """测试思考模式参数传递接口"""
        data = request.get_json()
        print("测试接口接收到的完整请求数据:", data)
        print("测试接口原始thinkMode值:", data.get('thinkMode'), "类型:", type(data.get('thinkMode')))
        return json.dumps({"status": "success", "received": data.get('thinkMode')})

    def process_list(self, input_list):
        # 去除重复元素并保持原顺序
        unique_list = []
        seen = set()
        for item in input_list:
            if item not in seen:
                seen.add(item)
                unique_list.append(item)

        # 判断是否需要删除'正常'
        if '正常' in unique_list and len(unique_list) > 1:
            unique_list = [item for item in unique_list if item != '正常']

        return unique_list

    def save_data(self, data, path):
        """将结果数据上传到服务器"""
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(path, data=data, headers=headers)
            print("记录上传成功！" if response.status_code == 200 else f"记录上传失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            print(f"上传记录时发生错误: {str(e)}")

    def convert_avi_to_mp4(self, temp_output):
        """使用 FFmpeg 将 AVI 格式转换为 MP4 格式，并显示转换进度。"""
        ffmpeg_command = f"ffmpeg -i {temp_output} -vcodec libx264 {self.paths['output']} -y"
        process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        total_duration = self.get_video_duration(temp_output)

        for line in process.stderr:
            if "time=" in line:
                try:
                    time_str = line.split("time=")[1].split(" ")[0]
                    h, m, s = map(float, time_str.split(":"))
                    processed_time = h * 3600 + m * 60 + s
                    if total_duration > 0:
                        progress = (processed_time / total_duration) * 100
                        yield progress
                except Exception as e:
                    print(f"解析进度时发生错误: {e}")

        process.wait()
        yield 100

    def get_video_duration(self, path):
        """获取视频总时长（秒）"""
        try:
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                return 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            return total_frames / fps if fps > 0 else 0
        except Exception:
            return 0

    def get_file_names(self, directory):
        """获取指定文件夹中的所有文件名"""
        try:
            return [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
        except Exception as e:
            print(f"发生错误: {e}")
            return []

    def upload(self, out_path):
        """上传处理后的图片或视频文件到远程服务器"""
        upload_url = "http://localhost:9999/files/upload"
        try:
            with open(out_path, 'rb') as file:
                files = {'file': (os.path.basename(out_path), file)}
                response = requests.post(upload_url, files=files)
                if response.status_code == 200:
                    print("文件上传成功！")
                    return response.json()['data']
                else:
                    print("文件上传失败！")
        except Exception as e:
            print(f"上传文件时发生错误: {str(e)}")

    def download(self, url, save_path):
        """下载文件并保存到指定路径"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            print(f"文件已成功下载并保存到 {save_path}")
        except requests.RequestException as e:
            print(f"下载失败: {e}")

    def cleanup_files(self, file_paths):
        """清理文件"""
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

    def cleanup_resources(self, cap, video_writer):
        """释放资源"""
        if cap.isOpened():
            cap.release()
        if video_writer is not None:
            video_writer.release()
        cv2.destroyAllWindows()


# 启动应用
if __name__ == '__main__':
    video_app = VideoProcessingApp()
    video_app.run()
