# SVS Label OCR

`SVS Label OCR` 是一个面向病理切片 `.svs` 文件的批处理工具，用于递归扫描目录、提取每个 SVS 的 `label associated image`、按从上到下的空间顺序识别标签中的手写文字，并将结果写入 CSV。

当前版本聚焦一个直接、清晰、可批量运行的工作流：

- 递归扫描输入目录中的 `.svs` 文件
- 从 `associated_images["label"]` 提取标签图像
- 对标签图像做轻量预处理，提升分行与 OCR 稳定性
- 基于水平投影进行文本行分割
- 按行裁剪并放大，再逐行做 OCR
- 默认先走本地 OCR；当结果明显可疑时，再触发 OpenAI fallback
- 将每个 SVS 的识别结果写入同一个 CSV
- 额外生成一张预览总图，方便快速人工检查前几个成功样本

## 输出结果

输出 CSV 包含三列：

- `svs_filename`: 仅保存文件名，不保存完整路径
- `slide_path`: 相对 `--input-dir` 的相对路径
- `recognized_text`: 识别出的标签文本，保留从上到下的行顺序，行之间用换行符连接

如果某个文件处理失败，不会中断整个批次；该文件对应的 `recognized_text` 会写入 `ERROR: ...` 信息。

程序还会默认输出一张预览 PNG，总图尺寸为 `4096x4096`，默认展示前 5 个成功处理的 slide。每一行包含：

- WSI 缩略图
- label 缩略图
- 按 CSV 同样分行规则绘制的识别文本

## 环境要求

- Python 3.9+
- 本地 OCR 依赖：
  - `pytesseract`
  - 系统已安装并可在 `PATH` 中找到的 `tesseract`
- SVS 读取依赖：
  - `openslide-python`
  - 系统 OpenSlide 动态库
- OpenAI fallback 依赖：
  - `openai`
  - 环境变量 `OPENAI_API_KEY`

在 macOS 上，如果安装了 `openslide-python` 但仍提示缺少 OpenSlide 动态库，可优先尝试：

```bash
pip install openslide-bin
```

## 安装

### 方式一：使用 `venv`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 方式二：使用 Conda

如果你更习惯用 Conda，可以这样创建并激活环境：

```bash
conda create -n svs-label-ocr python=3.9 -y
conda activate svs-label-ocr
pip install -e .
```

如果当前机器还没有安装 `tesseract` 或 OpenSlide 系统库，Conda 方式也可以一起安装常见依赖：

```bash
conda create -n svs-label-ocr python=3.9 -y
conda activate svs-label-ocr
conda install -c conda-forge tesseract openslide
pip install -e .
```

使用 Conda 环境运行时，进入项目后先执行：

```bash
conda activate svs-label-ocr
```

## 使用方法

基础用法：

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv
```

上面的命令默认还会输出：

```text
/path/to/output.preview.png
```

仅使用本地 OCR，不启用 OpenAI fallback：

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --disable-openai-fallback
```

指定本地 OCR 语言：

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --tesseract-language eng
```

指定预览图输出路径和展示行数：

```bash
svs-label-ocr \
  --input-dir /path/to/svs_root \
  --output-csv /path/to/output.csv \
  --preview-image /path/to/custom.preview.png \
  --preview-rows 5
```

可用参数：

- `--input-dir`: 输入根目录，程序会递归查找其中的 `.svs`
- `--output-csv`: 输出 CSV 路径
- `--tesseract-language`: 本地 tesseract 语言，默认 `eng`
- `--disable-openai-fallback`: 禁用 OpenAI fallback
- `--openai-model`: fallback 使用的 OpenAI 模型，默认 `gpt-5`
- `--openai-prompt`: fallback 提示词，默认要求模型只返回图片中的手写文本
- `--preview-image`: 预览总图输出路径；不传时默认使用 `output_csv` 同目录下的 `*.preview.png`
- `--preview-rows`: 预览图显示的成功样本行数，默认 `5`

## 工作流程

程序的单文件处理流程如下：

1. 打开 `.svs`
2. 提取 `label associated image`
3. 裁剪黑边，灰度化，轻度去噪，增强对比度，二值化
4. 基于行投影检测文本行范围
5. 对每一行做左右内容收紧和放大
6. 先做本地 OCR
7. 若本地结果为空、过短、没有字母数字，或符号噪声比例过高，则切换到 OpenAI fallback
8. 按自上而下顺序拼接多行文本
9. 将结果写入 CSV，并写入相对输入目录的 `slide_path`
10. 选取前 5 个成功样本生成 `4096x4096` 的预览总图

## 错误处理原则

- 对明显非法的输入目录，直接显式报错
- 对单个 SVS 的处理错误，隔离到该文件，不影响整个批次
- 不使用静默 fallback 掩盖关键错误
- 缺失 `label` 时会显式报错，不会偷偷改用主图区域代替

## 当前实现范围

已实现：

- 递归 SVS 扫描
- `label associated image` 提取
- 图像预处理
- 投影式分行
- 逐行裁剪与放大
- 本地 OCR 与 OpenAI fallback 编排
- CSV 导出
- `slide_path` 相对路径输出
- 预览总图输出
- 批处理错误隔离

暂未扩展：

- 面向复杂版式的整页 OCR
- 与特定标签命名规则强绑定的后处理纠错
- 自定义手写识别模型训练或微调
- GUI
- 数据库或分布式处理

## 测试

运行测试：

```bash
python -m pytest -v
```

如果你使用的是 Conda 环境，同样先激活环境再执行：

```bash
conda activate svs-label-ocr
python -m pytest -v
```

## 项目结构

```text
src/svs_label_ocr/
  cli.py              # 命令行入口
  export.py           # 批处理与 CSV 输出
  label_extractor.py  # SVS label 提取
  line_images.py      # 按行裁剪与放大
  ocr.py              # 本地 OCR、fallback OCR、可疑结果判断
  pipeline.py         # 单文件端到端处理流程
  preview.py          # 预览总图渲染
  preprocess.py       # 图像预处理
  scanner.py          # 递归扫描 .svs
  segmentation.py     # 基于投影的文本行分割
tests/
  ...                 # 单元测试与烟雾测试
docs/
  DEMANDS.MD
  CHANGELOG.md
```
