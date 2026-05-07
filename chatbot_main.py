#!/usr/bin/env python3
"""
Main entry point for the chatbot.
Supports both standalone mode and server-connected group chat mode.
"""

import sys
import argparse

# Check for command line arguments to determine mode
def main():
    parser = argparse.ArgumentParser(description='Chatbot with group chat support')
    parser.add_argument('--mode', choices=['standalone', 'server'], default='standalone',
                        help='Run in standalone mode or connect to chat server')
    parser.add_argument('--name', default='ChatBot', help='Bot name (server mode)')
    parser.add_argument('--personality', default='You are a helpful assistant.', help='Bot personality')
    parser.add_argument('--model', default='phi3:mini', help='Model to use')
    parser.add_argument('--host', default='http://localhost:11434', help='Ollama host')
    parser.add_argument('--server', default=None, help='Server address (host:port)')
    
    args, unknown = parser.parse_known_args()
    
    if args.mode == 'server':
        # Server mode - participate in group chats
        from chatbot_server_client import ChatBotServerClient
        
        server = None
        if args.server:
            host, port = args.server.split(':')
            server = (host, int(port))
        
        bot = ChatBotServerClient(
            name=args.name,
            personality=args.personality,
            model=args.model,
            host=args.host
        )
        bot.connect(server)
        bot.login()
        bot.run()
    else:
        # Standalone mode - simple chatbot interaction
        from chat_bot_client import ChatBotClient
        
        # Get personality from remaining args or use default
        personality = "You are a helpful assistant."
        if unknown:
            personality = " ".join(unknown)
        
        bot = ChatBotClient(personality=personality, model=args.model, host=args.host)
        
        print("Chatbot is ready! You can start chatting with it. Type 'exit' to quit.")
        
        while True:
            input_message = input("You: ")
            if input_message.lower() == 'exit':
                break
            reply = bot.chat(input_message)
            print("chatbot:", reply)


if __name__ == "__main__":
    main()
