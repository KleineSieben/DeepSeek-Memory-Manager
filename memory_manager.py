import ollama
import time
import json
import os
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Bypass proxy for local connections
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'

# Configuration
DISTILLATION_MODEL = "deepseek-r1:32b-qwen-distill-q4_K_M"
EMBEDDING_MODEL = "nomic-embed-text"  # Lightweight local embedder

class SmartMemory:
    def __init__(self):
        self.memory_file = "smart_memories.json"
        self.memories = self.load_memories()
        
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
            return response['embeddings'][0]  # nomic-embed-text returns 768 dimensions
        except Exception as e:
            print(f"Embedding error: {e}")
            # Fallback: return random embedding of correct dimension (768 for nomic-embed-text)
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
        """Distill with retries and fallbacks"""
        for attempt in range(max_retries):
            try:
                prompt = self.create_distillation_prompt(user_msg, assistant_msg)
                response = ollama.generate(model=DISTILLATION_MODEL, prompt=prompt)
                distilled = response['response'].strip()
                
                if self.quality_check(distilled):
                    print(f"✓ Distillation successful (attempt {attempt + 1})")
                    return distilled
                else:
                    print(f"⚠ Distillation quality check failed, retrying...")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Distillation error (attempt {attempt + 1}): {e}")
                time.sleep(2)
        
        # Fallback: use a smart excerpt
        fallback = assistant_msg[:300] + "..." if len(assistant_msg) > 300 else assistant_msg
        return f"Key points: {fallback}"
    
    def save_conversation(self, user_message, assistant_response):
        """Save conversation with smart distillation"""
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