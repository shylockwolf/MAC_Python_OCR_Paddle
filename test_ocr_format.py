#!/usr/bin/env python3
"""
测试 PaddleOCR 返回格式
"""
from paddleocr import PaddleOCR
import fitz

ocr = PaddleOCR(use_textline_orientation=True, lang='ch')

pdf_path = "/Users/noone/Downloads/Program/TestAPP/中国农民调查.pdf"
doc = fitz.open(pdf_path)
page = doc[0]

pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
img_path = "temp_processing/test_page.png"
pix.save(img_path)

print("测试 OCR 结果格式...")
result = ocr.predict(img_path)

print(f"\n结果类型: {type(result)}")
print(f"结果长度: {len(result) if hasattr(result, '__len__') else 'N/A'}")

if result:
    print(f"\n第一个元素: {result[0]}")
    print(f"第一个元素类型: {type(result[0])}")
    
    if len(result[0]) > 0:
        print(f"\n第一个结果项: {result[0][0]}")
        print(f"第一个结果项类型: {type(result[0][0])}")
        print(f"第一个结果项长度: {len(result[0][0])}")
        
        if len(result[0][0]) > 0:
            for i, item in enumerate(result[0][0]):
                print(f"  项 {i}: {item} (类型: {type(item)})")

doc.close()