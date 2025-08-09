# 基于计算机图像分类与大模型反馈的肺炎诊断系统

这是一个结合深度学习图像分类和大模型反馈的智能肺炎诊断系统。系统通过YOLOv8模型进行图像分析，检测肺部X光片或CT图像中的肺炎特征，并利用大型语言模型提供诊断建议和解释。

## 系统架构

本项目采用前后端分离架构，包含三个主要组件：

1. **前端(Vue)**：基于Vue3+TypeScript构建的用户界面，提供图像上传、诊断结果展示和历史记录查询等功能。
2. **后端(SpringBoot)**：负责用户管理、数据存储和请求转发的Java服务。
3. **AI模型服务(Flask)**：运行深度学习模型和大语言模型的Python服务，提供图像分析和智能诊断功能。

## 主要功能

- 肺炎X光片图像分析与诊断
- 肺部CT图像分析与诊断
- 视频流实时分析
- 诊断历史记录管理
- 智能诊断建议生成
- 用户账户管理

## 技术栈

- **前端**：Vue 3、TypeScript、Element Plus
- **后端**：SpringBoot、MyBatis-Plus、MySQL
- **AI服务**：Flask、YOLOv8、大型语言模型API
- **部署**：Docker (可选)

## 快速开始

### 前提条件

- JDK 11+
- Node.js 14+
- Python 3.8+
- MySQL 8.0+
- CUDA支持的GPU (推荐用于模型推理)
- LM-Studio (用于本地部署大模型)

### 数据库配置

1. 创建名为`ai`的数据库
2. 运行`database.sql`脚本初始化数据库结构

### 后端服务启动

1. 进入springboot目录
2. 使用Maven构建项目：`mvn clean package`
3. 运行生成的jar文件：`java -jar target/Kcsj-0.0.1-SNAPSHOT.jar`

### AI服务启动

1. 进入flask目录
2. 安装依赖：`pip install -r requirements.txt`
3. 启动Flask服务：`python main\(YOLO\).py`

### 前端启动

1. 进入vue目录
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm run dev`
4. 构建生产版本：`npm run build`

## 大模型部署与使用

本系统支持多种大模型部署方式，用于生成诊断报告和建议：

### 支持的模型

- **云端API模型**
  - Deepseek-R1
  - Qwen

- **局域网部署模型**
  - Deepseek-R1-LAN
  - Qwen3-LAN
  - Qwen2.5-VL-LAN
  - Qwen2.5-Omni-LAN
  - Gemma3-LAN

- **本地部署模型**
  - Deepseek-R1-Local
  - Qwen3-Local
  - Qwen2.5-VL-Local
  - Qwen2.5-Omni-Local
  - Gemma3-Local

### 使用LM-Studio进行本地部署

1. 下载并安装 [LM-Studio](https://lmstudio.ai/)
2. 从Hugging Face或其他来源下载所需模型（如Deepseek-R1、Qwen等）
3. 在LM-Studio中加载模型
4. 启动本地API服务器（通常在http://localhost:1234）
5. 在诊断系统的设置中选择对应的"本地"模型选项

### 思考模式

系统支持开启思考模式（thinkMode），启用后大模型会提供更详细的分析过程和诊断依据，适合教学和研究使用。

## 系统截图

(此处可以添加系统界面截图)

## 模型信息

### 图像分类模型

本系统使用YOLOv8模型对肺炎影像进行分类和检测。预训练模型存储在`flask/weights/`目录下。

### 大语言模型

支持多种大语言模型，既可以通过API密钥访问云端模型，也可以通过LM-Studio在本地部署运行。系统会根据选定的模型自动配置请求参数。

## 许可证

MIT

## 贡献

欢迎提交问题和贡献代码，请通过创建Issue或Pull Request参与项目开发。

## 致谢

感谢所有为本项目提供支持和贡献的人员。 