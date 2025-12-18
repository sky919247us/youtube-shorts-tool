import json
import logging
from config.settings import API_KEYS_FILE

class KeyManager:
    def __init__(self, file_path=API_KEYS_FILE):
        self.file_path = file_path
        self.keys = []
        self.current_index = 0
        if self.file_path:
            self.load_keys()

    def load_keys(self):
        """從 JSON 檔案讀取 API Keys"""
        if not self.file_path or not self.file_path.exists():
            if self.file_path:
                logging.warning(f"Key file not found: {self.file_path}")
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.keys = data.get("api_keys", [])
                self.current_index = data.get("current_index", 0)
                
                # Ensure index is valid
                if self.keys and self.current_index >= len(self.keys):
                    self.current_index = 0
                    
        except Exception as e:
            logging.error(f"Failed to load API keys: {e}")

    def save_keys(self):
        """儲存 Keys 與當前索引"""
        if not self.file_path:
            return

        data = {
            "api_keys": self.keys,
            "current_index": self.current_index
        }
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save API keys: {e}")

    def get_current_key(self) -> str:
        """取得當前的 API Key"""
        if not self.keys:
            return ""
        return self.keys[self.current_index]

    def rotate_key(self) -> str:
        """切換到下一個 Key (Round-Robin)"""
        if not self.keys:
            return ""
        
        self.current_index = (self.current_index + 1) % len(self.keys)
        self.save_keys()  # 記住最後使用的位置
        logging.info(f"Rotated to API Key index: {self.current_index}")
        return self.get_current_key()

    def set_keys(self, new_keys: list[str]):
        """更新 Key 列表 (從 UI 設定)"""
        # Filter empty strings
        valid_keys = [k.strip() for k in new_keys if k.strip()]
        self.keys = valid_keys
        self.current_index = 0
        self.save_keys()

    def validate_key(self, key: str) -> bool:
        """(Optional) 驗證 Key 是否有效 - 此功能通常需呼叫 API 測試"""
        # 這裡僅作簡單格式檢查，實際驗證需在 API Client 嘗試呼叫
        return len(key) > 20
