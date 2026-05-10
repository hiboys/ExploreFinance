import os
import sys
import json
import csv
import logging
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    def setup_logging(level: str = "INFO"):
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    @staticmethod
    def validate_query(query: str) -> bool:
        if not query or not query.strip():
            logger.error("Query cannot be empty")
            return False
        
        if len(query.strip()) < 2:
            logger.error("Query is too short")
            return False
        
        return True
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            logger.warning(f"Failed to parse date: {date_str}")
            return None
    
    @staticmethod
    def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        return date_obj.strftime(format_str)
    
    @staticmethod
    def generate_cache_key(query: str, limit: int = 10) -> str:
        key_str = f"{query}_{limit}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def save_to_csv(data: List[Dict[str, Any]], filepath: str) -> bool:
        try:
            if not data:
                logger.warning("No data to save")
                return False
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            fieldnames = data[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Data saved to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
            return False
    
    @staticmethod
    def save_to_json(data: List[Dict[str, Any]], filepath: str) -> bool:
        try:
            if not data:
                logger.warning("No data to save")
                return False
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.info(f"Data saved to JSON: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
            return False
    
    @staticmethod
    def save_to_txt(data: List[Dict[str, Any]], filepath: str) -> bool:
        try:
            if not data:
                logger.warning("No data to save")
                return False
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as txtfile:
                for i, item in enumerate(data, 1):
                    txtfile.write(f"结果 {i}:\n")
                    txtfile.write(f"标题: {item.get('title', '')}\n")
                    txtfile.write(f"摘要: {item.get('summary', '')}\n")
                    txtfile.write(f"链接: {item.get('url', '')}\n")
                    txtfile.write(f"发布时间: {item.get('publish_date', '')}\n")
                    txtfile.write("-" * 50 + "\n\n")
            
            logger.info(f"Data saved to TXT: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save TXT: {e}")
            return False
    
    @staticmethod
    def read_queries_from_file(filepath: str) -> List[str]:
        try:
            if not os.path.exists(filepath):
                logger.error(f"Input file not found: {filepath}")
                return []
            
            queries = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        queries.append(line)
            
            logger.info(f"Read {len(queries)} queries from {filepath}")
            return queries
        except Exception as e:
            logger.error(f"Failed to read queries from file: {e}")
            return []
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        return os.path.splitext(filepath)[1].lower().lstrip('.')
    
    @staticmethod
    def format_results_for_display(results: List[Dict[str, Any]]) -> str:
        if not results:
            return "未找到相关公告信息。"
        
        output_lines = []
        output_lines.append(f"找到 {len(results)} 条相关公告：")
        output_lines.append("=" * 60)
        
        for i, result in enumerate(results, 1):
            output_lines.append(f"{i}. {result.get('title', '')}")
            output_lines.append(f"   摘要: {result.get('summary', '')}")
            output_lines.append(f"   发布时间: {result.get('publish_date', '')}")
            output_lines.append(f"   链接: {result.get('url', '')}")
            output_lines.append("-" * 40)
        
        output_lines.append("数据来源：同花顺问财")
        return "\n".join(output_lines)
    
    @staticmethod
    def calculate_execution_time(start_time: float) -> float:
        return time.time() - start_time
    
    @staticmethod
    def format_execution_time(seconds: float) -> str:
        if seconds < 1:
            return f"{seconds*1000:.0f}毫秒"
        elif seconds < 60:
            return f"{seconds:.1f}秒"
        else:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"

if __name__ == "__main__":
    Utils.setup_logging()
    logger.info("Utils module loaded successfully")
    
    test_data = [
        {
            "title": "测试公告标题",
            "summary": "测试公告摘要",
            "url": "https://example.com/test",
            "publish_date": "2024-01-01 10:00:00"
        }
    ]
    
    print("Testing CSV save:")
    Utils.save_to_csv(test_data, "test_output.csv")
    
    print("\nTesting JSON save:")
    Utils.save_to_json(test_data, "test_output.json")
    
    print("\nTesting TXT save:")
    Utils.save_to_txt(test_data, "test_output.txt")
    
    print("\nTesting display formatting:")
    print(Utils.format_results_for_display(test_data))