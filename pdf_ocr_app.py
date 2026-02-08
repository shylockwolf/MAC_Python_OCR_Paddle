#!/usr/bin/env python3
import os
import json
import time
import base64
import re
from pathlib import Path
from datetime import datetime
from threading import Thread

import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from PIL import Image
from paddleocr import PaddleOCR
import fitz
import requests
from dotenv import load_dotenv

load_dotenv()

class PDFOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF OCR 转换工具")
        self.root.geometry("900x700")
        
        self.pdf_path = None
        self.output_dir = None
        self.temp_dir = Path("temp_processing")
        self.ocr = None
        self.is_converting = False
        self.stop_requested = False
        
        self.setup_ui()
        self.init_ocr()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="wens")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        ttk.Label(main_frame, text="PDF 文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.file_label = ttk.Label(main_frame, text="未选择文件", relief="sunken", width=60)
        self.file_label.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        ttk.Button(main_frame, text="选择文件", command=self.select_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="OCR 模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.ocr_mode = tk.StringVar(value="local")
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="本地模型", variable=self.ocr_mode, value="local").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="API 模式", variable=self.ocr_mode, value="api").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(main_frame, text="开始转换", command=self.start_conversion).grid(row=2, column=1, pady=10, padx=5)
        
        self.stop_button = ttk.Button(main_frame, text="停止转换", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=2, pady=10)
        
        ttk.Label(main_frame, text="转换进度:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=1, columnspan=2, sticky="we", padx=5, pady=5)
        
        self.status_label = ttk.Label(main_frame, text="准备就绪")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        split_frame = ttk.Frame(main_frame)
        split_frame.grid(row=5, column=0, columnspan=3, sticky="wens", pady=5)
        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=2)
        split_frame.rowconfigure(0, weight=1)
        
        ttk.Label(split_frame, text="识别文本:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.text_display = scrolledtext.ScrolledText(split_frame, wrap=tk.WORD)
        self.text_display.grid(row=1, column=0, sticky="wens", padx=(0, 5))
        
        ttk.Label(split_frame, text="正在处理的图像:").grid(row=0, column=1, sticky=tk.W, pady=5)
        self.image_frame = ttk.Frame(split_frame, relief="sunken", borderwidth=1)
        self.image_frame.grid(row=1, column=1, sticky="wens")
        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.rowconfigure(0, weight=1)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        main_frame.rowconfigure(5, weight=1)
        
    def init_ocr(self):
        try:
            self.ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
            self.update_status("OCR 引擎初始化成功")
        except Exception as e:
            self.update_status(f"OCR 初始化失败: {str(e)}")
            
    def call_ocr_api(self, file_path):
        api_url = os.getenv('PADDLEOCR_API_URL')
        token = os.getenv('PADDLEOCR_API_KEY')
        
        if not api_url or not token:
            raise Exception("API URL 或 Token 未配置，请检查 .env 文件")
        
        with open(file_path, "rb") as file:
            file_bytes = file.read()
            file_data = base64.b64encode(file_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }
        
        required_payload = {
            "file": file_data,
            "fileType": 1
        }
        
        optional_payload = {
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
        }
        
        payload = {**required_payload, **optional_payload}
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"API 调用失败，状态码: {response.status_code}")
        
        result = response.json().get("result", {})
        return result
    
    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
            
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf")]
        )
        
        if file_path:
            self.pdf_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.update_status(f"已选择: {os.path.basename(file_path)}")
            
            self.temp_dir.mkdir(exist_ok=True)
            for item in self.temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    
            self.text_display.delete(1.0, tk.END)
            self.progress['value'] = 0
            
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
        
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update()
        
    def append_text(self, text):
        self.text_display.insert(tk.END, text + "\n")
        self.text_display.see(tk.END)
        self.root.update()
        
    def update_image(self, image_path):
        try:
            img = Image.open(image_path)
            
            # 获取图像框架的尺寸
            width = self.image_frame.winfo_width()
            height = self.image_frame.winfo_height()
            
            # 计算缩放比例，保持宽高比
            if width > 0 and height > 0:
                img_ratio = img.width / img.height
                frame_ratio = width / height
                
                if img_ratio > frame_ratio:
                    new_width = width
                    new_height = int(width / img_ratio)
                else:
                    new_height = height
                    new_width = int(height * img_ratio)
                
                # 缩放图像
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # 转换为tkinter可用的格式
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img)
                
                # 更新图像标签
                self.image_label.config(image=photo)
                self.image_label.image = photo  # 保持引用，防止被垃圾回收
                self.root.update()
        except Exception as e:
            print(f"更新图像失败: {str(e)}")
        
    def start_conversion(self):
        if not self.pdf_path:
            self.update_status("请先选择 PDF 文件")
            return
            
        if self.is_converting:
            self.update_status("转换正在进行中...")
            return
            
        self.is_converting = True
        self.stop_requested = False
        self.stop_button.config(state=tk.NORMAL)
        thread = Thread(target=self.convert_pdf)
        thread.daemon = True
        thread.start()
        
    def stop_conversion(self):
        if self.is_converting:
            self.stop_requested = True
            self.update_status("正在停止转换...")
        
    def convert_pdf(self):
        try:
            if not self.pdf_path:
                self.update_status("PDF 文件路径未设置")
                return
            
            mode = self.ocr_mode.get()
            
            if mode == "local" and not self.ocr:
                self.update_status("OCR 引擎未初始化")
                return
            
            pdf_path = Path(self.pdf_path)
            pdf_name = pdf_path.stem
            parent_dir = pdf_path.parent
            
            self.temp_dir.mkdir(exist_ok=True)
            self.update_status("正在读取 PDF 文件...")
            
            doc = fitz.open(str(self.pdf_path))
            total_pages = len(doc)
            
            all_results = []
            total_lines = 0
            total_chars = 0
            confidence_sum = 0
            
            params = {
                "name": pdf_name,
                "description": "通过 GUI 应用生成",
                "mode": mode,
                "params": {
                    "use_textline_orientation": True,
                    "lang": "ch"
                }
            }
            
            for page_num in range(total_pages):
                if self.stop_requested:
                    self.update_status("转换已停止")
                    break
                    
                progress = (page_num + 1) / total_pages * 100
                self.update_progress(progress)
                self.update_status(f"正在处理第 {page_num + 1}/{total_pages} 页...")
                
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_path = self.temp_dir / f"page_{page_num + 1:03d}.png"
                pix.save(img_path)
                
                self.update_image(str(img_path))
                
                page_text_lines = []
                page_confidences = []
                
                if mode == "local":
                    self.update_status(f"正在识别第 {page_num + 1}/{total_pages} 页文本...")
                    result = self.ocr.predict(str(img_path))
                    
                    if result and len(result) > 0:
                        ocr_result = result[0]
                        rec_texts = ocr_result.get('rec_texts', [])
                        rec_scores = ocr_result.get('rec_scores', [])
                        rec_polys = ocr_result.get('rec_polys', [])
                        
                        for i, text in enumerate(rec_texts):
                            confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                            
                            page_text_lines.append(text)
                            page_confidences.append(confidence)
                            
                            if i == 0:
                                self.append_text(f"[第{page_num + 1}页] {text}")
                            else:
                                self.append_text(text)
                            
                            total_lines += 1
                            total_chars += len(text)
                            confidence_sum += confidence
                else:
                    self.update_status(f"正在通过 API 识别第 {page_num + 1}/{total_pages} 页...")
                    api_result = self.call_ocr_api(str(img_path))
                    
                    layout_results = api_result.get("layoutParsingResults", [])
                    
                    for layout_res in layout_results:
                        markdown_text = layout_res.get("markdown", {}).get("text", "")
                        if markdown_text:
                            lines = markdown_text.split('\n')
                            for i, line in enumerate(lines):
                                clean_line = self.remove_html_tags(line).strip()
                                if clean_line:
                                    page_text_lines.append(clean_line)
                                    page_confidences.append(1.0)
                                    
                                    if i == 0:
                                        self.append_text(f"[第{page_num + 1}页] {clean_line}")
                                    else:
                                        self.append_text(clean_line)
                                    
                                    total_lines += 1
                                    total_chars += len(clean_line)
                                    confidence_sum += 1.0
                
                if page_confidences:
                    avg_page_conf = sum(page_confidences) / len(page_confidences)
                else:
                    avg_page_conf = 0
                
                page_result = {
                    "image": f"page_{page_num + 1:03d}.png",
                    "text_lines": [],
                    "page_number": page_num + 1,
                    "average_confidence": avg_page_conf,
                    "lines_count": len(page_text_lines)
                }
                
                for i, text in enumerate(page_text_lines):
                    confidence = page_confidences[i] if i < len(page_confidences) else 0.0
                    
                    page_result["text_lines"].append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": []
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
            
            params_path = self.temp_dir / "test_params.json"
            with open(params_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=2)
            
            all_text = []
            for page_result in all_results:
                for line in page_result["text_lines"]:
                    all_text.append(line["text"])
            
            output_text_path = parent_dir / f"{pdf_name}.txt"
            with open(output_text_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
            
            self.update_progress(100)
            mode_text = "本地模型" if mode == "local" else "API"
            self.update_status(f"转换完成! ({mode_text}) 共识别 {total_lines} 行文本,保存到 {output_text_path}")
            
        except Exception as e:
            self.update_status(f"转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.is_converting = False
            self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    PDFOCRApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()