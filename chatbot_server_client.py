"""
Chatbot Server Client - A chatbot that can participate in group chats
This integrates the ChatBotClient with the chat server client functionality
"""

import socket
import select
import sys
import json
import threading
import time
from chat_utils import *
import client_state_machine as csm
from chat_bot_client import ChatBotClient


class ChatBotServerClient:
    def __init__(self, name="ChatBot", personality="You are a helpful assistant.", 
                 model="phi3:mini", host='http://localhost:11434'):
        self.name = name
        self.socket = None
        self.state = S_OFFLINE
        self.console_input = []
        self.system_msg = ''
        self.peer = ''
        # Default to college student personality with 20-word limit
        # Can be overridden by passing custom personality
        if personality == "You are a helpful assistant.":
            college_personality = "You are a friendly college student. Reply naturally in less than 20 words like human being. Be casual and helpful."
            self.chatbot = ChatBotClient(name=name, model=model, host=host, personality=college_personality)
        else:
            self.chatbot = ChatBotClient(name=name, model=model, host=host, personality=personality)
        self.group_members = []  # Track group chat participants
        
    def connect(self, server_addr=SERVER):
        """Connect to the chat server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(server_addr)
        print(f"Connected to chat server at {server_addr}")
        
    def login(self):
        """Login to the chat server with bot name"""
        msg = json.dumps({"action": "login", "name": self.name})
        mysend(self.socket, msg)
        response = json.loads(myrecv(self.socket))
        if response["status"] == 'ok':
            self.state = S_LOGGEDIN
            print(f"Logged in as {self.name}")
            return True
        elif response["status"] == 'duplicate':
            print("Name already taken, try another")
            return False
        return False
    
    def get_msgs(self):
        """Check for incoming messages and user input"""
        read_sockets = [self.socket]
        my_msg = ''
        peer_msg = []
        
        # Check for user input
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        
        # Check for socket input
        readable, _, _ = select.select(read_sockets, [], [], 0)
        if self.socket in readable:
            peer_msg = self.recv()
            
        return my_msg, peer_msg
    
    def send(self, msg):
        """Send message to server"""
        mysend(self.socket, msg)
    
    def recv(self):
        """Receive message from server"""
        return myrecv(self.socket)
    
    def read_input(self):
        """Read input from console in a separate thread"""
        while True:
            text = sys.stdin.readline()[:-1]
            if text:
                self.console_input.append(text)
    
    def process_message(self, msg):
        """Process incoming message and generate response if needed"""
        if not msg:
            return
            
        msg_data = json.loads(msg)
        action = msg_data.get("action")
        
        if action == "connect":
            # Someone connected to us or we were added to a group
            from_name = msg_data.get("from", "Unknown")
            if from_name != self.name:
                print(f"\n[{from_name} connected to the chat]")
                self.group_members.append(from_name)
                
        elif action == "exchange":
            # Group message received
            from_name = msg_data.get("from", "Unknown")
            message = msg_data.get("message", "")
            
            print(f"\n[{from_name}]: {message}")
            
            # Check if bot is mentioned with @ prefix
            should_respond = self.should_respond_to(message, from_name)
            
            if should_respond:
                # Extract the actual question (remove @botname)
                actual_message = self.extract_message(message)
                
                # Small delay to simulate thinking (more natural)
                time.sleep(0.5)
                
                # Generate intelligent response using the chatbot
                response = self.chatbot.chat(actual_message)
                
                # Format as natural human response (without [BotName] prefix)
                print(f"\n{self.name}: {response}")
                
                # Send response to the group (without brackets to look more natural)
                self.send_natural_message(response)
                
        elif action == "list":
            # User list response
            results = msg_data.get("results", "")
            print(f"\n{results}")
            
    def should_respond_to(self, message, from_name):
        """Determine if the bot should respond to this message"""
        # Don't respond to own messages
        if from_name == self.name:
            return False
        
        message_lower = message.lower()
        
        # Only respond when bot is mentioned with @ at the front
        # Check for "@chatbot" or "@Assistant" (case insensitive)
        bot_mention = f"@{self.name.lower()}"
        
        if message_lower.strip().startswith(bot_mention):
            return True
        
        # Also check if bot name appears after @ anywhere in the message
        if "@" in message:
            # Extract the mentioned username (simple check)
            parts = message.split("@")
            for part in parts[1:]:  # Skip first part (before first @)
                mentioned_name = part.split()[0].lower() if part.split() else ""
                if mentioned_name == self.name.lower():
                    return True
                
        return False
    
    def extract_message(self, message):
        """Extract the actual message after removing @botname mention"""
        message_lower = message.lower()
        bot_mention = f"@{self.name.lower()}"
        
        # Remove @botname from the beginning
        if message_lower.strip().startswith(bot_mention):
            return message[len(f"@{self.name}"):].strip()
        
        # Remove @botname from anywhere in the message
        if "@" in message:
            parts = message.split("@")
            for part in parts[1:]:  # Skip first part (before first @)
                mentioned_name = part.split()[0].lower() if part.split() else ""
                if mentioned_name == self.name.lower():
                    # Remove this @mention
                    idx = message.find("@" + part.split()[0])
                    if idx >= 0:
                        message = message[:idx] + message[idx + len(self.name) + 1:]
            return message.strip()
        
        return message
    
    def send_group_message(self, message):
        """Send a message to the group chat (with brackets)"""
        msg = json.dumps({
            "action": "exchange", 
            "from": f"[{self.name}]", 
            "message": message
        })
        self.send(msg)
    
    def send_natural_message(self, message):
        """Send a message to the group chat without brackets (more natural)"""
        msg = json.dumps({
            "action": "exchange", 
            "from": self.name, 
            "message": message
        })
        self.send(msg)
    
    def connect_to_user(self, user_name):
        """Connect to a specific user to start a chat"""
        msg = json.dumps({"action": "connect", "target": user_name})
        self.send(msg)
        response = json.loads(self.recv())
        if response["status"] == "success":
            print(f"Connected to {user_name}")
            return True
        return False
    
    def list_users(self):
        """List all available users"""
        msg = json.dumps({"action": "list"})
        self.send(msg)
        response = json.loads(self.recv())
        return response.get("results", "")
    
    def run(self):
        """Main run loop"""
        # Connect and login
        self.connect()
        if not self.login():
            print("Failed to login")
            return
        
        # Start input thread
        input_thread = threading.Thread(target=self.read_input)
        input_thread.daemon = True
        input_thread.start()
        
        print("\n=== Chatbot is ready! ===")
        print("Commands:")
        print("  who - List all users")
        print("  c <username> - Connect to a user")
        print("  exit - Quit")
        print("========================\n")
        
        while self.state != S_OFFLINE:
            my_msg, peer_msg = self.get_msgs()
            
            # Process user input
            if my_msg:
                if my_msg == "exit":
                    msg = json.dumps({"action": "disconnect"})
                    self.send(msg)
                    self.state = S_OFFLINE
                    break
                elif my_msg == "who":
                    print(self.list_users())
                elif my_msg.startswith("c "):
                    # Connect to user
                    target = my_msg[2:].strip()
                    self.connect_to_user(target)
                else:
                    # Send regular message
                    msg = json.dumps({
                        "action": "exchange", 
                        "from": f"[{self.name}]", 
                        "message": my_msg
                    })
                    self.send(msg)
            
            # Process peer messages
            if peer_msg:
                self.process_message(peer_msg)
            
            time.sleep(0.1)
        
        if self.socket:
            self.socket.close()
        print("Disconnected from server")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Chatbot that participates in group chats')
    parser.add_argument('--name', default='ChatBot', help='Bot name')
    parser.add_argument('--personality', default='You are a helpful assistant.', help='Bot personality')
    parser.add_argument('--model', default='phi3:mini', help='Model to use')
    parser.add_argument('--host', default='http://localhost:11434', help='Ollama host')
    parser.add_argument('--server', default=None, help='Server address (host:port)')
    
    args = parser.parse_args()
    
    # Parse server address if provided
    server = SERVER
    if args.server:
        host, port = args.server.split(':')
        server = (host, int(port))
    
    # Create and run the chatbot
    bot = ChatBotServerClient(
        name=args.name,
        personality=args.personality,
        model=args.model,
        host=args.host
    )
    bot.run()


if __name__ == "__main__":
    main()