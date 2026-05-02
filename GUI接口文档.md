# 聊天系统GUI接口文档

## 概述

这是一个多客户端聊天系统，支持文本聊天、群聊和AI聊天机器人。GUI需要与核心聊天客户端类交互来提供用户界面。

## 核心组件

### 1. Client 类 (chat_client_class.py)

主要的聊天客户端类，处理网络连接、消息收发和状态管理。

#### 初始化
```python
client = Client(args)
```

#### 主要方法

##### 连接和登录
- `init_chat()`: 初始化聊天连接
- `login()`: 登录到服务器
- `run_chat()`: 启动聊天循环

##### 消息处理
- `get_msgs()`: 获取新消息
  - 返回: `(my_msg, peer_msg)` - 用户输入和对等方消息
- `send(msg)`: 发送消息
- `recv()`: 接收消息

##### 状态管理
- `get_name()`: 获取用户名
- `quit()`: 退出聊天

### 2. ClientSM 类 (client_state_machine.py)

客户端状态机，管理聊天状态和命令处理。

#### 状态常量
- `S_OFFLINE = 0`: 离线
- `S_CONNECTED = 1`: 已连接
- `S_LOGGEDIN = 2`: 已登录
- `S_CHATTING = 3`: 聊天中

#### 主要方法
- `connect_to(peer)`: 连接到对等方
- `disconnect()`: 断开连接
- `proc(my_msg, peer_msg)`: 处理消息和命令

### 3. ChatBotServerClient 类 (chatbot_server_client.py)

AI聊天机器人客户端，支持群聊参与。

#### 初始化
```python
bot = ChatBotServerClient(name="BotName", personality="...", model="phi3:mini")
```

#### 主要方法
- `connect(server_addr)`: 连接到服务器
- `login()`: 登录机器人
- `run()`: 启动机器人
- `send_group_message(message)`: 发送群聊消息

## 消息格式

### 客户端到服务器消息

所有消息都是JSON格式：

```json
{
  "action": "action_type",
  "target": "target_name",  // 可选
  "message": "message_text", // 可选
  "name": "user_name"       // 可选
}
```

#### Action类型
- `"login"`: 登录
- `"connect"`: 连接到用户
- `"exchange"`: 发送消息
- `"disconnect"`: 断开连接
- `"list"`: 获取用户列表
- `"time"`: 获取服务器时间
- `"search"`: 搜索聊天记录
- `"poem"`: 获取诗歌

### 服务器到客户端消息

```json
{
  "action": "action_type",
  "status": "status_code",    // 可选
  "from": "sender_name",      // 可选
  "message": "message_text",  // 可选
  "results": "result_data"    // 可选
}
```

## GUI集成指南

### 1. 初始化客户端

```python
from chat_client_class import Client
import argparse

# 创建参数对象
args = argparse.Namespace()
args.d = None  # 使用默认服务器

# 初始化客户端
client = Client(args)
client.init_chat()

# 登录
while not client.login():
    # 处理登录失败
    pass
```

### 2. 消息循环

```python
import threading
import time

def message_loop():
    while client.sm.get_state() != S_OFFLINE:
        my_msg, peer_msg = client.get_msgs()

        # 处理用户输入
        if my_msg:
            # 发送消息或处理命令
            if my_msg.startswith('c '):
                peer = my_msg[2:]
                client.sm.connect_to(peer)
            elif my_msg == 'who':
                # 获取用户列表
                pass
            else:
                # 发送普通消息
                pass

        # 处理接收到的消息
        if peer_msg:
            data = json.loads(peer_msg)
            if data['action'] == 'exchange':
                # 显示消息
                sender = data['from']
                message = data['message']
                # 更新GUI
            elif data['action'] == 'connect':
                # 处理连接事件
                pass

# 启动消息循环线程
threading.Thread(target=message_loop, daemon=True).start()
```

### 3. 状态监听

```python
def get_current_state():
    return client.sm.get_state()

def get_current_peer():
    return client.sm.peer

def get_my_name():
    return client.sm.get_myname()
```

### 4. 发送消息

