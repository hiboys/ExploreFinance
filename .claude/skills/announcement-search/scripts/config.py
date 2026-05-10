import os
import json
import logging
from typing import Dict, Any, Optional

class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        default_config = {
            "api": {
                "base_url": "https://openapi.iwencai.com",
                "endpoint": "/v1/comprehensive/search",
                "timeout": 30,
                "max_retries": 3
            },
            "auth": {
                "api_key_env_var": "IWENCAI_API_KEY",
                "api_key": os.getenv("IWENCAI_API_KEY", "")
            },
            "search": {
                "channels": ["announcement"],
                "app_id": "AIME_SKILL",
                "default_limit": 10,
                "max_limit": 50
            },
            "skill": {
                "id": "announcement-search",
                "version": "1.0.0",
                "plugin_id": "none",
                "plugin_version": "none"
            },
            "output": {
                "default_format": "csv",
                "supported_formats": ["csv", "json", "txt"],
                "date_format": "%Y-%m-%d %H:%M:%S",
                "encoding": "utf-8"
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "announcement_search.log"
            },
            "cache": {
                "enabled": False,
                "ttl": 3600,
                "cache_dir": ".cache"
            },
            "performance": {
                "max_concurrent_requests": 5,
                "request_delay": 0.5,
                "batch_size": 10
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    default_config = self._merge_configs(default_config, file_config)
            except Exception as e:
                logging.warning(f"Failed to load config file {config_path}: {e}")
        
        return default_config
    
    def _merge_configs(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _setup_logging(self):
        log_config = self.config["logging"]
        log_level = getattr(logging, log_config["level"].upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format=log_config["format"],
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_config["file"])
            ]
        )
    
    def get_api_key(self) -> str:
        api_key = self.config["auth"]["api_key"]
        if not api_key:
            raise ValueError("API Key not found. Please set IWENCAI_API_KEY environment variable.")
        return api_key
    
    def get_api_config(self) -> Dict[str, Any]:
        return self.config["api"]
    
    def get_search_config(self) -> Dict[str, Any]:
        return self.config["search"]
    
    def get_output_config(self) -> Dict[str, Any]:
        return self.config["output"]
    
    def get_cache_config(self) -> Dict[str, Any]:
        return self.config["cache"]
    
    def get_performance_config(self) -> Dict[str, Any]:
        return self.config["performance"]
    
    def get_skill_config(self) -> Dict[str, Any]:
        return self.config["skill"]
    
    def validate(self) -> bool:
        try:
            api_key = self.get_api_key()
            if not api_key or api_key == "your_api_key_here":
                return False
            
            search_config = self.get_search_config()
            if not search_config.get("channels") or "announcement" not in search_config["channels"]:
                return False
            
            if not search_config.get("app_id"):
                return False
            
            return True
        except Exception as e:
            logging.error(f"Config validation failed: {e}")
            return False

config = Config()

if __name__ == "__main__":
    print("Configuration loaded successfully")
    print(f"API Base URL: {config.get_api_config()['base_url']}")
    print(f"Search Channels: {config.get_search_config()['channels']}")
    print(f"Default Output Format: {config.get_output_config()['default_format']}")