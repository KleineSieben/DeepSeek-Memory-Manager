import ollama
import time
import json
import os
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Bypass proxy for local connections
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'

DISTILLATION_MODEL = "deepseek-r1:32b-qwen-distill"  # Remove specific quantization
EMBEDDING_MODEL = "nomic-embed-text"  # This is correct

class SmartMemory:
    def check_models_available(self):
        """Robust model detection - handles different naming formats"""
        try:
            response = ollama.list()
            print(f"🔍 Ollama response received")
            
            # Extract model names safely
            if hasattr(response, 'models'):
                installed_models = [getattr(model, 'model', '') for model in response.models]
            elif 'models' in response:
                installed_models = [model.get('model', model.get('name', '')) for model in response['models']]
            else:
                installed_models = [model.get('model', model.get('name', '')) for model in response]
            
            print(f"📋 Found models: {installed_models}")
            
            # Check models with flexible matching
            distillation_models = [m for m in installed_models if DISTILLATION_MODEL in m]
            embedding_models = [m for m in installed_models if EMBEDDING_MODEL in m]
            
            if distillation_models:
                print(f"✅ Distillation model: {distillation_models[0]}")
            else:
                print(f"❌ Missing: {DISTILLATION_MODEL}")
                
            if embedding_models:
                print(f"✅ Embedding model: {embedding_models[0]}")
            else:
                print(f"❌ Missing: {EMBEDDING_MODEL}")
                
            return len(distillation_models) > 0 and len(embedding_models) > 0
            
        except Exception as e:
            print(f"❌ Cannot check models: {e}")
            return False

    def __init__(self):
        self.memory_file = "smart_memories.json"
        self.memories = self.load_memories()
        
        # Check models on startup
        print("🔍 Checking required models...")
        self.check_models_available()  # ← THIS MUST BE INSIDE __init__

    def load_memories(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_memories(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def get_embedding(self, text):
        """Get embedding using local Ollama model"""
        try:
            response = ollama.embed(model=EMBEDDING_MODEL, input=text)
            return response['embeddings'][0]
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            print("💡 Check: Is Ollama running? Run 'ollama serve' in another window")
            # Fallback: return random embedding
            return [0.0] * 768
    
    def create_distillation_prompt(self, user_msg, assistant_msg):
        """Smart prompt to prevent garbage"""
        return f"""
EXTRACT KEY INFORMATION FROM THIS CONVERSATION:

USER: {user_msg[:1500]}
ASSISTANT: {assistant_msg[:1500]}

Create a VERY CONCISE summary (3-5 bullet points max) focusing on:
• Key facts mentioned  
• User's preferences or constraints
• Important context for future chats
• Any decisions or conclusions

DO NOT include greetings, small talk, or repetitive information.
KEEP IT SHORT AND USEFUL.

SUMMARY:
"""
    
    def quality_check(self, distilled_text):
        """Make sure we don't store garbage"""
        if not distilled_text or len(distilled_text) < 20:
            return False
        if len(distilled_text) > 800:
            return False  
        garbage_indicators = ["i don't know", "error", "cannot", "sorry", "i can't"]
        if any(indicator in distilled_text.lower() for indicator in garbage_indicators):
            return False
        return True
    
    def safe_distill(self, user_msg, assistant_msg, max_retries=2):
        """Distill with better error handling and model selection"""
        for attempt in range(max_retries):
            try:
                prompt = self.create_distillation_prompt(user_msg, assistant_msg)
                
                # Get available models and use the first matching one
                models = ollama.list()
                available_models = [m['model'] for m in models.get('models', [])]
                distillation_model = [m for m in available_models if 'deepseek-r1:32b-qwen-distill' in m][0]
                
                response = ollama.generate(model=distillation_model, prompt=prompt)
                distilled = response['response'].strip()
                
                if self.quality_check(distilled):
                    print(f"✓ Distillation successful")
                    return distilled
                else:
                    print(f"⚠ Quality check failed, retrying...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Distillation error (attempt {attempt + 1}): {e}")
                time.sleep(2)
        
        # Fallback with clear explanation
        fallback = assistant_msg[:300] + "..." if len(assistant_msg) > 300 else assistant_msg
        print("🔄 Using fallback (distillation unavailable)")
        return f"Key points: {fallback}"
    
    def save_conversation(self, user_message, assistant_response):
        """Save conversation with smart distillation - CORRECTED VERSION"""
        print("🧠 Distilling conversation...")
        distilled = self.safe_distill(user_message, assistant_response)
        
        # Generate embedding from the distilled version
        embedding = self.get_embedding(distilled)
        
        memory_entry = {
            "raw_user": user_message[:800],
            "raw_assistant": assistant_response[:800],
            "distilled": distilled,
            "embedding": embedding,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memories.append(memory_entry)
        self.save_memories()
        print(f"✅ Smart memory saved: {distilled[:80]}...")
    
    def find_relevant_memories(self, query, n_results=3):
        """Find relevant memories using the distilled versions"""
        if not self.memories:
            return []
        
        # Get embedding for the query
        query_embedding = np.array(self.get_embedding(query)).reshape(1, -1)
        
        similarities = []
        for memory in self.memories:
            mem_embedding = np.array(memory["embedding"]).reshape(1, -1)
            similarity = cosine_similarity(query_embedding, mem_embedding)[0][0]
            similarities.append((similarity, memory["distilled"]))
        
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [text for _, text in similarities[:n_results]]
    
    def ask_with_memory(self, query, n_results=3):
        """Enhanced prompt with relevant memories"""
        relevant = self.find_relevant_memories(query, n_results)
        
        if not relevant:
            return query
        
        context = "Relevant past conversations:\n"
        for i, memory in enumerate(relevant, 1):
            context += f"{i}. {memory}\n"
        
        enhanced_prompt = f"{context}\n\nNew question: {query}"
        return enhanced_prompt

    def inspect_memory_structure(self):
        """Debug: Show exactly what's stored in memories"""
        print(f"\n🧠 MEMORY STRUCTURE INSPECTION:")
        print(f"Total memories: {len(self.memories)}")
        
        for i, memory in enumerate(self.memories):
            print(f"\n--- Memory {i+1} ---")
            print(f"Keys: {list(memory.keys())}")
            if 'distilled' in memory:
                print(f"Has distilled: YES (length: {len(memory['distilled'])})")
                print(f"Distilled preview: {memory['distilled'][:100]}...")
            else:
                print(f"Has distilled: NO")
            print(f"Raw user preview: {memory.get('raw_user', 'MISSING')[:100]}...")

    def search_memories(self):
        """Search through stored memories"""
        search_term = simpledialog.askstring("Search Memories", "Enter search term:")
        if search_term:
            relevant_memories = []
            for memory in self.memory.memories:
                if (search_term.lower() in memory.get('distilled', '').lower() or 
                    search_term.lower() in memory.get('raw_user', '').lower()):
                    relevant_memories.append(memory)
            
            if relevant_memories:
                self.show_search_results(relevant_memories, search_term)
            else:
                messagebox.showinfo("Search Results", f"No memories found for '{search_term}'")

    def show_search_results(self, memories, search_term):
        """Display search results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results for '{search_term}'")
        results_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(results_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_area.insert(tk.END, f"🔍 Found {len(memories)} memories for '{search_term}':\n\n")
        
        for i, memory in enumerate(memories, 1):
            text_area.insert(tk.END, f"🧠 MEMORY {i}:\n")
            text_area.insert(tk.END, f"📅 {memory['timestamp']}\n")
            text_area.insert(tk.END, f"💡 {memory.get('distilled', 'NOT DISTILLED')}\n")
            text_area.insert(tk.END, "="*70 + "\n\n")

    def create_backup(self):
        """Create a backup of memories"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"smart_memories_backup_{timestamp}.json"
        
        try:
            shutil.copy2(self.memory_file, backup_file)
            messagebox.showinfo("Backup Created", f"Backup saved as: {backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not create backup: {e}")

    def system_health_check(self):
        """Check the health of the entire system"""
        health_report = []
        
        # Check memory count
        health_report.append(f"📊 Memories stored: {len(self.memory.memories)}")
        
        # Check model availability
        try:
            models = ollama.list()
            model_count = len(models.get('models', []))
            health_report.append(f"🤖 Available models: {model_count}")
        except:
            health_report.append("❌ Cannot connect to Ollama")
        
        # Check file health
        if os.path.exists(self.memory.memory_file):
            file_size = os.path.getsize(self.memory.memory_file)
            health_report.append(f"💾 Memory file size: {file_size} bytes")
        else:
            health_report.append("❌ Memory file missing")
        
        messagebox.showinfo("System Health", "\n".join(health_report))