import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from memory_manager import SmartMemory

class SmartMemoryApp:
    def __init__(self, root):
        self.memory = SmartMemory()
        self.root = root
        self.root.title("🧠 SMART DeepSeek Memory Manager")
        self.root.geometry("800x600")
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🧠 SMART DeepSeek Memory Manager", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Stats
        self.stats_label = tk.Label(main_frame, text=f"Memories stored: {len(self.memory.memories)}",
                                   font=("Arial", 10))
        self.stats_label.pack(pady=5)
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(control_frame, text="📊 View All Memories", 
                 command=self.view_memories, bg='#9C27B0', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="🔄 Check Memory Health", 
                 command=self.check_memory_health, bg='#FF9800', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Add Conversation Section
        add_frame = tk.LabelFrame(main_frame, text="Add Conversation (Smart Distillation)", font=("Arial", 10))
        add_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(add_frame, text="Your Message:").pack(anchor='w')
        self.user_text = scrolledtext.ScrolledText(add_frame, height=3)
        self.user_text.pack(fill=tk.X, pady=2)
        
        tk.Label(add_frame, text="Assistant Response:").pack(anchor='w')
        self.assistant_text = scrolledtext.ScrolledText(add_frame, height=3)
        self.assistant_text.pack(fill=tk.X, pady=2)
        
        tk.Button(add_frame, text="💾 Save with Smart Distillation", command=self.save_conversation,
                 bg='#4CAF50', fg='white').pack(pady=5)
        
        # Ask with Memory Section
        ask_frame = tk.LabelFrame(main_frame, text="Ask with Memory", font=("Arial", 10))
        ask_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ask_frame, text="Your Question:").pack(anchor='w')
        self.question_text = scrolledtext.ScrolledText(ask_frame, height=2)
        self.question_text.pack(fill=tk.X, pady=2)
        
        tk.Button(ask_frame, text="🔍 Generate Enhanced Prompt", command=self.generate_prompt,
                 bg='#2196F3', fg='white').pack(pady=5)
        
        # Results Section
        result_frame = tk.LabelFrame(main_frame, text="Enhanced Prompt (Copy to DeepSeek)", font=("Arial", 10))
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="🗑️ Clear All Text", command=self.clear_all).pack(side=tk.LEFT)
        tk.Button(button_frame, text="❌ Exit", command=self.root.quit, 
                 bg='#f44336', fg='white').pack(side=tk.RIGHT)
    
    def save_conversation(self):
        user_msg = self.user_text.get("1.0", tk.END).strip()
        assistant_msg = self.assistant_text.get("1.0", tk.END).strip()
        
        if user_msg and assistant_msg:
            self.memory.save_conversation(user_msg, assistant_msg)
            messagebox.showinfo("Success", "Conversation saved with smart distillation!")
            self.user_text.delete("1.0", tk.END)
            self.assistant_text.delete("1.0", tk.END)
            self.update_stats()
        else:
            messagebox.showwarning("Input Error", "Please enter both user and assistant messages")
    
    def generate_prompt(self):
        question = self.question_text.get("1.0", tk.END).strip()
        if question:
            enhanced = self.memory.ask_with_memory(question)
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", enhanced)
        else:
            messagebox.showwarning("Input Error", "Please enter a question")
    
    def view_memories(self):
        if not self.memory.memories:
            messagebox.showinfo("Memories", "No memories stored yet.")
            return
        
        memory_window = tk.Toplevel(self.root)
        memory_window.title("All Memories")
        memory_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(memory_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, memory in enumerate(self.memory.memories, 1):
            text_area.insert(tk.END, f"🧠 MEMORY {i}:\n")
            text_area.insert(tk.END, f"📅 Timestamp: {memory['timestamp']}\n")
            text_area.insert(tk.END, f"💡 Distilled: {memory.get('distilled', 'NOT DISTILLED')}\n")
            text_area.insert(tk.END, f"👤 Raw User: {memory.get('raw_user', '')[:200]}...\n")
            text_area.insert(tk.END, f"🤖 Raw Assistant: {memory.get('raw_assistant', '')[:200]}...\n")
            text_area.insert(tk.END, "="*70 + "\n\n")
    
    def check_memory_health(self):
        """Check if memories are properly distilled"""
        if not self.memory.memories:
            messagebox.showinfo("Memory Health", "No memories stored yet.")
            return
        
        healthy_count = 0
        problematic = []
        
        for i, memory in enumerate(self.memory.memories):
            if 'distilled' in memory and memory['distilled'] and len(memory['distilled']) > 20:
                healthy_count += 1
            else:
                problematic.append(i + 1)
        
        messagebox.showinfo("Memory Health", 
                           f"Total memories: {len(self.memory.memories)}\n"
                           f"Properly distilled: {healthy_count}\n"
                           f"Problematic memories: {problematic}")
    
    def update_stats(self):
        """Update the statistics display"""
        self.stats_label.config(text=f"Memories stored: {len(self.memory.memories)}")
    
    def clear_all(self):
        self.user_text.delete("1.0", tk.END)
        self.assistant_text.delete("1.0", tk.END)
        self.question_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartMemoryApp(root)
    root.mainloop()