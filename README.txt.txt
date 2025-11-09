# SMART DeepSeek Memory Manager

A desktop application that enhances your DeepSeek AI conversations with persistent memory and smart conversation distillation.

## Features

- 🧠 **Smart Conversation Distillation** - Uses local Ollama models to extract key insights
- 💾 **Persistent Memory Storage** - Vector-based semantic search across all conversations  
- 🌐 **Browser Integration** - Automatic conversation capture from DeepSeek web interface
- 🎨 **GUI Interface** - Easy-to-use Tkinter-based desktop app

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt

2. Install Ollama and required models:

ollama pull deepseek-r1:32b-qwen-distill
ollama pull nomic-embed-text

3.Run the application

python smart_app.py