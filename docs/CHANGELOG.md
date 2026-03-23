v0.3.2 - 2026-03-23
用户需求
用户要求在现有 README 基础上，补充使用 Conda 创建环境、安装依赖和运行测试/程序的说明
已做改动
版本号升级到 v0.3.2
更新根目录 `README.md`，在安装与测试章节补充 Conda 环境创建、激活、依赖安装和运行说明
同步更新 `docs/DEMANDS.MD`，记录 Conda 文档需求
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py` 版本号
影响文件
README.md
docs/DEMANDS.MD
docs/CHANGELOG.md
pyproject.toml
src/svs_label_ocr/__init__.py
验证结果
git diff --check
.venv/bin/python -m pytest -v

v0.3.1 - 2026-03-23
用户需求
用户要求为仓库生成一个可直接阅读和使用的 `README.md`，并让文档内容与当前已实现功能保持一致
已做改动
版本号升级到 v0.3.1
新增根目录 `README.md`，说明项目目标、运行依赖、安装步骤、CLI 参数、输出格式、处理流程、错误处理原则、当前范围和测试方法
同步更新 `docs/DEMANDS.MD`，记录本次 README 文档需求
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py` 版本号
影响文件
README.md
docs/DEMANDS.MD
docs/CHANGELOG.md
pyproject.toml
src/svs_label_ocr/__init__.py
验证结果
git diff --check
.venv/bin/python -m pytest -v

v0.3.0 - 2026-03-23
用户需求
用户要求把需求文档中规划的首版功能全部补完，形成从递归扫描 `.svs`、提取 `label associated image`、图像预处理、分行、OCR 到 CSV 导出的完整首版可运行流水线
已做改动
版本号升级到 v0.3.0
新增 `src/svs_label_ocr/preprocess.py`，实现黑边裁剪、灰度化、轻度去噪、自动对比度、Otsu 二值化和轻量形态学清理
新增 `src/svs_label_ocr/segmentation.py`，实现基于行投影的文本行检测、细线过滤和短间隙合并
新增 `src/svs_label_ocr/line_images.py`，实现逐行裁剪、左右内容收紧和放大
新增 `src/svs_label_ocr/ocr.py`，实现 OCR 结果清洗、可疑结果判定、本地 `pytesseract` OCR，以及基于 OpenAI Responses API 文件输入的 fallback OCR
新增 `src/svs_label_ocr/pipeline.py`，实现单个 `.svs` 文件从 label 提取到逐行识别的完整编排
新增 `src/svs_label_ocr/export.py`，实现批处理、逐文件异常隔离和 CSV 导出
扩展 `src/svs_label_ocr/cli.py`，新增可执行入口、OCR 配置参数和批处理调用
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py`，声明运行依赖、命令行入口和版本号
新增 `tests/test_preprocess.py`、`tests/test_segmentation.py`、`tests/test_line_images.py`、`tests/test_ocr.py`、`tests/test_pipeline.py`、`tests/test_export.py`、`tests/test_integration_smoke.py`，覆盖核心模块与端到端烟雾链路
更新 `docs/DEMANDS.MD`，补充系统依赖说明和使用示例
影响文件
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/cli.py
src/svs_label_ocr/preprocess.py
src/svs_label_ocr/segmentation.py
src/svs_label_ocr/line_images.py
src/svs_label_ocr/ocr.py
src/svs_label_ocr/pipeline.py
src/svs_label_ocr/export.py
tests/test_preprocess.py
tests/test_segmentation.py
tests/test_line_images.py
tests/test_ocr.py
tests/test_pipeline.py
tests/test_export.py
tests/test_integration_smoke.py
docs/DEMANDS.MD
docs/CHANGELOG.md
验证结果
.venv/bin/python -m pytest -v
git diff --check
.venv/bin/python -m svs_label_ocr.cli --help
.venv/bin/svs-label-ocr --help
.venv/bin/python -c "import openslide; print(openslide.__version__)"

v0.2.0 - 2026-03-23
用户需求
用户要求在现有需求与计划基础上，先落地首批可运行代码骨架，包括 CLI 参数契约、递归 `.svs` 扫描，以及 `label associated image` 提取能力，为后续预处理和 OCR 流水线继续开发打基础
已做改动
版本号升级到 v0.2.0
新增 `pyproject.toml`，建立 Python 包与 `pytest` 测试配置
新增 `.gitignore`，忽略本地虚拟环境和测试缓存
新增 `src/svs_label_ocr/__init__.py`，记录当前代码版本
新增 `src/svs_label_ocr/cli.py`，实现 `--input-dir` 与 `--output-csv` 两个必填参数
新增 `src/svs_label_ocr/scanner.py`，实现递归 `.svs` 搜索、稳定排序，以及非法输入的显式报错
新增 `src/svs_label_ocr/label_extractor.py`，实现从 `associated_images["label"]` 直接提取标签图像，缺失时显式报错
新增 `tests/test_cli.py`、`tests/test_scanner.py`、`tests/test_label_extractor.py`，按 TDD 固定首批行为
同步更新 `docs/DEMANDS.MD` 版本号
影响文件
.gitignore
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/cli.py
src/svs_label_ocr/scanner.py
src/svs_label_ocr/label_extractor.py
tests/test_cli.py
tests/test_scanner.py
tests/test_label_extractor.py
docs/DEMANDS.MD
docs/CHANGELOG.md
验证结果
.venv/bin/python -m pytest tests/test_cli.py -v
.venv/bin/python -m pytest tests/test_scanner.py -v
.venv/bin/python -m pytest tests/test_label_extractor.py -v

v0.1.0 - 2026-03-23
用户需求
用户要求构建一个从 `.svs` 文件提取 `label associated image`、按空间顺序识别其中手写文字并输出 CSV 的批处理 OCR 工具；当前阶段先把需求与实现计划结构化落地到仓库中，作为后续开发基线
已做改动
初始化仓库文档版本为 v0.1.0
新增 `docs/DEMANDS.MD`，结构化整理项目目标、模块职责、异常处理边界、首版范围和验收标准
新增 `docs/plans/2026-03-23-svs-label-ocr-pipeline.md`，拆分首版实现任务、测试路径和验证命令
影响文件
docs/DEMANDS.MD
docs/plans/2026-03-23-svs-label-ocr-pipeline.md
docs/CHANGELOG.md
验证结果
人工核对文档结构与需求原文一致
