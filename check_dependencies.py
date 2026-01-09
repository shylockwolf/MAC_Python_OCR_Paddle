#!/usr/bin/env python3
"""
测试 PDF OCR 应用
运行这个脚本可以快速测试应用是否能够正常启动
"""

import sys
import os

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_modules = ['tkinter', 'paddleocr', 'pymupdf', 'PIL']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'paddleocr':
                from paddleocr import PaddleOCR
            elif module == 'pymupdf':
                import fitz
            elif module == 'PIL':
                from PIL import Image
            print(f"✓ {module} 已安装")
        except ImportError:
            print(f"✗ {module} 未安装")
            missing_modules.append(module)
    
    return missing_modules

if __name__ == "__main__":
    print("检查依赖...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n缺少以下依赖: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n所有依赖都已安装，可以运行应用了！")
        print("运行命令: python3 pdf_ocr_app.py")