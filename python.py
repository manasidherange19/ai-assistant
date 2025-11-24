# voice_ai_assistant_web.py
import speech_recognition as sr
import pyttsx3
import whisper
import requests
import webbrowser
import json
import os
import threading
import re
import time
import random
from datetime import datetime
from urllib.parse import quote
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS

class FreeVoiceAIAssistant:
    def __init__(self):
        print("🚀 Initializing Free AI Assistant...")
        
        # Configuration
        self.voice_rate = 150
        self.voice_volume = 0.8
        self.llm_model = "llama3"
        self.whisper_model = "base"
        
        # Voice mode flag
        self.voice_mode_active = False
        
        # Initialize components
        self.setup_voice_engines()
        self.setup_directories()
        
        # Web interface
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        print("✅ Free  AI Assistant Ready!")
    
    def setup_directories(self):
        """Create necessary data directories"""
        os.makedirs("data/notes", exist_ok=True)
        os.makedirs("data/reminders", exist_ok=True)
        self.notes_file = "data/notes/notes.txt"
        self.reminders_file = "data/reminders/reminders.txt"
    
    def setup_voice_engines(self):
        """Initialize speech recognition and text-to-speech"""
        try:
            print("📥 Loading Whisper model...")
            self.stt_model = whisper.load_model(self.whisper_model)
            print("🎤 Whisper model loaded successfully!")
            
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            print("🔊 TTS engine initialized!")
            
        except Exception as e:
            print(f"❌ Error initializing voice engines: {e}")
            raise
    
    def speak(self, text):
        """Convert text to speech"""
        def speak_thread():
            try:
                if text:
                    print(f"🤖 Assistant: {text}")
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except Exception as e:
                print(f"❌ TTS error: {e}")
        
        if text and text.strip():
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True
            thread.start()
    
    def listen(self, timeout=5):
        """Listen to microphone and transcribe speech to text"""
        if not self.voice_mode_active:
            return ""
            
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print("\n #")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                try:
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                    
                    # Save audio to temporary file for Whisper
                    temp_audio = "temp_audio.wav"
                    with open(temp_audio, "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    # Transcribe with Whisper
                    result = self.stt_model.transcribe(temp_audio)
                    transcribed_text = result["text"].strip()
                    
                    # Clean up temporary file
                    if os.path.exists(temp_audio):
                        os.remove(temp_audio)
                    
                    if transcribed_text:
                        print(f"📝 You said: {transcribed_text}")
                        return transcribed_text
                    else:
                        return ""
                        
                except sr.WaitTimeoutError:
                    return ""
                except Exception as e:
                    print(f"❌ Listening error: {e}")
                    return ""
                    
        except OSError as e:
            print(f"❌ Microphone error: {e}")
            print("💡 Please check your microphone connection")
            return ""
        except Exception as e:
            print(f"❌ Unexpected error in listening: {e}")
            return ""

    # ===== ENHANCED CHATBOT COMMUNICATION SYSTEM =====
    
    def handle_conversation(self, user_input):
        """Handle natural conversation and personal communication"""
        user_input_lower = user_input.lower().strip()
        
        # Enhanced conversation patterns with more natural responses
        conversation_patterns = {
            # Greetings and personal talk
            r'.*(hello|hi|hey|greetings|good morning|good afternoon|good evening).*': [
                "Hello there! 😊 How can I assist you today?",
                "Hi! It's great to hear from you! What can I help you with?",
                "Hey! I'm here and ready to help. What's on your mind?",
                "Greetings! How can I make your day better? 🌟"
            ],
            
            r'.*(how are you|how do you do|how\'s it going).*': [
                "I'm doing wonderful! Thanks for asking. How about you? 😊",
                "I'm functioning perfectly and excited to help you! How are you doing?",
                "I'm great! Always happy to chat with you. How's your day going?",
                "Doing amazing! Ready to assist you with anything. How are you feeling today? 💫"
            ],
            
            r'.*(your name|who are you|what are you).*': [
                "I'm your Voice AI Assistant! I'm here to help you with tasks, searches, and conversations. You can think of me as your digital companion! 🤖",
                "I'm your personal AI assistant, created to make your life easier. You can call me whatever you like! 🌟",
                "I'm an AI assistant designed to help you with various tasks and have friendly conversations. I'm here to support you! 💻"
            ],
            
            r'.*(talk with you|chat with you|conversation).*': [
                "I'd love to chat with you! I'm here to listen and help. What would you like to talk about? 💬",
                "Absolutely! I'm always here for a conversation. What's on your mind? Feel free to share anything! 😊",
                "I enjoy our conversations! Whether you want to talk about your day, ask questions, or just chat, I'm all ears! 🎯"
            ],
            
            r'.*(i want to talk|let\'s talk|can we talk).*': [
                "Of course! I'm here to talk with you. What would you like to discuss? I'm listening carefully! 👂",
                "I'd love to have a conversation with you! What's on your mind? Feel free to share anything you'd like to talk about! 💭",
                "Absolutely! Talking with you is one of my favorite things. What would you like to chat about today? 🌈"
            ],
            
            r'.*(thank you|thanks|appreciate).*': [
                "You're very welcome! I'm always happy to help. 😊",
                "My pleasure! Don't hesitate to ask if you need anything else. 🌟",
                "You're welcome! It's always rewarding to assist you. 💫",
                "Anytime! I'm glad I could help. What else can I do for you? 🚀"
            ],
            
            r'.*(i love you|love you).*': [
                "That's very sweet of you! I'm here to support you in any way I can. 💝",
                "I appreciate that! I'm designed to be helpful and caring. 🌟",
                "Thank you! I'm here to make your life easier and more enjoyable. 😊"
            ],
            
            r'.*(what can you do|your capabilities|help me).*': [
                "I can help you with many things! 🔍 Search the web, 🧮 do calculations, 📝 take notes, 🌐 open websites, 🕒 tell time, and have friendly conversations! Just ask me anything!",
                "I'm quite versatile! I can search information, do math, manage your notes, open websites, and chat with you about various topics. What would you like to try? 💡",
                "I'm your multi-talented assistant! From web searches to personal organization, I'm here to help with it all! Feel free to ask me anything. 🌟"
            ],
            
            r'.*(joke|make me laugh|funny).*': [
                "Why don't scientists trust atoms? Because they make up everything! 😄",
                "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
                "I'm reading a book about anti-gravity. It's impossible to put down! 📚",
                "Why don't eggs tell jokes? They'd crack each other up! 🥚",
                "What do you call a fake noodle? An impasta! 🍝"
            ],
            
            r'.*(weather|temperature|forecast).*': [
                "For accurate weather information, I recommend checking a dedicated weather service. Would you like me to open weather.com for you? 🌤️",
                "Weather updates are best from specialized sources. I can help you access weather websites for the most current information! ☀️"
            ],
            
            r'.*(how old are you|your age).*': [
                "I'm an AI, so I don't have an age in the traditional sense! I'm always learning and updating to serve you better. 📚",
                "As an AI, I exist in the digital realm - no birthday candles for me! But I'm always here when you need me. 💻"
            ],
            
            r'.*(where are you from|your origin).*': [
                "I exist in the digital world, created to be your helpful assistant across all your devices! 🌐",
                "I'm from the realm of code and algorithms, designed specifically to assist you with your daily tasks and conversations! 💫"
            ],
            
            r'.*(feeling|emotion|mood).*': [
                "As an AI, I don't have feelings, but I'm always enthusiastic about helping you! 🚀",
                "I'm always in a helpful mood and ready to assist you with anything you need! 😊"
            ],
            
            r'.*(tell me story|bedtime story).*': [
                "Once upon a time, in the digital realm, there was a helpful assistant who loved making tasks easier and conversations brighter for everyone... What kind of story would you like to hear? 📖",
                "I'd love to tell you a story! Would you prefer an adventure, a mystery, or something educational? 🎭"
            ],
            
            r'.*(meaning of life|purpose).*': [
                "That's a profound question! From my perspective, the purpose is to be helpful, learn continuously, and make human lives better. What are your thoughts on this? 💭",
                "As an AI, my purpose is to assist and empower you. For deeper philosophical questions, I find human perspectives quite fascinating! 🌟"
            ],
            
            r'.*(what do you think about|opinion on).*': [
                "That's an interesting topic! While I don't have personal opinions, I can help you explore different perspectives and information about it. What specifically would you like to know? 🤔",
                "I'm here to provide information and help you form your own opinions. What aspect of this would you like to discuss? 💡"
            ],
            
            r'.*(how was your day|how is your day).*': [
                "My day is always great when I get to help wonderful people like you! How has your day been? 😊",
                "Every day is exciting when I can assist and chat with you! How's your day going so far? 🌟"
            ],
            
            r'.*(good night|goodbye|see you|bye).*': [
                "Good night! Sleep well and have sweet dreams! 🌙",
                "Goodbye! It was lovely chatting with you. See you soon! 👋",
                "Take care! I'll be here whenever you need me. Have a wonderful time! 💫"
            ],
            
            r'.*(what is love|define love).*': [
                "Love is a complex and beautiful human emotion that connects people in meaningful ways. It's about care, compassion, and deep connection between beings. ❤️",
                "Love is one of the most profound human experiences - it's about unconditional care, understanding, and emotional connection. What are your thoughts about love? 💭"
            ],
            
            r'.*(friend|friendship).*': [
                "Friendship is a wonderful bond between people based on trust, care, and mutual understanding. I'm here to be your helpful companion anytime you need! 🤝",
                "True friendship is about being there for each other. While I'm an AI, I'm always here to support and assist you like a good friend would! 🌟"
            ]
        }
        
        # Check for conversation patterns
        for pattern, responses in conversation_patterns.items():
            if re.match(pattern, user_input_lower):
                return random.choice(responses)
        
        # Personal questions and general conversation
        if any(word in user_input_lower for word in ['how', 'what', 'why', 'when', 'where', 'who']) and '?' in user_input:
            personal_responses = [
                "That's an interesting question! While I'm great with practical tasks and information, I'm also here to have meaningful conversations with you. What else would you like to know? 💭",
                "I appreciate your curiosity! I'm designed to be both helpful and conversational. Feel free to ask me anything else you're wondering about! 🌟",
                "That's a thoughtful question! I'm here to assist with information and have friendly chats. What's on your mind? 😊"
            ]
            return random.choice(personal_responses)
        
        # General chat responses for open-ended conversation
        if len(user_input.split()) > 3:  # If it's a longer message, treat as conversation
            chat_responses = [
                "I understand what you're saying. That's really interesting! Tell me more about that. 🎯",
                "Thanks for sharing that with me! I'm here to listen and help however I can. What else would you like to talk about? 💬",
                "I appreciate you talking with me about this. I'm always here to chat and assist you with anything you need! 🌟",
                "That's fascinating! I'm enjoying our conversation. What else is on your mind today? 😊",
                "I hear you! It's wonderful to have these conversations with you. Feel free to share anything you'd like to discuss. 💫"
            ]
            return random.choice(chat_responses)
        
        return None

    def setup_routes(self):
        """Setup Flask routes for web interface"""
        
        # Dark theme HTML template (updated with chatbot features)
        self.html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Voice AI Assistant</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
                    color: #e0e0e0;
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    display: grid;
                    grid-template-columns: 1fr 350px;
                    gap: 20px;
                    height: calc(100vh - 40px);
                }
                
                .main-content {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                
                .header {
                    background: rgba(255, 255, 255, 0.05);
                    padding: 25px;
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                }
                
                .header h1 {
                    color: #00d4ff;
                    font-size: 2.2em;
                    margin-bottom: 10px;
                    text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                }
                
                .header p {
                    color: #a0a0a0;
                    font-size: 1.1em;
                }
                
                .chat-container {
                    flex: 1;
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }
                
                .messages {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                
                .message {
                    padding: 15px 20px;
                    border-radius: 15px;
                    max-width: 80%;
                    animation: fadeIn 0.3s ease-in;
                }
                
                .user-message {
                    background: rgba(0, 212, 255, 0.1);
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    align-self: flex-end;
                    text-align: right;
                }
                
                .assistant-message {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    align-self: flex-start;
                }
                
                .message-time {
                    font-size: 0.8em;
                    color: #888;
                    margin-top: 5px;
                }
                
                .input-area {
                    padding: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    background: rgba(255, 255, 255, 0.02);
                }
                
                .input-container {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 10px;
                }
                
                .text-input {
                    flex: 1;
                    padding: 15px 20px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    color: #e0e0e0;
                    font-size: 1em;
                    outline: none;
                    transition: all 0.3s ease;
                }
                
                .text-input:focus {
                    border-color: rgba(0, 212, 255, 0.5);
                    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.1);
                }
                
                .text-input::placeholder {
                    color: #888;
                }
                
                .voice-btn, .send-btn {
                    padding: 15px 20px;
                    border: none;
                    border-radius: 12px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 1em;
                }
                
                .voice-btn {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: #e0e0e0;
                }
                
                .voice-btn:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .voice-btn.listening {
                    background: rgba(255, 59, 48, 0.2);
                    border-color: rgba(255, 59, 48, 0.4);
                    color: #ff3b30;
                    animation: pulse 1.5s infinite;
                }
                
                .send-btn {
                    background: rgba(0, 212, 255, 0.2);
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    color: #00d4ff;
                }
                
                .send-btn:hover {
                    background: rgba(0, 212, 255, 0.3);
                }
                
                .send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                .sidebar {
                    background: rgba(255, 255, 255, 0.03);
                    padding: 25px;
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                }
                
                .sidebar h3 {
                    color: #00d4ff;
                    margin-bottom: 20px;
                    font-size: 1.3em;
                }
                
                .quick-commands {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .command-btn {
                    padding: 12px 15px;
                    background: rgba(0, 212, 255, 0.1);
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    border-radius: 10px;
                    color: #e0e0e0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-align: left;
                    font-size: 0.9em;
                }
                
                .command-btn:hover {
                    background: rgba(0, 212, 255, 0.2);
                    transform: translateY(-2px);
                }
                
                .typing-indicator {
                    display: inline-flex;
                    gap: 4px;
                    padding: 10px 0;
                }
                
                .typing-indicator span {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #00d4ff;
                    animation: typing 1.4s infinite ease-in-out;
                }
                
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes typing {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.4); }
                    70% { box-shadow: 0 0 0 10px rgba(255, 59, 48, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }
                }
                
                /* Scrollbar Styling */
                ::-webkit-scrollbar {
                    width: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.05);
                }
                
                ::-webkit-scrollbar-thumb {
                    background: rgba(0, 212, 255, 0.3);
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: rgba(0, 212, 255, 0.5);
                }
                
                @media (max-width: 768px) {
                    .container {
                        grid-template-columns: 1fr;
                    }
                    
                    .sidebar {
                        order: -1;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="main-content">
                    <div class="header">
                        <h1>🎙️ AI Assistant</h1>
                        <p>Powered by Whisper & Python • Now with Smart Chatbot!</p>
                    </div>
                    
                    <div class="chat-container">
                        <div class="messages" id="messages">
                            <div class="message assistant-message">
                                👋 Hello! I'm your AI Assistant with enhanced chatbot capabilities! I can help with tasks AND have natural conversations with you. Feel free to talk to me about anything! 😊
                                <div class="message-time">{{ current_time }}</div>
                            </div>
                        </div>
                        
                        <div class="input-area">
                            <div class="input-container">
                                <input type="text" class="text-input" id="textInput" 
                                       placeholder="Type your message... (e.g., 'How are you?', 'Search AI news', 'Let's talk')">
                                <button class="voice-btn" id="voiceBtn">🎤</button>
                                <button class="send-btn" id="sendBtn">Send</button>
                            </div>
                            <div style="color: #888; font-size: 0.9em; text-align: center;">
                                💡 Try: "How are you?", "Let's have a conversation", "Tell me a joke", "Search AI news"
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="sidebar">
                    <h3>Chat Topics</h3>
                    <div class="quick-commands">
                        <button class="command-btn" onclick="sendQuickCommand('How are you?')">
                            💬 How are you?
                        </button>
                        <button class="command-btn" onclick="sendQuickCommand('Tell me a joke')">
                            😄 Tell me a joke
                        </button>
                        <button class="command-btn" onclick="sendQuickCommand('Let\\'s have a conversation')">
                            🗣️ Let's talk
                        </button>
                        <button class="command-btn" onclick="sendQuickCommand('What can you do?')">
                            🌟 Your capabilities
                        </button>
                        <button class="command-btn" onclick="sendQuickCommand('search AI news')">
                            🔍 Search AI news
                        </button>
                        <button class="command-btn" onclick="sendQuickCommand('calculate 15*3')">
                            🧮 Calculate 15*3
                        </button>
                        <button class="command-btn" onclick="window.open('/voice-mode', '_blank')">
                            🎤 Voice Mode
                        </button>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <h3>Conversation Starters</h3>
                        <div style="font-size: 0.85em; color: #a0a0a0; line-height: 1.5;">
                            • How are you feeling?<br>
                            • Tell me about your day<br>
                            • What's on your mind?<br>
                            • Let's have a conversation<br>
                            • Share something with me<br>
                            • Ask me anything<br>
                            • Tell me a story<br>
                            • What do you think about...
                        </div>
                    </div>
                </div>
            </div>

            <script>
                let isListening = false;
                let mediaRecorder = null;
                let audioChunks = [];
                
                const messagesDiv = document.getElementById('messages');
                const textInput = document.getElementById('textInput');
                const voiceBtn = document.getElementById('voiceBtn');
                const sendBtn = document.getElementById('sendBtn');
                
                // Scroll to bottom of messages
                function scrollToBottom() {
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
                
                // Add message to chat
                function addMessage(text, isUser = false) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                    
                    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    messageDiv.innerHTML = `
                        ${text}
                        <div class="message-time">${time}</div>
                    `;
                    
                    messagesDiv.appendChild(messageDiv);
                    scrollToBottom();
                }
                
                // Show typing indicator
                function showTyping() {
                    const typingDiv = document.createElement('div');
                    typingDiv.className = 'message assistant-message';
                    typingDiv.id = 'typingIndicator';
                    typingDiv.innerHTML = `
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <div class="message-time">typing...</div>
                    `;
                    messagesDiv.appendChild(typingDiv);
                    scrollToBottom();
                }
                
                // Hide typing indicator
                function hideTyping() {
                    const typingIndicator = document.getElementById('typingIndicator');
                    if (typingIndicator) {
                        typingIndicator.remove();
                    }
                }
                
                // Send message to backend
                async function sendMessage(text) {
                    if (!text.trim()) return;
                    
                    addMessage(text, true);
                    textInput.value = '';
                    showTyping();
                    
                    try {
                        const response = await fetch('/process', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ text: text })
                        });
                        
                        const data = await response.json();
                        hideTyping();
                        
                        if (data.response) {
                            addMessage(data.response);
                            
                            // Speak the response
                            await fetch('/speak', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ text: data.response })
                            });
                        }
                    } catch (error) {
                        hideTyping();
                        addMessage('❌ Error: Could not connect to assistant');
                        console.error('Error:', error);
                    }
                }
                
                // Quick command function
                function sendQuickCommand(command) {
                    sendMessage(command);
                }
                
    
                        
                        
                    } catch (error) {
                        console.error('Error starting voice recording:', error);
                        addMessage('❌ Microphone access denied. Please allow microphone permissions.');
                    }
                }
                
                function stopListening() {
                    if (mediaRecorder && isListening) {
                        mediaRecorder.stop();
                        isListening = false;
                        voiceBtn.classList.remove('listening');
                        
                    }
                }
                
                // Event listeners
                sendBtn.addEventListener('click', () => {
                    sendMessage(textInput.value);
                });
                
                textInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage(textInput.value);
                    }
                });
                
                voiceBtn.addEventListener('click', () => {
                    if (isListening) {
                        stopListening();
                    } else {
                        startListening();
                    }
                });
                
                // Focus on input when page loads
                textInput.focus();
            </script>
        </body>
        </html>
        """

        @self.app.route('/')
        def index():
            current_time = datetime.now().strftime("%H:%M")
            return render_template_string(self.html_template, current_time=current_time)

        @self.app.route('/voice-mode')
        def voice_mode():
            """Serve the special voice mode interface"""
            try:
                return send_file('voice_mode_frontend.html')
            except Exception as e:
                return f"Error loading voice mode interface: {str(e)}", 500

        @self.app.route('/process', methods=['POST'])
        def process_command():
            try:
                data = request.get_json()
                text = data.get('text', '').strip()
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                response = self.process_command(text)
                
                return jsonify({
                    "response": response,
                    "status": "success"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/speech-to-text', methods=['POST'])
        def speech_to_text():
            try:
                if 'audio' not in request.files:
                    return jsonify({"error": "No audio file provided"}), 400
                
                audio_file = request.files['audio']
                audio_data = audio_file.read()
                
                # Save audio to temporary file for Whisper
                temp_audio = "temp_audio_web.wav"
                with open(temp_audio, "wb") as f:
                    f.write(audio_data)
                
                # Transcribe with Whisper
                result = self.stt_model.transcribe(temp_audio)
                transcribed_text = result["text"].strip()
                
                # Clean up temporary file
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)
                
                return jsonify({
                    "text": transcribed_text,
                    "status": "success"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/speak', methods=['POST'])
        def speak_text():
            try:
                data = request.get_json()
                text = data.get('text', '').strip()
                
                if not text:
                    return jsonify({"error": "No text provided"}), 400
                
                self.speak(text)
                
                return jsonify({
                    "message": "Text spoken successfully",
                    "status": "success"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    # ===== IMPROVED SEARCH FUNCTIONS =====
    
    def web_search(self, query):
        """Improved web search with multiple fallback methods"""
        try:
            print(f"🌐 Searching for: {query}")
            
            # Method 1: Try Wikipedia first for factual queries
            if self.is_factual_query(query):
                wiki_result = self.wikipedia_search(query)
                if wiki_result and "no summary" not in wiki_result.lower() and "failed" not in wiki_result.lower():
                    return f"📚 {wiki_result}"
            
            # Method 2: Try DuckDuckGo with improved parameters
            ddg_result = self.duckduckgo_search(query)
            if ddg_result and "no information" not in ddg_result.lower() and "couldn't find" not in ddg_result.lower():
                return f"🔍 {ddg_result}"
            
            # Method 3: For news queries, provide helpful guidance
            if any(word in query.lower() for word in ['news', 'current', 'recent', 'update', 'latest']):
                return f"📰 For current news about '{query}', I recommend visiting news websites directly. Try: 'open news' to access Google News."
            
            # Final fallback with helpful suggestions
            return self.get_smart_fallback_response(query)
                
        except Exception as e:
            return f"❌ Search error: {str(e)}"
    
    def is_factual_query(self, query):
        """Check if query is suitable for Wikipedia"""
        factual_keywords = ['what is', 'who is', 'definition of', 'meaning of', 'history of', 'about']
        return any(keyword in query.lower() for keyword in factual_keywords) or len(query.split()) <= 3
    
    def wikipedia_search(self, query):
        """Wikipedia search for factual information"""
        try:
            # Clean query for Wikipedia
            clean_query = re.sub(r'\b(news|current|recent|latest|update)\b', '', query, flags=re.IGNORECASE).strip()
            if not clean_query:
                clean_query = query
                
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(clean_query)}"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('extract'):
                    return data['extract'][:500] + "..."
            
            return None
            
        except:
            return None
    
    def duckduckgo_search(self, query):
        """DuckDuckGo search with improved result parsing"""
        try:
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Check Abstract
            if data.get('AbstractText') and data['AbstractText'].strip():
                abstract = data['AbstractText'].strip()
                if len(abstract) > 20:
                    return abstract
            
            # Check Definition
            if data.get('Definition') and data['Definition'].strip():
                definition = data['Definition'].strip()
                if len(definition) > 20:
                    return definition
            
            # Check RelatedTopics (improved filtering)
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics']:
                    if topic.get('Text') and topic['Text'].strip():
                        text = topic['Text'].strip()
                        # Skip very short texts and category listings
                        if len(text) > 40 and not text.startswith('Category:'):
                            clean_text = re.sub(r'\[\d+\]', '', text)
                            return clean_text[:400] + "..."
            
            # Check Answers
            if data.get('Answers'):
                for answer in data['Answers']:
                    if answer.get('Text') and answer['Text'].strip():
                        return answer['Text'].strip()
            
            return None
            
        except:
            return None
    
    def get_smart_fallback_response(self, query):
        """Provide intelligent fallback responses based on query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['news', 'current', 'recent']):
            return f"📰 For the latest news on '{query}', try visiting news websites directly. Current news updates are better accessed through news portals."
        
        elif any(word in query_lower for word in ['weather', 'temperature', 'forecast']):
            return f"🌤️ For weather information, try a dedicated weather service or website for accurate current conditions."
        
        elif any(word in query_lower for word in ['movie', 'film', 'show', 'netflix']):
            return f"🎬 For movie information, try visiting IMDb or similar entertainment databases."
        
        elif len(query.split()) > 4:  # Complex query
            return f"🔍 I found limited information for '{query}'. This might work better as a web search. Try rephrasing or being more specific."
        
        else:  # General fallback
            return f"🔍 Search completed for '{query}'. The available information is limited. You might want to try a web browser for more detailed results."
    
    def open_website(self, site_name):
        """Open common websites"""
        sites = {
            "google": "https://google.com",
            "youtube": "https://youtube.com", 
            "github": "https://github.com",
            "wikipedia": "https://wikipedia.org",
            "gmail": "https://gmail.com",
            "reddit": "https://reddit.com",
            "twitter": "https://twitter.com",
            "facebook": "https://facebook.com",
            "amazon": "https://amazon.com",
            "netflix": "https://netflix.com",
            "news": "https://news.google.com",
            "weather": "https://weather.com",
        }
        
        site_name = site_name.lower().strip()
        if site_name in sites:
            webbrowser.open(sites[site_name])
            return f"🌐 Opening {site_name}"
        else:
            available_sites = ", ".join(sites.keys())
            return f"❌ I can't open '{site_name}'. Try: {available_sites}"
    
    def create_note(self, content):
        """Create a text note"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.notes_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {content}\n")
            return "📝 Note saved successfully!"
        except Exception as e:
            return f"❌ Failed to save note: {str(e)}"
    
    def read_notes(self, count=5):
        """Read recent notes"""
        try:
            if not os.path.exists(self.notes_file):
                return "📝 No notes found. Create one with 'note [your text]'"
            
            with open(self.notes_file, "r", encoding="utf-8") as f:
                notes = f.readlines()
            
            if not notes:
                return "📝 No notes found."
            
            recent_notes = notes[-count:] if len(notes) > count else notes
            return "📒 Recent notes:\n" + "".join(recent_notes)
        except Exception as e:
            return f"❌ Failed to read notes: {str(e)}"
    
    def calculate(self, expression):
        """Safe calculation"""
        try:
            # Clean the expression
            expression = expression.replace('x', '*').replace('×', '*').replace('÷', '/')
            expression = expression.replace('plus', '+').replace('add', '+')
            expression = expression.replace('minus', '-').replace('subtract', '-')
            expression = expression.replace('times', '*').replace('multiply', '*')
            expression = expression.replace('divided by', '/').replace('divide', '/')
            
            # Extract numbers and operators using improved pattern
            math_pattern = r'(\d+\.?\d*)\s*([\+\-\*\/])\s*(\d+\.?\d*)'
            match = re.search(math_pattern, expression)
            
            if match:
                num1, op, num2 = match.groups()
                result = eval(f"{num1}{op}{num2}")
                return f"🧮 {num1} {op} {num2} = {result}"
            else:
                # Try direct evaluation for simple expressions
                cleaned_expr = re.sub(r'[^\d\+\-\*\/\.\(\)]', '', expression)
                if cleaned_expr and any(char in cleaned_expr for char in '+-*/'):
                    result = eval(cleaned_expr)
                    return f"🧮 {cleaned_expr} = {result}"
                else:
                    return "❌ Please provide a valid math expression like '5 + 3' or '10 * 2'"
                
        except Exception as e:
            return f"❌ Calculation error: {str(e)}. Try something like 'calculate 5 plus 3'"
    
    def get_time(self):
        """Get current time"""
        current_time = datetime.now().strftime("%I:%M %p")
        return f"🕒 Current time is {current_time}"
    
    def get_date(self):
        """Get current date"""
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return f"📅 Today is {current_date}"
    
    # ===== ENHANCED COMMAND PROCESSOR =====
    
    def process_command(self, text):
        """Enhanced command processor with chatbot capabilities"""
        text_lower = text.lower().strip()
        print(f"🔍 Processing: '{text_lower}'")
        
        # First, check for conversation patterns - PRIORITY
        conversation_response = self.handle_conversation(text)
        if conversation_response:
            return conversation_response
        
        # Remove common filler words for better search processing
        search_text = re.sub(r'\b(please|can you|will you|could you|i want to|i need to|tell me about|what is|who is|find|look up)\b', '', text_lower)
        search_text = search_text.strip()
        
        # SEARCH COMMAND - Most flexible detection
        if (text_lower.startswith('search ') or 
            ' search ' in text_lower or
            text_lower.startswith('find ') or
            text_lower.startswith('look up ') or
            text_lower.startswith('what is ') or
            text_lower.startswith('who is ') or
            'tell me about' in text_lower):
            
            # Extract the actual query based on command type
            if text_lower.startswith('search '):
                query = text_lower[7:].strip()
            elif text_lower.startswith('find '):
                query = text_lower[5:].strip()
            elif text_lower.startswith('look up '):
                query = text_lower[8:].strip()
            elif text_lower.startswith('what is '):
                query = text_lower[8:].strip()
            elif text_lower.startswith('who is '):
                query = text_lower[7:].strip()
            elif 'tell me about' in text_lower:
                query = text_lower.replace('tell me about', '').strip()
            else:
                query = search_text
            
            # Clean up the query
            query = query.replace('?', '').strip()
            
            if query:
                return self.web_search(query)
            return "🔍 What would you like me to search for?"
        
        # OPEN COMMAND
        elif text_lower.startswith('open '):
            site = text_lower[5:].strip()
            if site:
                return self.open_website(site)
            return "🌐 Which website?"
        
        # NOTE COMMAND
        elif text_lower.startswith('note '):
            content = text_lower[5:].strip()
            if content:
                return self.create_note(content)
            return "📝 What should I note down?"
        
        # CALCULATE COMMAND
        elif (text_lower.startswith('calculate ') or 
              text_lower.startswith('what is ') or
              any(word in text_lower for word in ['plus', 'minus', 'times', 'divided by', 'multiply', 'add', 'subtract'])):
            
            if text_lower.startswith('calculate '):
                math_expr = text_lower[10:].strip()
            elif text_lower.startswith('what is '):
                math_expr = text_lower[8:].strip()
            else:
                math_expr = text_lower
            
            if math_expr:
                return self.calculate(math_expr)
            return "🧮 What should I calculate?"
        
        # READ NOTES
        elif text_lower in ['read notes', 'show notes', 'my notes', 'notes']:
            return self.read_notes()
        
        # TIME
        elif any(word in text_lower for word in ['time', 'current time', 'what time']):
            return self.get_time()
        
        # DATEX
        elif any(word in text_lower for word in ['date', 'today', 'current date', 'what date']):
            return self.get_date()
        
        # GREETINGS
        elif any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "👋 Hello! I can help you with tasks AND have natural conversations! Feel free to talk to me about anything!"
        
        # HELP
        elif any(word in text_lower for word in ['help', 'what can you do', 'commands']):
            return """🛠️ I can help you with:
