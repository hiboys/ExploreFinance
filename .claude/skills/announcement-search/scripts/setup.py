#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

def read_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="announcement-search",
    version="1.0.0",
    description="金融公告搜索工具 - 搜索A股、港股、基金、ETF等金融标的公告",
    long_description=read_file('../README.md'),
    long_description_content_type="text/markdown",
    author="公告搜索技能开发团队",
    author_email="",
    url="",
    packages=find_packages(),
    py_modules=[
        'config',
        'utils',
        'announcement_search'
    ],
    scripts=['__main__.py'],
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'announcement-search=__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='finance, announcement, search, stock, fund, etf',
    project_urls={
        'Documentation': 'https://github.com/example/announcement-search',
        'Source': 'https://github.com/example/announcement-search',
        'Tracker': 'https://github.com/example/announcement-search/issues',
    },
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
)

if __name__ == "__main__":
    print("公告搜索工具安装脚本")
    print("=" * 40)
    print("安装方法:")
    print("1. 基本安装: pip install -e .")
    print("2. 开发安装: pip install -e .[dev]")
    print("3. 生产安装: pip install .")
    print()
    print("安装后可以使用: announcement-search --help")