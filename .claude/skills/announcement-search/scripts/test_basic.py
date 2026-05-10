#!/usr/bin/env python3
"""
公告搜索工具基本测试
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils import Utils
from announcement_search import AnnouncementSearch

class TestConfig(unittest.TestCase):
    def test_config_initialization(self):
        """测试配置初始化"""
        config = Config()
        self.assertIsNotNone(config.config)
        
        # 检查基本配置项
        self.assertIn("api", config.config)
        self.assertIn("auth", config.config)
        self.assertIn("search", config.config)
    
    def test_get_api_key(self):
        """测试获取API Key"""
        config = Config()
        
        # 测试环境变量中的API Key
        with patch.dict(os.environ, {"IWENCAI_API_KEY": "test_key"}):
            config = Config()
            api_key = config.get_api_key()
            self.assertEqual(api_key, "test_key")
        
        # 测试缺少API Key的情况
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            with self.assertRaises(ValueError):
                config.get_api_key()
    
    def test_validate_config(self):
        """测试配置验证"""
        config = Config()
        
        # 测试有效配置
        with patch.dict(os.environ, {"IWENCAI_API_KEY": "valid_key"}):
            config = Config()
            self.assertTrue(config.validate())
        
        # 测试无效配置（缺少API Key）
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            self.assertFalse(config.validate())

class TestUtils(unittest.TestCase):
    def test_validate_query(self):
        """测试查询验证"""
        # 有效查询
        self.assertTrue(Utils.validate_query("贵州茅台"))
        self.assertTrue(Utils.validate_query("上市公司业绩预告"))
        
        # 无效查询
        self.assertFalse(Utils.validate_query(""))
        self.assertFalse(Utils.validate_query("  "))
        self.assertFalse(Utils.validate_query("a"))
    
    def test_generate_cache_key(self):
        """测试缓存键生成"""
        key1 = Utils.generate_cache_key("test query", 10)
        key2 = Utils.generate_cache_key("test query", 10)
        key3 = Utils.generate_cache_key("different query", 10)
        
        # 相同查询应生成相同键
        self.assertEqual(key1, key2)
        
        # 不同查询应生成不同键
        self.assertNotEqual(key1, key3)
    
    def test_save_to_csv(self):
        """测试保存为CSV"""
        test_data = [
            {"title": "测试标题1", "summary": "测试摘要1", "url": "http://test1.com", "publish_date": "2024-01-01 10:00:00"},
            {"title": "测试标题2", "summary": "测试摘要2", "url": "http://test2.com", "publish_date": "2024-01-02 11:00:00"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success = Utils.save_to_csv(test_data, tmp_path)
            self.assertTrue(success)
            
            # 验证文件内容
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("测试标题1", content)
                self.assertIn("测试标题2", content)
                self.assertIn("title,summary,url,publish_date", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_save_to_json(self):
        """测试保存为JSON"""
        test_data = [
            {"title": "测试标题", "summary": "测试摘要", "url": "http://test.com", "publish_date": "2024-01-01 10:00:00"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success = Utils.save_to_json(test_data, tmp_path)
            self.assertTrue(success)
            
            # 验证文件内容
            with open(tmp_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                self.assertEqual(len(loaded_data), 1)
                self.assertEqual(loaded_data[0]["title"], "测试标题")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_read_queries_from_file(self):
        """测试从文件读取查询"""
        test_queries = [
            "# 注释行",
            "查询1",
            "",
            "查询2",
            " 查询3 "  # 带空格的查询
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("\n".join(test_queries))
            tmp_path = tmp.name
        
        try:
            queries = Utils.read_queries_from_file(tmp_path)
            
            # 应该读取3个查询（忽略注释行和空行）
            self.assertEqual(len(queries), 3)
            self.assertIn("查询1", queries)
            self.assertIn("查询2", queries)
            self.assertIn("查询3", queries)  # 空格应该被去除
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_format_results_for_display(self):
        """测试结果格式化显示"""
        test_results = [
            {"title": "测试标题1", "summary": "测试摘要1", "url": "http://test1.com", "publish_date": "2024-01-01 10:00:00"},
            {"title": "测试标题2", "summary": "测试摘要2", "url": "http://test2.com", "publish_date": "2024-01-02 11:00:00"}
        ]
        
        formatted = Utils.format_results_for_display(test_results)
        
        # 检查基本内容
        self.assertIn("找到 2 条相关公告", formatted)
        self.assertIn("测试标题1", formatted)
        self.assertIn("测试标题2", formatted)
        self.assertIn("数据来源：同花顺问财", formatted)
        
        # 测试空结果
        empty_formatted = Utils.format_results_for_display([])
        self.assertEqual(empty_formatted, "未找到相关公告信息。")

class TestAnnouncementSearch(unittest.TestCase):
    def setUp(self):
        """测试前置设置"""
        self.search = AnnouncementSearch()
    
    def test_smart_query_analysis(self):
        """测试智能查询分析"""
        # 测试简单查询
        queries = self.search.smart_query_analysis("贵州茅台")
        self.assertEqual(queries, ["贵州茅台"])
        
        # 测试包含"和"的查询
        queries = self.search.smart_query_analysis("贵州茅台和五粮液")
        self.assertIn("贵州茅台 公告", queries)
        self.assertIn("五粮液 公告", queries)
        
        # 测试包含"与"的查询
        queries = self.search.smart_query_analysis("宁德时代与比亚迪")
        self.assertIn("宁德时代 公告", queries)
        self.assertIn("比亚迪 公告", queries)
        
        # 测试包含"、"的查询
        queries = self.search.smart_query_analysis("中国平安、中国人寿")
        self.assertIn("中国平安 公告", queries)
        self.assertIn("中国人寿 公告", queries)
    
    def test_evaluate_results(self):
        """测试结果评估"""
        test_results = [
            {"title": "贵州茅台2023年度业绩预告", "summary": "公司预计2023年度净利润增长"},
            {"title": "五粮液分红公告", "summary": "公司宣布年度分红方案"},
            {"title": "无关公告", "summary": "其他内容"}
        ]
        
        # 测试高相关性
        relevant, evaluation = self.search.evaluate_results("贵州茅台 业绩预告", test_results)
        self.assertTrue(relevant)
        self.assertIn("较高", evaluation)
        
        # 测试低相关性
        relevant, evaluation = self.search.evaluate_results("完全无关的查询", test_results)
        self.assertFalse(relevant)
        self.assertIn("较低", evaluation)
    
    def test_generate_search_summary(self):
        """测试搜索摘要生成"""
        test_results = [
            {"title": "标题1", "summary": "摘要1", "url": "http://test1.com", "publish_date": "2024-01-01 10:00:00"},
            {"title": "标题2", "summary": "摘要2", "url": "http://test2.com", "publish_date": "2024-01-02 11:00:00"},
            {"title": "标题3", "summary": "摘要3", "url": "http://test3.com", "publish_date": "2024-01-03 12:00:00"},
            {"title": "标题4", "summary": "摘要4", "url": "http://test4.com", "publish_date": "2024-01-04 13:00:00"},
            {"title": "标题5", "summary": "摘要5", "url": "http://test5.com", "publish_date": "2024-01-05 14:00:00"},
            {"title": "标题6", "summary": "摘要6", "url": "http://test6.com", "publish_date": "2024-01-06 15:00:00"}
        ]
        
        summary = self.search.generate_search_summary("测试查询", test_results)
        
        # 检查基本内容
        self.assertIn("测试查询", summary)
        self.assertIn("找到 6 条相关公告", summary)
        self.assertIn("标题1", summary)
        self.assertIn("标题5", summary)
        self.assertIn("还有 1 条结果", summary)  # 只显示前5条
        self.assertIn("数据来源：同花顺问财", summary)
        
        # 测试空结果
        empty_summary = self.search.generate_search_summary("空查询", [])
        self.assertIn("未找到相关公告信息", empty_summary)
    
    @patch('announcement_search.requests.post')
    def test_search_success(self, mock_post):
        """测试成功搜索"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"title": "测试公告1", "summary": "测试摘要1", "url": "http://test1.com", "publish_date": "2024-01-01 10:00:00"},
                {"title": "测试公告2", "summary": "测试摘要2", "url": "http://test2.com", "publish_date": "2024-01-02 11:00:00"}
            ]
        }
        mock_post.return_value = mock_response
        
        success, results, message = self.search.search("测试查询", limit=2)
        
        self.assertTrue(success)
        self.assertEqual(len(results), 2)
        self.assertEqual(message, "搜索成功")
        self.assertEqual(results[0]["title"], "测试公告1")
        self.assertEqual(results[1]["title"], "测试公告2")
    
    @patch('announcement_search.requests.post')
    def test_search_empty_results(self, mock_post):
        """测试空结果搜索"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_post.return_value = mock_response
        
        success, results, message = self.search.search("测试查询")
        
        self.assertTrue(success)
        self.assertEqual(len(results), 0)
        self.assertEqual(message, "未找到相关公告")
    
    @patch('announcement_search.requests.post')
    def test_search_auth_failure(self, mock_post):
        """测试认证失败"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        success, results, message = self.search.search("测试查询")
        
        self.assertFalse(success)
        self.assertEqual(len(results), 0)
        self.assertIn("API认证失败", message)
    
    @patch('announcement_search.requests.post')
    def test_search_network_error(self, mock_post):
        """测试网络错误"""
        mock_post.side_effect = ConnectionError("网络连接错误")
        
        success, results, message = self.search.search("测试查询")
        
        self.assertFalse(success)
        self.assertEqual(len(results), 0)
        self.assertIn("网络连接错误", message)

def run_tests():
    """运行所有测试"""
    print("运行公告搜索工具测试...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestAnnouncementSearch))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print(f"测试完成: {result.testsRun} 个测试用例")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # 设置环境变量用于测试
    os.environ["IWENCAI_API_KEY"] = "test_key_for_unit_tests"
    os.environ["LOG_LEVEL"] = "ERROR"  # 测试时减少日志输出
    
    success = run_tests()
    sys.exit(0 if success else 1)