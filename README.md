# PDF OCR 转换工具

使用 PaddleOCR 将 PDF 文件转换为文本的桌面应用程序。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python pdf_ocr_app.py
```

## 功能特性

1. 打开 PDF 文件
2. 点击转换按钮开始 OCR 识别
3. 实时显示转换进度和状态
4. 识别文本实时滚动显示
5. 中间文件保存在 temp_processing 目录
6. 生成的文本文件与 PDF 同目录
7. 转换完成后生成详细的识别结果和参数配置

## 输出文件

- `temp_processing/`: 中间处理文件目录
  - `page_*.png`: PDF 页面图像
  - `detailed_results.json`: 详细识别结果
  - `test_params.json`: 参数配置和统计信息
- `{pdf_name}.txt`: 最终识别的文本文件