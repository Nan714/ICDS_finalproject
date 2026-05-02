#!/usr/bin/env python3
"""
Demo script showing the chatbot participating in group chats.

This demonstrates:
1. Starting a chatbot that connects to the chat server
2. The chatbot responding when mentioned in group chats
3. Natural integration into multi-client conversations

Usage:
    1. Start the chat server: python chat_server.py
    2. Start regular clients: python chat_client_class.py (in separate terminals)
    3. Start the chatbot: python chatbot_server_client.py --name "Assistant"
    4. Have clients connect to each other and the chatbot will respond naturally
"""

import subprocess
import time
import sys


def print_demo_header():
    print("=" * 60)
    print("Chatbot Group Chat Participation Demo")
    print("=" * 60)
    print()
    print("This demo shows how the chatbot can participate in group chats.")
    print()
    print("Setup steps:")
    print("1. Terminal 1: python chat_server.py")
    print("2. Terminal 2: python chat_client_class.py (as 'Alice')")
    print("3. Terminal 3: python chat_client_class.py (as 'Bob')")
    print("4. Terminal 4: python chatbot_server_client.py --name 'Assistant'")
    print()
    print("Then in Alice's terminal:")
    print("  - Type 'who' to see all users")
    print("  - Type 'c Bob' to connect to Bob")
    print("  - Type 'c Assistant' to add the chatbot to the group")
    print()
    print("The chatbot will respond when:")
    print("  - Someone mentions 'Assistant'")
    print("  - Someone asks a question (?)")
    print("  - It's a group conversation (occasionally)")
    print("=" * 60)
    print()


def print_conversation_example():
    print("\nExample conversation:")
    print("-" * 40)
    print("Alice: who")
    print("Server: Users: {'Alice': 0, 'Bob': 0, 'Assistant': 0}")
    print()
    print("Alice: c Bob")
    print("Server: Connected to Bob")
    print()
    print("Alice: c Assistant")
    print("Server: Assistant added to group")
    print()
    print("Alice: Hello everyone! How are you?")
    print("Bob: I'm good, thanks!")
    print("[Assistant]: Hi Alice! I'm doing well. How can I help you today?")
    print()
    print("Alice: @Assistant can you help me with Python?")
    print("[Assistant]: Of course! What would you like to know about Python?")
    print("-" * 40)


def main():
    print_demo_header()
    
    # Ask user if they want to see example conversation
    response = input("Would you like to see an example conversation? (y/n): ")
    if response.lower() == 'y':
        print_conversation_example()
    
    print("\nTo get started:")
    print("1. First start the chat server:")
    print("   python chat_server.py")
    print()
    print("2. In another terminal, start a regular client:")
    print("   python chat_client_class.py")
    print("   (enter your name when prompted)")
    print()
    print("3. In another terminal, start the chatbot:")
    print("   python chatbot_server_client.py --name 'Assistant'")
    print()
    print("4. Have the regular clients connect to each other and the chatbot")
    print("   using the 'c <username>' command")
    print()
    print("The chatbot will automatically respond in group conversations!")


if __name__ == "__main__":
    main()