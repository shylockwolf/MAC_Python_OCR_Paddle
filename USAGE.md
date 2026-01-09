# PDF OCR 转换工具 - 使用说明

## 安装步骤

1. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **检查依赖是否安装成功**
   ```bash
   python3 check_dependencies.py
   ```

## 运行应用

```bash
python3 pdf_ocr_app.py
```

## 功能说明

### 界面介绍
- **PDF 文件**: 显示当前选择的 PDF 文件名
- **选择文件按钮**: 打开文件选择对话框，选择 PDF 文件
- **开始转换按钮**: 开始 OCR 转换过程
- **转换进度条**: 显示当前转换进度
- **状态标签**: 显示当前操作状态
- **识别文本窗口**: 实时显示识别出的文本

### 操作流程

1. 点击"选择文件"按钮，选择要转换的 PDF 文件
2. 选择文件后，临时处理目录 `temp_processing/` 会自动清空
3. 点击"开始转换"按钮开始转换
4. 转换过程中可以看到：
   - 进度条显示转换进度
   - 状态显示当前正在处理的页面
   - 识别的文本实时滚动显示在窗口中
5. 转换完成后，文本文件会保存在 PDF 文件同目录下

### 输出文件

#### 临时处理目录 (`temp_processing/`)
- `page_001.png`, `page_002.png`, ...: PDF 每一页的图像
- `detailed_results.json`: 详细的识别结果，包含每页的文本、置信度、坐标等信息
- `test_params.json`: 转换参数和统计信息

#### 最终输出文件
- `{pdf_name}.txt`: 识别出的文本，保存在 PDF 文件同目录下

### 配置参考

生成的 JSON 文件格式参考 `test_01_base/` 目录中的示例文件：
- `test_params.json`: 参数配置和统计信息
- `detailed_results.json`: 详细识别结果

## 注意事项

1. **中间文件保留**: `temp_processing/` 目录中的中间文件会保留，不会自动删除
2. **自动清空**: 每次选择新的 PDF 文件时，`temp_processing/` 目录会自动清空
3. **实时显示**: 识别的文本会实时显示在应用窗口中，方便查看转换进度
4. **OCR 引擎**: 使用 PaddleOCR 进行中文文本识别

## 故障排除

### OCR 引擎初始化失败
- 检查 PaddleOCR 是否正确安装
- 检查网络连接（首次运行需要下载模型）
- 确保有足够的磁盘空间存储模型文件

### 转换失败
- 检查 PDF 文件是否损坏
- 确认 PDF 文件包含可识别的文本或图像
- 查看错误信息了解具体问题

## 技术栈

- **GUI 框架**: Tkinter
- **OCR 引擎**: PaddleOCR
- **PDF 处理**: PyMuPDF (fitz)
- **图像处理**: Pillow (PIL)