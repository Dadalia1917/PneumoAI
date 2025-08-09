import json
import requests
from openai import OpenAI


class ChatAPI:
    def __init__(self, deepseek_api_key=None, qwen_api_key=None):
        if deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
        if qwen_api_key:
            self.qwen_headers = {
                "Authorization": f"Bearer {qwen_api_key}",
                "Content-Type": "application/json"
            }
            self.qwen_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        # 局域网配置
        self.lan_url = "http://192.168.1.108:1234/v1/chat/completions"
        
        # 本地配置
        self.local_url = "http://127.0.0.1:1234/v1/chat/completions"

    def deepseek_request(self, messages, model="deepseek-chat", stream=False):
        """DeepSeek API请求方法"""
        response = self.deepseek_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream
        )
        return response.choices[0].message.content

    def qwen_request(self, messages, model="Qwen/Qwen2.5-14B-Instruct",
                     max_tokens=512, temperature=0.7):
        """Qwen API请求方法"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "response_format": {"type": "text"}
        }

        try:
            response = requests.post(
                self.qwen_url,
                json=payload,
                headers=self.qwen_headers
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Qwen API请求错误: {str(e)}")
            return "Qwen API请求失败"

    def lan_deepseek_request(self, messages):
        """局域网Deepseek-R1请求方法"""
        try:
            print(f"正在向局域网Deepseek-R1模型发送请求...")
            
            response = requests.post(
                f"{self.lan_url}",
                json={
                    "model": "deepseek/deepseek-r1-0528-qwen3-8b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"局域网Deepseek-R1请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "Deepseek-R1离线不可用，请检查局域网服务是否正常运行"
                
            result = response.json()
            print(f"收到局域网Deepseek-R1模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"Deepseek-R1模型错误: {result}")
                return "Deepseek-R1模型未找到，请先在服务器上加载deepseek-r1-0528-qwen3-8b模型"
            else:
                print(f"Deepseek-R1响应格式错误: {result}")
                return "Deepseek-R1响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("局域网Deepseek-R1请求超时")
            return "Deepseek-R1请求超时，请检查局域网服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到局域网Deepseek-R1服务")
            return "Deepseek-R1离线不可用，请检查局域网服务是否正常运行"
        except Exception as e:
            print(f"局域网Deepseek-R1请求失败: {e}")
            return "Deepseek-R1离线不可用，请检查局域网服务是否正常运行"

    def local_deepseek_request(self, messages):
        """使用本地部署的Deepseek-R1模型"""
        try:
            print(f"正在向本地Deepseek-R1模型发送请求...")
            
            response = requests.post(
                f"{self.local_url}",
                json={
                    "model": "deepseek/deepseek-r1-0528-qwen3-8b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"本地Deepseek-R1请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "Deepseek-R1离线不可用，请检查本地服务是否正常运行"
                
            result = response.json()
            print(f"收到本地Deepseek-R1模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"Deepseek-R1模型错误: {result}")
                return "Deepseek-R1模型未找到，请先在LM-Studio中加载deepseek-r1-0528-qwen3-8b模型"
            else:
                print(f"本地Deepseek-R1响应格式错误: {result}")
                return "Deepseek-R1响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("本地Deepseek-R1请求超时")
            return "Deepseek-R1请求超时，请检查本地服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到本地Deepseek-R1服务")
            return "Deepseek-R1离线不可用，请检查本地服务是否正常运行"
        except Exception as e:
            print(f"本地Deepseek-R1请求失败: {e}")
            return "Deepseek-R1离线不可用，请检查本地服务是否正常运行"

    def local_gemma_request(self, messages):
        """使用本地部署的Gemma3模型"""
        try:
            # 将messages格式转换为OpenAI格式
            print(f"正在向本地Gemma模型发送请求...")
            
            response = requests.post(
                f"{self.local_url}",
                json={
                    "model": "google/gemma-3-4b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"Gemma3请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "Gemma3离线不可用，请检查LM-Studio服务是否正常运行"
                
            result = response.json()
            print(f"收到Gemma模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"Gemma3模型错误: {result}")
                return "Gemma3模型未找到，请先在LM-Studio中加载gemma-3-4b-it模型"
            else:
                print(f"Gemma3响应格式错误: {result}")
                return "Gemma3响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("Gemma3请求超时")
            return "Gemma3请求超时，请检查LM-Studio服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到LM-Studio服务")
            return "Gemma3离线不可用，请检查LM-Studio服务是否正常运行"
        except Exception as e:
            print(f"本地Gemma3请求失败: {e}")
            return "Gemma3离线不可用，请检查LM-Studio服务是否正常运行"

    def lan_gemma_request(self, messages):
        """使用局域网部署的Gemma3模型"""
        try:
            print(f"正在向局域网Gemma模型发送请求...")
            
            response = requests.post(
                f"{self.lan_url}",
                json={
                    "model": "google/gemma-3-4b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"局域网Gemma3请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "Gemma3离线不可用，请检查局域网服务是否正常运行"
                
            result = response.json()
            print(f"收到局域网Gemma模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"Gemma3模型错误: {result}")
                return "Gemma3模型未找到，请先在服务器上加载gemma-3-4b-it模型"
            else:
                print(f"Gemma3响应格式错误: {result}")
                return "Gemma3响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("局域网Gemma3请求超时")
            return "Gemma3请求超时，请检查局域网服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到局域网Gemma3服务")
            return "Gemma3离线不可用，请检查局域网服务是否正常运行"
        except Exception as e:
            print(f"局域网Gemma3请求失败: {e}")
            return "Gemma3离线不可用，请检查局域网服务是否正常运行"

    def local_qwen3_request(self, messages, think_mode=False):
        """使用本地部署的qwen3.0模型"""
        try:
            # 处理思考模式
            if think_mode:
                system_message = {"role": "system", "content": "请深入思考问题，提供详尽的分析和解答。"}
                messages = [system_message] + messages
            
            print(f"正在向本地qwen3.0模型发送请求...")
            
            response = requests.post(
                f"{self.local_url}",
                json={
                    "model": "qwen/qwen3-4b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"qwen3.0请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen3.0离线不可用，请检查LM-Studio服务是否正常运行"
                
            result = response.json()
            print(f"收到qwen3.0模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen3.0模型错误: {result}")
                return "qwen3.0模型未找到，请先在LM-Studio中加载qwen3-4b模型"
            else:
                print(f"qwen3.0响应格式错误: {result}")
                return "qwen3.0响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("qwen3.0请求超时")
            return "qwen3.0请求超时，请检查LM-Studio服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到LM-Studio服务")
            return "qwen3.0离线不可用，请检查LM-Studio服务是否正常运行"
        except Exception as e:
            print(f"本地qwen3.0请求失败: {e}")
            return "qwen3.0离线不可用，请检查LM-Studio服务是否正常运行"

    def lan_qwen3_request(self, messages, think_mode=False):
        """使用局域网部署的qwen3.0模型"""
        try:
            # 处理思考模式
            if think_mode:
                system_message = {"role": "system", "content": "请深入思考问题，提供详尽的分析和解答。"}
                messages = [system_message] + messages
            
            print(f"正在向局域网qwen3.0模型发送请求...")
            
            response = requests.post(
                f"{self.lan_url}",
                json={
                    "model": "qwen/qwen3-4b",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"局域网qwen3.0请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen3.0离线不可用，请检查局域网服务是否正常运行"
                
            result = response.json()
            print(f"收到局域网qwen3.0模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen3.0模型错误: {result}")
                return "qwen3.0模型未找到，请先在服务器上加载qwen3-4b模型"
            else:
                print(f"qwen3.0响应格式错误: {result}")
                return "qwen3.0响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("局域网qwen3.0请求超时")
            return "qwen3.0请求超时，请检查局域网服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到局域网qwen3.0服务")
            return "qwen3.0离线不可用，请检查局域网服务是否正常运行"
        except Exception as e:
            print(f"局域网qwen3.0请求失败: {e}")
            return "qwen3.0离线不可用，请检查局域网服务是否正常运行"

    def local_qwen25vl_request(self, messages):
        """使用本地部署的qwen2.5-VL模型"""
        try:
            print(f"正在向本地qwen2.5-VL模型发送请求...")
            
            response = requests.post(
                f"{self.local_url}",
                json={
                    "model": "qwen2.5-vl-3b-instruct",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"qwen2.5-VL请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen2.5-VL离线不可用，请检查LM-Studio服务是否正常运行"
                
            result = response.json()
            print(f"收到qwen2.5-VL模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen2.5-VL模型错误: {result}")
                return "qwen2.5-VL模型未找到，请先在LM-Studio中加载qwen2.5-vl-3b-instruct模型"
            else:
                print(f"qwen2.5-VL响应格式错误: {result}")
                return "qwen2.5-VL响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("qwen2.5-VL请求超时")
            return "qwen2.5-VL请求超时，请检查LM-Studio服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到LM-Studio服务")
            return "qwen2.5-VL离线不可用，请检查LM-Studio服务是否正常运行"
        except Exception as e:
            print(f"本地qwen2.5-VL请求失败: {e}")
            return "qwen2.5-VL离线不可用，请检查LM-Studio服务是否正常运行"

    def lan_qwen25vl_request(self, messages):
        """使用局域网部署的qwen2.5-VL模型"""
        try:
            print(f"正在向局域网qwen2.5-VL模型发送请求...")
            
            response = requests.post(
                f"{self.lan_url}",
                json={
                    "model": "qwen2.5-vl-3b-instruct",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"局域网qwen2.5-VL请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen2.5-VL离线不可用，请检查局域网服务是否正常运行"
                
            result = response.json()
            print(f"收到局域网qwen2.5-VL模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen2.5-VL模型错误: {result}")
                return "qwen2.5-VL模型未找到，请先在服务器上加载qwen2.5-vl-3b-instruct模型"
            else:
                print(f"qwen2.5-VL响应格式错误: {result}")
                return "qwen2.5-VL响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("局域网qwen2.5-VL请求超时")
            return "qwen2.5-VL请求超时，请检查局域网服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到局域网qwen2.5-VL服务")
            return "qwen2.5-VL离线不可用，请检查局域网服务是否正常运行"
        except Exception as e:
            print(f"局域网qwen2.5-VL请求失败: {e}")
            return "qwen2.5-VL离线不可用，请检查局域网服务是否正常运行"

    def local_qwen25omni_request(self, messages):
        """使用本地部署的qwen2.5-Omni模型"""
        try:
            print(f"正在向本地qwen2.5-Omni模型发送请求...")
            
            response = requests.post(
                f"{self.local_url}",
                json={
                    "model": "qwen2.5-omni-instruct",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"qwen2.5-Omni请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen2.5-Omni离线不可用，请检查LM-Studio服务是否正常运行"
                
            result = response.json()
            print(f"收到qwen2.5-Omni模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen2.5-Omni模型错误: {result}")
                return "qwen2.5-Omni模型未找到，请先在LM-Studio中加载qwen2.5-omni-instruct模型"
            else:
                print(f"qwen2.5-Omni响应格式错误: {result}")
                return "qwen2.5-Omni响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("qwen2.5-Omni请求超时")
            return "qwen2.5-Omni请求超时，请检查LM-Studio服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到LM-Studio服务")
            return "qwen2.5-Omni离线不可用，请检查LM-Studio服务是否正常运行"
        except Exception as e:
            print(f"本地qwen2.5-Omni请求失败: {e}")
            return "qwen2.5-Omni离线不可用，请检查LM-Studio服务是否正常运行"

    def lan_qwen25omni_request(self, messages):
        """使用局域网部署的qwen2.5-Omni模型"""
        try:
            print(f"正在向局域网qwen2.5-Omni模型发送请求...")
            
            response = requests.post(
                f"{self.lan_url}",
                json={
                    "model": "qwen2.5-omni-instruct",
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=300
            )
            
            if response.status_code != 200:
                print(f"局域网qwen2.5-Omni请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return "qwen2.5-Omni离线不可用，请检查局域网服务是否正常运行"
                
            result = response.json()
            print(f"收到局域网qwen2.5-Omni模型响应: {str(result)[:100]}...")
            
            if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                return result['choices'][0]['message']['content']
            elif 'error' in result:
                print(f"qwen2.5-Omni模型错误: {result}")
                return "qwen2.5-Omni模型未找到，请先在服务器上加载qwen2.5-omni-instruct模型"
            else:
                print(f"qwen2.5-Omni响应格式错误: {result}")
                return "qwen2.5-Omni响应格式错误，请检查模型输出"
        except requests.Timeout:
            print("局域网qwen2.5-Omni请求超时")
            return "qwen2.5-Omni请求超时，请检查局域网服务是否正常运行"
        except requests.ConnectionError:
            print("无法连接到局域网qwen2.5-Omni服务")
            return "qwen2.5-Omni离线不可用，请检查局域网服务是否正常运行"
        except Exception as e:
            print(f"局域网qwen2.5-Omni请求失败: {e}")
            return "qwen2.5-Omni离线不可用，请检查局域网服务是否正常运行"


# 使用示例
if __name__ == "__main__":
    # 初始化实例
    chat = ChatAPI()

    # 构造通用消息
    messages = [
        {"role": "user", "content": "我用RT-DETR检测出学生上课玩手机。请生成实质性建议，包括如何改善课堂纪律、提高学生专注度等"}
    ]

    # 调用本地Deepseek-R1
    print("本地Deepseek-R1响应:")
    print(chat.local_deepseek_request(messages))

    # 调用局域网Deepseek-R1
    print("\n局域网Deepseek-R1响应:")
    print(chat.lan_deepseek_request(messages))

    # 调用本地Gemma3
    print("\n本地Gemma3响应:")
    print(chat.local_gemma_request(messages))

    # 调用局域网Gemma3
    print("\n局域网Gemma3响应:")
    print(chat.lan_gemma_request(messages))

    # 调用本地qwen3.0
    print("\n本地qwen3.0响应:")
    print(chat.local_qwen3_request(messages))

    # 调用局域网qwen3.0
    print("\n局域网qwen3.0响应:")
    print(chat.lan_qwen3_request(messages))
    
    # 调用本地qwen2.5-VL
    print("\n本地qwen2.5-VL响应:")
    print(chat.local_qwen25vl_request(messages))
    
    # 调用局域网qwen2.5-VL
    print("\n局域网qwen2.5-VL响应:")
    print(chat.lan_qwen25vl_request(messages))
    
    # 调用本地qwen2.5-Omni
    print("\n本地qwen2.5-Omni响应:")
    print(chat.local_qwen25omni_request(messages))
    
    # 调用局域网qwen2.5-Omni
    print("\n局域网qwen2.5-Omni响应:")
    print(chat.lan_qwen25omni_request(messages))
