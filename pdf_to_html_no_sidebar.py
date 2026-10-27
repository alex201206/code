#!/usr/bin/env python3
"""
PDF 转 HTML 并移除左侧导航栏脚本
功能：
1. 使用 pdf2htmlEX 将指定目录下所有 PDF 转换为 HTML
2. 注入 CSS 隐藏左侧导航栏（sidebar）
3. 调整主内容区占满宽度
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def find_pdf_files(directory):
    """查找目录下所有 PDF 文件"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def convert_pdf_to_html(pdf_path):
    """使用 pdf2htmlEX 转换单个 PDF 文件"""
    html_path = pdf_path.replace('.pdf', '.html')
    cmd = ['pdf2htmlEX', '--zoom', '1.3', pdf_path]
    
    print(f"正在转换: {os.path.basename(pdf_path)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"  警告: 转换过程有错误 (code={result.returncode})")
            if result.stderr:
                print(f"  stderr: {result.stderr[:200]}")
        return html_path
    except FileNotFoundError:
        print(f"  错误: 未找到 pdf2htmlEX 命令，请确保已安装")
        return None
    except Exception as e:
        print(f"  错误: {e}")
        return None

def remove_sidebar_from_html(html_path):
    """在 HTML 文件中注入 CSS 隐藏导航栏"""
    if not os.path.exists(html_path):
        print(f"  错误: HTML 文件不存在 {html_path}")
        return False
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 <head> 标签，在它后面注入 CSS
        head_pattern = r'(<head[^>]*>)'
        match = re.search(head_pattern, content, re.IGNORECASE)
        
        if not match:
            print(f"  警告: 未找到 <head> 标签，尝试在文件开头注入")
            # 在文件开头注入
            new_content = """<style>
#sidebar { display: none !important; }
#page-container { left: 0 !important; }
</style>
""" + content
        else:
            # 在 <head> 标签后注入
            head_end = match.end()
            new_content = content[:head_end] + """
<style>
#sidebar { display: none !important; }
#page-container { left: 0 !important; }
</style>
""" + content[head_end:]
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  已移除导航栏: {os.path.basename(html_path)}")
        return True
        
    except Exception as e:
        print(f"  处理 HTML 文件时出错: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python pdf_to_html_no_sidebar.py <目录路径>")
        print("示例: python pdf_to_html_no_sidebar.py C:\\Papers")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"错误: 目录不存在 {target_dir}")
        sys.exit(1)
    
    print(f"开始处理目录: {target_dir}")
    print("-" * 50)
    
    # 查找 PDF 文件
    pdf_files = find_pdf_files(target_dir)
    if not pdf_files:
        print("未找到 PDF 文件")
        sys.exit(0)
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件")
    
    success_count = 0
    fail_count = 0
    
    for pdf_file in pdf_files:
        print(f"\n处理: {os.path.basename(pdf_file)}")
        
        # 转换 PDF 到 HTML
        html_path = convert_pdf_to_html(pdf_file)
        if not html_path:
            fail_count += 1
            continue
        
        # 移除导航栏
        if remove_sidebar_from_html(html_path):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 50)
    print("处理完成:")
    print(f"  成功: {success_count} 个文件")
    print(f"  失败: {fail_count} 个文件")
    
    if success_count > 0:
        print(f"\n生成的 HTML 文件位于: {target_dir}")
        print("用浏览器打开任意 .html 文件查看效果")

if __name__ == "__main__":
    main()