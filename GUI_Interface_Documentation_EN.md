# Chat System GUI Interface Documentation

## Overview

This is a multi-client chat system that supports text chat, group chat, and AI chatbots. The GUI needs to interact with the core chat client classes to provide a user interface.

## Core Components

### 1. Client Class (chat_client_class.py)

The main chat client class that handles network connections, message sending/receiving, and state management.

#### Initialization
```python
client = Client(args)
```

#### Main Methods

##### Connection and Login
- `init_chat()`: Initialize chat connection
- `login()`: Login to server
- `run_chat()`: Start chat loop

##### Message Handling
- `get_msgs()`: Get new messages
  - Returns: `(my_msg, peer_msg)` - user input and peer messages
- `send(msg)`: Send message
- `recv()`: Receive message

##### State Management
- `get_name()`: Get username
- `quit()`: Quit chat

### 2. ClientSM Class (client_state_machine.py)

Client state machine that manages chat states and command processing.

#### State Constants
- `S_OFFLINE = 0`: Offline
- `S_CONNECTED = 1`: Connected
- `S_LOGGEDIN = 2`: Logged in
- `S_CHATTING = 3`: Chatting

#### Main Methods
- `connect_to(peer)`: Connect to peer
- `disconnect()`: Disconnect
- `proc(my_msg, peer_msg)`: Process messages and commands

### 3. ChatBotServerClient Class (chatbot_server_client.py)

AI chatbot client that supports group chat participation.

#### Initialization
```python
bot = ChatBotServerClient(name="BotName", personality="...", model="phi3:mini")
```

#### Main Methods
- `connect(server_addr)`: Connect to server
- `login()`: Login bot
- `run()`: Start bot
- `send_group_message(message)`: Send group message

## Message Format

### Client to Server Messages

All messages are in JSON format:

```json
{
  "action": "action_type",
  "target": "target_name",  // optional
  "message": "message_text", // optional
  "name": "user_name"       // optional
}
```

#### Action Types
- `"login"`: Login
- `"connect"`: Connect to user
- `"exchange"`: Send message
- `"disconnect"`: Disconnect
- `"list"`: Get user list
- `"time"`: Get server time
- `"search"`: Search chat logs
- `"poem"`: Get poem

### Server to Client Messages

```json
{
  "action": "action_type",
  "status": "status_code",    // optional
  "from": "sender_name",      // optional
  "message": "message_text",  // optional
  "results": "result_data"    // optional
}
```

## GUI Integration Guide

### 1. Initialize Client

```python
from chat_client_class import Client
import argparse

# Create args object
args = argparse.Namespace()
args.d = None  # Use default server

# Initialize client
client = Client(args)
client.init_chat()

# Login
while not client.login():
    # Handle login failure
    pass
```

### 2. Message Loop

```python
import threading
import time

def message_loop():
    while client.sm.get_state() != S_OFFLINE:
        my_msg, peer_msg = client.get_msgs()

        # Handle user input
        if my_msg:
            # Send message or process command
            if my_msg.startswith('c '):
                peer = my_msg[2:]
                client.sm.connect_to(peer)
            elif my_msg == 'who':
                # Get user list
                pass
            else:
                # Send regular message
                pass

        # Handle received messages
        if peer_msg:
            data = json.loads(peer_msg)
            if data['action'] == 'exchange':
                # Display message
                sender = data['from']
                message = data['message']
                # Update GUI
            elif data['action'] == 'connect':
                # Handle connect event
                pass

# Start message loop thread
threading.Thread(target=message_loop, daemon=True).start()
```

### 3. State Monitoring

```python
def get_current_state():
    return client.sm.get_state()

def get_current_peer():
    return client.sm.peer

def get_my_name():
    return client.sm.get_myname()
```

### 4. Send Messages

```python
def send_message(message):
    if client.sm.get_state() == S_CHATTING:
        # Send to current chat
        msg = json.dumps({
            "action": "exchange",
            "from": f"[{client.sm.get_myname()}]",
            "message": message
        })
        client.send(msg)
    else:
        # Handle error: not in chatting state
        pass

def connect_to_user(username):
    client.sm.connect_to(username)

def disconnect():
    client.sm.disconnect()
```

### 5. Command Processing

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

## Event Handling

### Message Events
- **New message**: `action: "exchange"`
- **User joined**: `action: "connect", status: "request"`
- **User left**: `action: "disconnect"`
- **User list**: `action: "list"`

### State Change Events
- Login success: `state = S_LOGGEDIN`
- Start chatting: `state = S_CHATTING`
- Disconnect: `state = S_LOGGEDIN`

## Error Handling

### Common Errors
- Connection failed: Check if server is running
- Login failed: Username duplicate or other error
- Send failed: Network error or state error

### Exception Handling
```python
try:
    client.send(msg)
except Exception as e:
    # Handle send error
    print(f"Send error: {e}")

try:
    response = client.recv()
    data = json.loads(response)
except json.JSONDecodeError:
    # Handle invalid JSON
    pass
except Exception as e:
    # Handle receive error
    print(f"Receive error: {e}")
```

## Sample GUI Code

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

        # User list
        self.user_list = tk.Listbox(self.root)
        self.user_list.pack(side=tk.LEFT, fill=tk.Y)

        # Chat area
        self.chat_area = tk.Text(self.root)
        self.chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.input_field = tk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def connect_to_server(self):
        # Initialize client
        args = argparse.Namespace()
        args.d = None
        self.client = Client(args)
        self.client.init_chat()

        # Start message handling thread
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

## Important Notes

1. **Thread Safety**: GUI updates must be done in the main thread
2. **State Synchronization**: Check client state regularly
3. **Error Handling**: Handle network errors and exceptions
4. **Resource Cleanup**: Properly close connections on exit
5. **Message Format**: Ensure message format matches protocol requirements

## Dependencies

- Python 3.x
- socket
- select
- json
- threading
- tkinter (for GUI example)</content>
<parameter name="filePath">/Users/nanwang1/Downloads/Chat_System_Full/GUI_Interface_Documentation.md