#!/usr/bin/env python3
"""
公告搜索工具使用示例
"""

import os
import sys
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils import Utils
from announcement_search import AnnouncementSearch

def setup_environment():
    """设置环境"""
    print("=" * 60)
    print("公告搜索工具使用示例")
    print("=" * 60)
    
    # 检查API Key
    api_key = os.getenv("IWENCAI_API_KEY")
    if not api_key:
        print("警告: IWENCAI_API_KEY 环境变量未设置")
        print("请设置环境变量: export IWENCAI_API_KEY='your_api_key'")
        return False
    
    print(f"✓ API Key 已设置")
    print(f"✓ 配置验证: {'通过' if config.validate() else '失败'}")
    return True

def example_basic_search():
    """示例1: 基本搜索"""
    print("\n" + "=" * 60)
    print("示例1: 基本搜索")
    print("=" * 60)
    
    search = AnnouncementSearch()
    
    # 搜索贵州茅台公告
    query = "贵州茅台 公告"
    print(f"搜索: {query}")
    
    start_time = time.time()
    success, results, message = search.search(query, limit=5)
    execution_time = time.time() - start_time
    
    if success:
        print(f"状态: {message}")
        print(f"找到 {len(results)} 条结果")
        print(f"执行时间: {execution_time:.2f}秒")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title', '')}")
            print(f"   发布时间: {result.get('publish_date', '')}")
            print(f"   摘要: {result.get('summary', '')[:80]}...")
    else:
        print(f"错误: {message}")

def example_multiple_queries():
    """示例2: 多个查询"""
    print("\n" + "=" * 60)
    print("示例2: 多个查询")
    print("=" * 60)
    
    search = AnnouncementSearch()
    
    queries = [
        "上市公司业绩预告",
        "分红派息公告",
        "回购增持公告"
    ]
    
    for query in queries:
        print(f"\n搜索: {query}")
        
        success, results, message = search.search(query, limit=3)
        
        if success:
            print(f"  找到 {len(results)} 条结果")
            if results:
                print(f"  最新公告: {results[0].get('title', '')}")
        else:
            print(f"  错误: {message}")
        
        time.sleep(1)  # 避免请求过于频繁

def example_smart_query_analysis():
    """示例3: 智能查询分析"""
    print("\n" + "=" * 60)
    print("示例3: 智能查询分析")
    print("=" * 60)
    
    search = AnnouncementSearch()
    
    complex_queries = [
        "贵州茅台和五粮液最近有什么公告",
        "查看宁德时代、比亚迪的业绩预告",
        "搜索分红和回购相关的公告"
    ]
    
    for query in complex_queries:
        print(f"\n原始查询: {query}")
        
        analyzed_queries = search.smart_query_analysis(query)
        print(f"分析后的查询: {analyzed_queries}")
        
        # 执行第一个分析后的查询作为示例
        if analyzed_queries:
            success, results, message = search.search(analyzed_queries[0], limit=2)
            if success:
                print(f"  示例结果: 找到 {len(results)} 条相关公告")

def example_batch_processing():
    """示例4: 批量处理"""
    print("\n" + "=" * 60)
    print("示例4: 批量处理")
    print("=" * 60)
    
    # 创建测试查询文件
    test_queries = [
        "# 测试查询文件",
        "贵州茅台 公告",
        "中国平安 分红",
        "宁德时代 业绩预告",
        "",
        "# 空行会被忽略",
        "回购增持"
    ]
    
    queries_file = "test_queries.txt"
    with open(queries_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(test_queries))
    
    print(f"创建测试查询文件: {queries_file}")
    
    # 读取查询文件
    queries = Utils.read_queries_from_file(queries_file)
    print(f"读取到 {len(queries)} 个查询:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    
    # 清理测试文件
    os.remove(queries_file)
    print(f"已清理测试文件")

def example_data_export():
    """示例5: 数据导出"""
    print("\n" + "=" * 60)
    print("示例5: 数据导出")
    print("=" * 60)
    
    # 创建测试数据
    test_data = [
        {
            "title": "某某公司2023年度业绩预告",
            "summary": "公司预计2023年度净利润同比增长50%-70%",
            "url": "https://example.com/announcement/12345",
            "publish_date": "2024-01-15 09:30:00"
        },
        {
            "title": "另一家公司重大合同公告",
            "summary": "公司与客户签订重大销售合同，金额约10亿元",
            "url": "https://example.com/announcement/12346",
            "publish_date": "2024-01-14 16:45:00"
        }
    ]
    
    # 导出为不同格式
    formats = ["csv", "json", "txt"]
    
    for fmt in formats:
        filename = f"test_output.{fmt}"
        
        if fmt == "csv":
            success = Utils.save_to_csv(test_data, filename)
        elif fmt == "json":
            success = Utils.save_to_json(test_data, filename)
        elif fmt == "txt":
            success = Utils.save_to_txt(test_data, filename)
        
        if success:
            print(f"✓ 数据已导出为 {fmt.upper()} 格式: {filename}")
            
            # 显示文件内容预览
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  文件大小: {len(content)} 字节")
                    
                    # 清理测试文件
                    os.remove(filename)
            except:
                pass
        else:
            print(f"✗ 导出为 {fmt.upper()} 格式失败")

def example_error_handling():
    """示例6: 错误处理"""
    print("\n" + "=" * 60)
    print("示例6: 错误处理")
    print("=" * 60)
    
    search = AnnouncementSearch()
    
    # 测试无效查询
    invalid_queries = [
        "",  # 空查询
        "a",  # 太短的查询
        "   ",  # 只有空格的查询
    ]
    
    for query in invalid_queries:
        print(f"\n测试查询: '{query}'")
        
        if Utils.validate_query(query):
            success, results, message = search.search(query)
            print(f"  结果: {message}")
        else:
            print(f"  验证失败: 查询无效")

def main():
    """主函数"""
    if not setup_environment():
        print("环境设置失败，请检查配置")
        return
    
    try:
        example_basic_search()
        example_multiple_queries()
        example_smart_query_analysis()
        example_batch_processing()
        example_data_export()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        print("\n更多使用方式:")
        print("1. 使用命令行: announcement-search --help")
        print("2. 查看详细文档: 参考 README.md 和 SKILL.md")
        print("3. 数据来源: 同花顺问财")
        
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()