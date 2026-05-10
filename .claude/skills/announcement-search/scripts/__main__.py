#!/usr/bin/env python3
import argparse
import sys
import os
import time
from typing import List, Dict, Any

from config import config
from utils import Utils
from announcement_search import AnnouncementSearch

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="公告搜索工具 - 搜索A股、港股、基金、ETF等金融标的公告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s "贵州茅台 公告"                    # 基本搜索
  %(prog)s "上市公司业绩预告" --limit 5       # 限制结果数量
  %(prog)s "分红派息" --format json          # 指定输出格式
  %(prog)s --input queries.txt --output results.csv  # 批量搜索
  %(prog)s --help                            # 显示帮助信息

数据来源: 同花顺问财
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="搜索关键词，例如：'贵州茅台 公告'、'上市公司业绩预告'"
    )
    
    parser.add_argument(
        "-i", "--input",
        help="输入文件路径，包含多个查询（每行一个）"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径，保存搜索结果"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json", "txt"],
        default=config.get_output_config()["default_format"],
        help="输出格式（默认: %(default)s）"
    )
    
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=config.get_search_config()["default_limit"],
        help="每个查询的结果数量限制（默认: %(default)d）"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"公告搜索工具 v{config.get_skill_config()['version']}"
    )
    
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    
    return parser.parse_args()

def show_platform_help():
    print("\n跨平台环境变量设置说明:")
    print("=" * 50)
    print("macOS / Linux (bash/zsh):")
    print("  export IWENCAI_API_KEY=\"your_api_key_here\"")
    print()
    print("Windows (PowerShell):")
    print("  $env:IWENCAI_API_KEY=\"your_api_key_here\"")
    print()
    print("Windows (CMD):")
    print("  set IWENCAI_API_KEY=your_api_key_here")
    print()
    print("获取API Key:")
    print("1. 访问 https://www.iwencai.com/skillhub")
    print("2. 登录您的账户")
    print("3. 选择公告搜索技能，复制API Key")
    print("=" * 50)

def validate_arguments(args):
    if not args.query and not args.input:
        print("错误: 必须提供查询关键词或输入文件")
        return False
    
    if args.limit > config.get_search_config()["max_limit"]:
        print(f"警告: 结果数量限制超过最大值 {config.get_search_config()['max_limit']}，已自动调整")
        args.limit = config.get_search_config()["max_limit"]
    
    if args.output and args.format not in config.get_output_config()["supported_formats"]:
        print(f"错误: 不支持的输出格式 '{args.format}'")
        print(f"支持的格式: {', '.join(config.get_output_config()['supported_formats'])}")
        return False
    
    return True

def save_results(results: List[Dict[str, Any]], args):
    if not args.output:
        return True
    
    file_ext = Utils.get_file_extension(args.output)
    
    if file_ext != args.format:
        new_output = f"{os.path.splitext(args.output)[0]}.{args.format}"
        print(f"警告: 输出文件扩展名与格式不匹配，已自动调整为: {new_output}")
        args.output = new_output
    
    if args.format == "csv":
        return Utils.save_to_csv(results, args.output)
    elif args.format == "json":
        return Utils.save_to_json(results, args.output)
    elif args.format == "txt":
        return Utils.save_to_txt(results, args.output)
    else:
        print(f"错误: 不支持的输出格式 '{args.format}'")
        return False

def display_results(results: List[Dict[str, Any]], query: str, execution_time: float):
    if not results:
        print(f"\n对于查询 '{query}'，未找到相关公告信息。")
        return
    
    print(f"\n搜索完成！")
    print(f"查询: {query}")
    print(f"找到 {len(results)} 条相关公告")
    print(f"执行时间: {Utils.format_execution_time(execution_time)}")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', '')}")
        
        if args.verbose:
            print(f"   摘要: {result.get('summary', '')}")
            print(f"   发布时间: {result.get('publish_date', '')}")
            print(f"   链接: {result.get('url', '')}")
        else:
            summary = result.get('summary', '')
            if len(summary) > 100:
                summary = summary[:100] + "..."
            print(f"   摘要: {summary}")
            print(f"   发布时间: {result.get('publish_date', '')}")
        
        print()

def main():
    global args
    args = parse_arguments()
    
    if not validate_arguments(args):
        sys.exit(1)
    
    log_level = "DEBUG" if args.verbose else "INFO"
    Utils.setup_logging(log_level)
    
    if not config.validate():
        print("错误: 配置验证失败")
        print("请检查 IWENCAI_API_KEY 环境变量是否设置")
        print()
        show_platform_help()
        sys.exit(1)
    
    search = AnnouncementSearch()
    
    all_results = []
    
    if args.input:
        queries = Utils.read_queries_from_file(args.input)
        if not queries:
            print(f"错误: 无法从文件读取查询: {args.input}")
            sys.exit(1)
        
        print(f"开始批量搜索，共 {len(queries)} 个查询")
        
        batch_results = search.batch_search(queries, args.limit)
        
        for query, (success, results, message) in batch_results.items():
            if success:
                all_results.extend(results)
                print(f"✓ {query}: 找到 {len(results)} 条结果")
            else:
                print(f"✗ {query}: {message}")
        
        if args.output:
            save_success = save_results(all_results, args)
            if save_success:
                print(f"\n所有结果已保存到: {args.output}")
        
        print(f"\n批量搜索完成，总共找到 {len(all_results)} 条公告")
        print("数据来源：同花顺问财")
        
    else:
        start_time = time.time()
        
        success, results, message = search.search(args.query, args.limit)
        
        execution_time = Utils.calculate_execution_time(start_time)
        
        if success:
            all_results = results
            
            if args.output:
                save_success = save_results(all_results, args)
                if save_success:
                    print(f"结果已保存到: {args.output}")
            
            display_results(all_results, args.query, execution_time)
            
            if results:
                print("数据来源：同花顺问财")
        else:
            print(f"\n搜索失败: {message}")
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n发生错误: {e}")
        if args and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)