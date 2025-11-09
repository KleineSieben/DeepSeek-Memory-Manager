import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class DeepSeekBrowserIntegration:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.driver = None
        self.is_monitoring = False
        
    def setup_browser(self):
        """Setup Brave browser with ZERO setup required"""
        try:
            chrome_options = Options()
            
            # Configure for Brave
            brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
            chrome_options.binary_location = brave_path
            
            # NO PROFILE CONFIGURATION - uses temporary profile automatically
            # Browser options for stability
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")  # More stable without extensions
            
            # Use manual driver path
            driver_path = "./chromedriver.exe"
            if not os.path.exists(driver_path):
                print(f"❌ ChromeDriver not found at: {driver_path}")
                return False
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Browser setup complete! (Using temporary profile)")
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def navigate_to_deepseek(self):
        """Navigate to DeepSeek chat"""
        if not self.driver:
            return False
            
        try:
            self.driver.get("https://chat.deepseek.com")
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ DeepSeek loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to load DeepSeek: {e}")
            return False

    def extract_conversation(self):
        """Better conversation extraction"""
        try:
            # Try to find the main chat area
            possible_selectors = [
                "main", "[role='main']", ".chat-container", 
                ".conversation", "#chat", "[class*='message']"
            ]
            
            for selector in possible_selectors:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = container.text
                    if text and len(text) > 50:  # Reasonable chat length
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        conversation = []
                        
                        for line in lines:
                            if len(line) > 10:  # Minimum message length
                                if any(word in line.lower() for word in ['you:', 'user:', 'question:']):
                                    conversation.append(('user', line))
                                else:
                                    conversation.append(('assistant', line))
                        
                        if conversation:
                            print(f"✅ Found {len(conversation)} messages using selector: {selector}")
                            return conversation[-4:]  # Last 4 messages
                except:
                    continue
            
            # Fallback: use body text
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in body_text.split('\n') if line.strip() and len(line.strip()) > 10]
            
            if lines:
                print(f"⚠️ Using fallback, found {len(lines)} lines")
                return [('assistant' if i % 2 == 0 else 'user', line) for i, line in enumerate(lines[-4:])]
            
            return []
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return []
    
    def process_conversation(self, conversation, callback=None):
        """Process and save conversation"""
        if len(conversation) >= 2:
            # Find user-assistant pairs
            for i in range(len(conversation)-1):
                if conversation[i][0] == 'user' and conversation[i+1][0] == 'assistant':
                    user_msg = conversation[i][1]
                    assistant_msg = conversation[i+1][1]
                    
                    try:
                        self.memory.save_conversation(user_msg, assistant_msg)
                        if callback:
                            callback(f"Saved: {user_msg[:30]}...")
                    except Exception as e:
                        if callback:
                            callback(f"Save failed: {e}")
    
    def start_monitoring(self, callback=None):
        """Start monitoring conversations"""
        self.is_monitoring = True
        
        def monitor():
            last_hash = ""
            while self.is_monitoring:
                try:
                    conversation = self.extract_conversation()
                    current_hash = str(conversation)
                    
                    if current_hash != last_hash and conversation:
                        self.process_conversation(conversation, callback)
                        last_hash = current_hash
                    
                    import time
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    if callback:
                        callback(f"Monitoring error: {e}")
                    import time
                    time.sleep(5)
        
        import threading
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.driver:
            self.driver.quit()