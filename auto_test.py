#!/usr/bin/env python3
"""
自动化测试脚本 - 使用中国农民调查.pdf测试OCR功能
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

from paddleocr import PaddleOCR
import fitz

class AutoTester:
    def __init__(self):
        self.pdf_path = Path("/Users/noone/Downloads/Program/TestAPP/中国农民调查.pdf")
        self.temp_dir = Path("temp_processing")
        self.output_dir = self.pdf_path.parent
        
        print("初始化 OCR 引擎...")
        self.ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
        print("OCR 引擎初始化完成")
        
    def clean_temp_dir(self):
        """清空临时目录"""
        self.temp_dir.mkdir(exist_ok=True)
        for item in self.temp_dir.iterdir():
            if item.is_file():
                item.unlink()
        print("已清空临时目录")
        
    def convert_pdf(self):
        """执行PDF转换"""
        print(f"\n开始转换: {self.pdf_path.name}")
        
        self.clean_temp_dir()
        
        doc = fitz.open(str(self.pdf_path))
        total_pages = len(doc)
        print(f"PDF 共有 {total_pages} 页")
        
        all_results = []
        total_lines = 0
        total_chars = 0
        confidence_sum = 0
        
        params = {
            "name": self.pdf_path.stem,
            "description": "自动化测试生成",
            "params": {
                "use_textline_orientation": True,
                "lang": "ch"
            }
        }
        
        print("\n开始逐页处理...")
        
        for page_num in range(total_pages):
            print(f"\n[进度 {page_num + 1}/{total_pages}] 正在处理第 {page_num + 1} 页...")
            
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_path = self.temp_dir / f"page_{page_num + 1:03d}.png"
            pix.save(img_path)
            print(f"  - 已保存图像: {img_path.name}")
            
            print(f"  - 正在识别文本...")
            result = self.ocr.predict(str(img_path))
            
            page_text_lines = []
            page_confidences = []
            
            if result and len(result) > 0:
                ocr_result = result[0]
                rec_texts = ocr_result.get('rec_texts', [])
                rec_scores = ocr_result.get('rec_scores', [])
                rec_polys = ocr_result.get('rec_polys', [])
                
                for i, text in enumerate(rec_texts):
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    bbox = rec_polys[i].tolist() if i < len(rec_polys) else []
                    
                    page_text_lines.append(text)
                    page_confidences.append(confidence)
                    
                    print(f"  - 识别到: {text}")
                    
                    total_lines += 1
                    total_chars += len(text)
                    confidence_sum += confidence
            
            if page_confidences:
                avg_page_conf = sum(page_confidences) / len(page_confidences)
            else:
                avg_page_conf = 0
            
            print(f"  - 本页识别 {len(page_text_lines)} 行，平均置信度: {avg_page_conf:.4f}")
            
            page_result = {
                "image": f"page_{page_num + 1:03d}.png",
                "text_lines": [],
                "page_number": page_num + 1,
                "average_confidence": avg_page_conf,
                "lines_count": len(page_text_lines)
            }
            
            if result and len(result) > 0:
                ocr_result = result[0]
                rec_texts = ocr_result.get('rec_texts', [])
                rec_scores = ocr_result.get('rec_scores', [])
                rec_polys = ocr_result.get('rec_polys', [])
                
                for i, text in enumerate(rec_texts):
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    bbox = rec_polys[i].tolist() if i < len(rec_polys) else []
                    
                    page_result["text_lines"].append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
            
            all_results.append(page_result)
            
            time.sleep(0.1)
        
        doc.close()
        
        avg_confidence = confidence_sum / total_lines if total_lines > 0 else 0
        
        params["metrics"] = {
            "total_pages": total_pages,
            "valid_pages": len([r for r in all_results if r["lines_count"] > 0]),
            "total_lines": total_lines,
            "total_chars": total_chars,
            "avg_confidence": float(avg_confidence),
            "chars_per_line": total_chars / total_lines if total_lines > 0 else 0,
            "lines_per_page": total_lines / total_pages if total_pages > 0 else 0,
            "success_rate": len([r for r in all_results if r["lines_count"] > 0]) / total_pages if total_pages > 0 else 0
        }
        params["score"] = float(avg_confidence * 100)
        params["timestamp"] = datetime.now().isoformat()
        
        results_path = self.temp_dir / "detailed_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n已保存详细结果: {results_path}")
        
        params_path = self.temp_dir / "test_params.json"
        with open(params_path, 'w', encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
        print(f"已保存参数配置: {params_path}")
        
        all_text = []
        for page_result in all_results:
            for line in page_result["text_lines"]:
                all_text.append(line["text"])
        
        output_text_path = self.output_dir / f"{self.pdf_path.stem}.txt"
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_text))
        print(f"\n已保存文本文件: {output_text_path}")
        
        return total_lines, total_chars, all_text
        
    def print_summary(self, total_lines, total_chars, all_text):
        """打印转换摘要"""
        print("\n" + "="*80)
        print("转换完成！")
        print("="*80)
        print(f"总识别行数: {total_lines}")
        print(f"总字符数: {total_chars}")
        print(f"\n前10行识别结果:")
        print("-"*80)
        for i, line in enumerate(all_text[:10]):
            print(f"{i+1}. {line}")
        print("-"*80)
        print(f"\n完整文本已保存到: {self.output_dir / f'{self.pdf_path.stem}.txt'}")
        print("="*80)

def main():
    try:
        tester = AutoTester()
        total_lines, total_chars, all_text = tester.convert_pdf()
        tester.print_summary(total_lines, total_chars, all_text)
        
        if total_lines > 10:
            print("\n✓ 测试成功！成功识别出大段中文文本")
            return 0
        else:
            print("\n✗ 测试失败！识别的文本行数太少")
            return 1
            
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())