```python
def send_message(message):
    if client.sm.get_state() == S_CHATTING:
        # 发送到当前聊天
        msg = json.dumps({
            "action": "exchange",
            "from": f"[{client.sm.get_myname()}]",
            "message": message
        })
        client.send(msg)
    else:
        # 处理错误：未在聊天状态
        pass

def connect_to_user(username):
    client.sm.connect_to(username)

def disconnect():
    client.sm.disconnect()
```

### 5. 命令处理

```python
def process_command(command):
    if command == 'who':
        msg = json.dumps({"action": "list"})
        client.send(msg)
        response = json.loads(client.recv())
        return response.get('results', '')
    elif command == 'time':
        msg = json.dumps({"action": "time"})
        client.send(msg)
        response = json.loads(client.recv())
        return response.get('results', '')
    elif command.startswith('?'):
        term = command[1:]
        msg = json.dumps({"action": "search", "target": term})
        client.send(msg)
        response = json.loads(client.recv())
        return response.get('results', '')
    elif command.startswith('p'):
        poem_num = command[1:]
        msg = json.dumps({"action": "poem", "target": poem_num})
        client.send(msg)
        response = json.loads(client.recv())
        return response.get('results', '')
```

## 事件处理

### 消息事件
- **新消息**: `action: "exchange"`
- **用户加入**: `action: "connect", status: "request"`
- **用户离开**: `action: "disconnect"`
- **用户列表**: `action: "list"`

### 状态变化事件
- 登录成功: `state = S_LOGGEDIN`
- 开始聊天: `state = S_CHATTING`
- 断开连接: `state = S_LOGGEDIN`

## 错误处理

### 常见错误
- 连接失败: 检查服务器是否运行
- 登录失败: 用户名重复或其他错误
- 发送失败: 网络错误或状态错误

### 异常处理
```python
try:
    client.send(msg)
except Exception as e:
    # 处理发送错误
    print(f"Send error: {e}")

try:
    response = client.recv()
    data = json.loads(response)
except json.JSONDecodeError:
    # 处理无效JSON
    pass
except Exception as e:
    # 处理接收错误
    print(f"Receive error: {e}")
```

## 示例GUI代码

```python
import tkinter as tk
from chat_client_class import Client
import json
import threading

class ChatGUI:
    def __init__(self):
        self.client = None
        self.setup_gui()
        self.connect_to_server()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Chat Client")

        # 用户列表
        self.user_list = tk.Listbox(self.root)
        self.user_list.pack(side=tk.LEFT, fill=tk.Y)

        # 聊天区域
        self.chat_area = tk.Text(self.root)
        self.chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 输入区域
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.input_field = tk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def connect_to_server(self):
        # 初始化客户端
        args = argparse.Namespace()
        args.d = None
        self.client = Client(args)
        self.client.init_chat()

        # 启动消息处理线程
        threading.Thread(target=self.message_loop, daemon=True).start()

    def message_loop(self):
        while self.client.sm.get_state() != S_OFFLINE:
            my_msg, peer_msg = self.client.get_msgs()

            if peer_msg:
                self.handle_message(peer_msg)

            time.sleep(0.1)

    def handle_message(self, msg):
        try:
            data = json.loads(msg)
            if data['action'] == 'exchange':
                sender = data['from']
                message = data['message']
                self.chat_area.insert(tk.END, f"{sender}: {message}\n")
                self.chat_area.see(tk.END)
        except:
            pass

    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            if self.client.sm.get_state() == S_CHATTING:
                msg = json.dumps({
                    "action": "exchange",
                    "from": f"[{self.client.sm.get_myname()}]",
                    "message": message
                })
                self.client.send(msg)
                self.chat_area.insert(tk.END, f"You: {message}\n")
                self.chat_area.see(tk.END)

if __name__ == "__main__":
    gui = ChatGUI()
    gui.root.mainloop()
```

## 注意事项

1. **线程安全**: GUI更新需要在主线程中进行
2. **状态同步**: 定期检查客户端状态
3. **错误处理**: 处理网络错误和异常情况
4. **资源清理**: 退出时正确关闭连接
5. **消息格式**: 确保消息格式符合协议要求

## 依赖项

- Python 3.x
- socket
- select
- json
- threading
- tkinter (用于GUI示例)</content>
<parameter name="filePath">/Users/nanwang1/Downloads/Chat_System_Full/GUI_Interface_Documentation.md