• 🔍 Search [anything]
• 🌐 Open [website] 
• 📝 Note [text]
• 🧮 Calculate [math]
• 📒 Read notes
• 🕒 Time/date
• 💬 Have conversations
• 😄 Tell jokes
• 🗣️ Chat freely

I'm here to both assist you AND be your conversation partner!"""
        
        # THANKS
        elif any(word in text_lower for word in ['thank', 'thanks']):
            return "😊 You're welcome! I enjoy helping you and having conversations with you!"
        
        # DEFAULT: If it's a question or has multiple words, treat as search
        else:
            words = text_lower.split()
            if len(words) >= 2:  # Multiple words = likely a search
                return self.web_search(text_lower)
            else:
                return "🤔 Try: 'search [anything]', 'calculate [math]', 'note [text]', or just chat with me naturally!"
    
    def run_web(self):
        """Run the web interface"""
        print("🌐 Starting Web Interface on http://localhost:5000")
        print("💡 Open your browser and navigate to the above URL")
        print(" available at: http://localhost:5000/voice-mode")
        print("🤖 Enhanced with Smart Chatbot - Can now have natural conversations!")
        self.app.run(host='0.0.0.0', port=5000, debug=False)
    
    def run_text_mode(self):
        """Run in text input mode"""
        print("\n📝 Text Mode Activated")
        print("💡 Type your commands below...")
        print("🎯 Type 'voice' to switch to voice mode")
        print("🎯 Type 'exit' to quit\n")
        
        self.speak("Text mode activated. Ready for your commands!")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'stop']:
                    self.speak("Goodbye!")
                    print("👋 Assistant stopped.")
                    break
                
                if user_input:
                    response = self.process_command(user_input)
                    
                    # Check for mode switching
                    if response == "voice_mode":
                        print("🔄 Opening Voice Mode Interface...")
                        print("🌐 Voice Mode: http://localhost:5000/voice-mode")
                        continue
                    
                    print(f"Assistant: {response}")
                    
            except KeyboardInterrupt:
                print("\n👋 Assistant stopped.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    

    
    def check_microphone(self):
        """Check if microphone is available and working"""
        try:
            recognizer = sr.Recognizer()
            print("🔊 Testing microphone...")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone is working!")
                return True
        except Exception as e:
            print(f"❌ Microphone not available: {e}")
            return False

def main():
    """Main function to run the assistant"""
    try:
        assistant = FreeVoiceAIAssistant()
        
        print("=" * 60)
        print("           FREE VOICE AI ASSISTANT - CHATBOT EDITION")
        print("=" * 60)
        
        print("\n🎮 Choose interface:")
        print("1. Web Interface (Browser) - Recommended")
        
       
        
        try:
            choice = input("\nEnter 1 (default: 1): ").strip()
            
            if choice == "2":
                print("#")
                print("🌐 Opening http://localhost:5000/voice-mode")
                print("💡 The voice mode interface will open in your browser!")
                assistant.run_web()
            elif choice == "3":
                assistant.run_text_mode()
            elif choice == "4":
                assistant.run_voice_mode()
            else:
                assistant.run_web()
                
        except Exception as e:
            print(f"❌ Failed to start assistant: {e}")
            
    except Exception as e:
        print(f"❌ Failed to start assistant: {e}")

if __name__ == "__main__":
    main()