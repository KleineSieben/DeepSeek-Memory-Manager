import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import time
import shutil
from datetime import datetime
from memory_manager import SmartMemory
from browser_integration import DeepSeekBrowserIntegration

class SmartMemoryApp:
    def __init__(self, root):
        self.memory = SmartMemory()
        self.browser_integration = DeepSeekBrowserIntegration(self.memory)
        self.root = root
        self.root.title("🧠 SMART DeepSeek Memory Manager + Browser")
        self.root.geometry("1000x800")
        self.root.minsize(900, 750)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(main_frame, text="🧠 SMART DeepSeek Memory Manager + Browser", 
                            font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Stats
        self.stats_label = tk.Label(main_frame, text=f"Memories stored: {len(self.memory.memories)}",
                                font=("Arial", 10))
        self.stats_label.pack(pady=(0, 10))
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(control_frame, text="📊 View All Memories", 
                command=self.view_memories, bg='#9C27B0', fg='white', width=18).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(control_frame, text="🔄 Check Memory Health", 
                command=self.check_memory_health, bg='#FF9800', fg='white', width=18).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="💾 Backup Memories", 
                command=self.create_backup, bg='#4CAF50', fg='white', width=18).pack(side=tk.LEFT, padx=5)
        
        # Browser Integration Section - SIMPLE VERSION
        browser_frame = tk.LabelFrame(main_frame, text="🌐 Auto-Browser Integration", 
                                    font=("Arial", 10, "bold"))
        browser_frame.pack(fill=tk.X, pady=(0, 8))
        
        browser_controls = tk.Frame(browser_frame)
        browser_controls.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(browser_controls, text="🚀 Launch & Auto-Monitor", 
                 command=self.launch_and_monitor, bg='#2196F3', fg='white', width=20).pack(side=tk.LEFT, padx=2)
        tk.Button(browser_controls, text="⏹️ Stop", 
                 command=self.stop_monitoring, bg='#f44336', fg='white', width=10).pack(side=tk.LEFT, padx=2)
        
        # Browser status
        self.browser_status = tk.Label(browser_frame, text="Status: Click 'Launch' to start", 
                                      font=("Arial", 9))
        self.browser_status.pack(pady=2)
        
        # Browser log
        browser_log_frame = tk.Frame(browser_frame)
        browser_log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(browser_log_frame, text="Browser Log:").pack(anchor='w')
        self.browser_log = scrolledtext.ScrolledText(browser_log_frame, height=3)
        self.browser_log.pack(fill=tk.X, pady=2)
        
        # Add Conversation Section
        add_frame = tk.LabelFrame(main_frame, text="Add Conversation (Smart Distillation)", font=("Arial", 10))
        add_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(add_frame, text="Your Message:").pack(anchor='w', pady=(5, 0))
        self.user_text = scrolledtext.ScrolledText(add_frame, height=2)
        self.user_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(add_frame, text="Assistant Response:").pack(anchor='w')
        self.assistant_text = scrolledtext.ScrolledText(add_frame, height=2)
        self.assistant_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Button(add_frame, text="💾 Save with Smart Distillation", command=self.save_conversation,
                bg='#4CAF50', fg='white').pack(pady=5)
        
        # Ask with Memory Section
        ask_frame = tk.LabelFrame(main_frame, text="Ask with Memory", font=("Arial", 10))
        ask_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(ask_frame, text="Your Question:").pack(anchor='w', pady=(5, 0))
        self.question_text = scrolledtext.ScrolledText(ask_frame, height=2)
        self.question_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Button(ask_frame, text="🔍 Generate Enhanced Prompt", command=self.generate_prompt,
                bg='#2196F3', fg='white').pack(pady=5)
        
        # Results Section
        result_frame = tk.LabelFrame(main_frame, text="Enhanced Prompt (Copy to DeepSeek)", font=("Arial", 10))
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=6)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="🔍 Search Memories", 
                command=self.search_memories, width=15).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="🗑️ Clear All Text", 
                command=self.clear_all, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📋 Copy Result", 
                command=self.copy_result, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Exit", command=self.root.quit, 
                bg='#f44336', fg='white', width=15).pack(side=tk.RIGHT)
    
    def launch_and_monitor(self):
        """Single button that launches browser and starts monitoring"""
        def browser_thread():
            self.update_browser_status("🔄 Launching browser...")
            self.log_browser_message("Starting browser setup...")
            
            if self.browser_integration.setup_browser():
                self.update_browser_status("✅ Browser ready")
                self.log_browser_message("Browser setup successful")
                
                if self.browser_integration.navigate_to_deepseek():
                    self.update_browser_status("🔍 Monitoring DeepSeek conversations...")
                    self.log_browser_message("DeepSeek loaded - starting monitoring")
                    
                    # Start monitoring
                    self.browser_integration.start_monitoring(callback=self.log_browser_message)
                else:
                    self.update_browser_status("❌ Failed to load DeepSeek")
                    self.log_browser_message("Failed to load DeepSeek")
            else:
                self.update_browser_status("❌ Browser setup failed")
                self.log_browser_message("Browser setup failed")
        
        threading.Thread(target=browser_thread, daemon=True).start()
    
    def stop_monitoring(self):
        """Stop browser monitoring"""
        self.browser_integration.stop_monitoring()
        self.update_browser_status("⏹️ Monitoring stopped")
        self.log_browser_message("Stopped monitoring")
    
    def update_browser_status(self, status):
        """Update browser status label"""
        def update():
            self.browser_status.config(text=f"Status: {status}")
        self.root.after(0, update)
    
    def log_browser_message(self, message):
        """Add message to browser log"""
        def update():
            self.browser_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.browser_log.see(tk.END)
        self.root.after(0, update)
    
    def save_conversation(self):
        """Save conversation with error handling"""
        try:
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
        except Exception as e:
            error_msg = f"Failed to save conversation:\n{str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def generate_prompt(self):
        """Generate prompt with error handling"""
        try:
            question = self.question_text.get("1.0", tk.END).strip()
            if question:
                enhanced = self.memory.ask_with_memory(question)
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", enhanced)
            else:
                messagebox.showwarning("Input Error", "Please enter a question")
        except Exception as e:
            error_msg = f"Failed to generate prompt:\n{str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def view_memories(self):
        """View all stored memories"""
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
        """Clear all text fields"""
        self.user_text.delete("1.0", tk.END)
        self.assistant_text.delete("1.0", tk.END)
        self.question_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
    
    def create_backup(self):
        """Create a backup of memories"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"smart_memories_backup_{timestamp}.json"
            
            shutil.copy2("smart_memories.json", backup_file)
            messagebox.showinfo("Backup Created", f"Backup saved as: {backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not create backup: {e}")
    
    def search_memories(self):
        """Search through stored memories"""
        search_term = simpledialog.askstring("Search Memories", "Enter search term:")
        if search_term:
            relevant_memories = []
            for memory in self.memory.memories:
                if (search_term.lower() in memory.get('distilled', '').lower() or 
                    search_term.lower() in memory.get('raw_user', '').lower() or
                    search_term.lower() in memory.get('raw_assistant', '').lower()):
                    relevant_memories.append(memory)
            
            if relevant_memories:
                self.show_search_results(relevant_memories, search_term)
            else:
                messagebox.showinfo("Search Results", f"No memories found for '{search_term}'")
    
    def show_search_results(self, memories, search_term):
        """Display search results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results for '{search_term}'")
        results_window.geometry("800x500")
        
        text_area = scrolledtext.ScrolledText(results_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_area.insert(tk.END, f"🔍 Found {len(memories)} memories for '{search_term}':\n\n")
        
        for i, memory in enumerate(memories, 1):
            text_area.insert(tk.END, f"🧠 MEMORY {i}:\n")
            text_area.insert(tk.END, f"📅 {memory['timestamp']}\n")
            text_area.insert(tk.END, f"💡 {memory.get('distilled', 'NOT DISTILLED')}\n")
            text_area.insert(tk.END, f"👤 User: {memory.get('raw_user', '')[:100]}...\n")
            text_area.insert(tk.END, f"🤖 Assistant: {memory.get('raw_assistant', '')[:100]}...\n")
            text_area.insert(tk.END, "="*70 + "\n\n")
    
    def copy_result(self):
        """Copy the result text to clipboard"""
        result_text = self.result_text.get("1.0", tk.END).strip()
        if result_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(result_text)
            messagebox.showinfo("Copied", "Enhanced prompt copied to clipboard!")
        else:
            messagebox.showwarning("No Text", "No text to copy")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartMemoryApp(root)
    root.mainloop()