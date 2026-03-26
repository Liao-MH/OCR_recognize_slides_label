v1.4.0 - 2026-03-26
用户需求
用户要求不要增加后处理，而是在把图像传给 GPT 时通过提示词明确约束：每一行识别结果的前 6 个字符必须是数字，并在模糊时优先输出数字而不是字母
已做改动
版本号升级到 v1.4.0
更新 `src/svs_label_ocr/ocr.py`，增强 OpenAI fallback 默认提示词，明确要求每行前 6 位必须为数字，并在模糊时优先输出数字
更新 `README.md` 与 `docs/DEMANDS.MD`，同步记录新的 GPT 提示词约束
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py`，同步版本号
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/ocr.py
docs/DEMANDS.MD
docs/CHANGELOG.md
验证结果
.venv/bin/python -m pytest -v
git diff --check

v1.3.0 - 2026-03-26
用户需求
用户在将 `--openai-model` 设为 `gpt-4.1` 时遇到 `.png` 被当成 `input_file` 发送而导致的 `400 invalid_request_error`，要求修复 OpenAI fallback，使视觉模型通过正确的图片输入路径工作
已做改动
版本号升级到 v1.3.0
新增 `docs/plans/2026-03-26-openai-image-input-design.md`，记录统一使用图片输入路径的设计决策
新增 `docs/plans/2026-03-26-openai-image-input-implementation.md`，记录本轮实现计划
更新 `src/svs_label_ocr/ocr.py`，移除临时 PNG 文件上传与 `input_file` 路径，改为将行图编码为 PNG data URL 并通过 Responses API `input_image` 发送
更新 `tests/test_ocr_provider_config.py`，覆盖 OpenAI fallback 请求中使用 `input_image` 的行为
更新 `README.md` 与 `docs/DEMANDS.MD`，同步说明 OpenAI fallback 现在直接发送图片输入，并兼容 `gpt-4.1`
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py`，同步版本号
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/ocr.py
tests/test_ocr_provider_config.py
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-26-openai-image-input-design.md
docs/plans/2026-03-26-openai-image-input-implementation.md
验证结果
.venv/bin/python -m pytest tests/test_ocr_provider_config.py -v
.venv/bin/python -m pytest -v
git diff --check

v1.2.0 - 2026-03-24
用户需求
用户要求在现有 `.run.log` 正常写入和保存的基础上，让终端窗口也能实时显示批处理进度，并在某个 slide 失败时立即看到失败信息，而不是只在最后看到汇总
已做改动
版本号升级到 v1.2.0
新增 `docs/plans/2026-03-24-live-progress-design.md`，记录实时终端进度与失败输出的设计决策
新增 `docs/plans/2026-03-24-live-progress-implementation.md`，记录本轮实现计划
更新 `src/svs_label_ocr/export.py`，新增单行覆盖式终端进度输出、即时失败摘要输出，以及可注入的终端流参数；同时保留现有 `.run.log` 作为完整 traceback 记录
新增 `tests/test_live_progress.py`，覆盖实时进度与失败摘要输出行为
更新 `README.md` 与 `docs/DEMANDS.MD`，同步默认终端实时进度行为
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py`，同步版本号
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/export.py
tests/test_live_progress.py
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-24-live-progress-design.md
docs/plans/2026-03-24-live-progress-implementation.md
验证结果
.venv/bin/python -m pytest tests/test_live_progress.py -v
.venv/bin/python -m pytest -v
git diff --check
PYTHONPATH=src .venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from svs_label_ocr.export import process_batch


class DummyProvider:
    def recognize_line(self, image):
        return "A1"


class DummySlide:
    associated_images = {"label": Image.new("RGB", (50, 30), "white")}
    level_dimensions = [(64, 64)]

    def close(self):
        pass

    def get_thumbnail(self, size):
        return Image.new("RGB", size, "gray")


def open_dummy_slide(path):
    if path.name == "bad.svs":
        raise ValueError("broken slide")
    return DummySlide()


with TemporaryDirectory() as tmp:
    root = Path(tmp) / "input"
    root.mkdir()
    (root / "bad.svs").write_text("")
    (root / "ok.svs").write_text("")
    process_batch(root, Path(tmp) / "output" / "result.csv", local_provider=DummyProvider(), slide_opener=open_dummy_slide)
PY

v1.1.0 - 2026-03-24
用户需求
用户要求在现有 CSV 与终端 summary 之外，默认额外输出一个代码运行日志文件，便于在大批量失败时查看每个 slide 的处理过程和具体报错；同时本轮提交不要把 `tests/` 目录作为功能改动的一部分
已做改动
版本号升级到 v1.1.0
新增 `docs/plans/2026-03-24-runtime-log-design.md`，记录默认运行日志文件的设计决策
新增 `docs/plans/2026-03-24-runtime-log-implementation.md`，记录本轮实现计划
更新 `src/svs_label_ocr/export.py`，为每次批处理默认生成 `<output_csv stem>.run.log`，记录批处理启动、扫描结果、逐 slide 处理、逐 slide 异常 traceback、预览输出状态和批次结束汇总
更新 `src/svs_label_ocr/cli.py`，让终端 summary 额外输出运行日志路径
更新 `README.md` 与 `docs/DEMANDS.MD`，同步默认运行日志文件的真实行为
更新 `pyproject.toml` 与 `src/svs_label_ocr/__init__.py`，同步版本号
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/cli.py
src/svs_label_ocr/export.py
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-24-runtime-log-design.md
docs/plans/2026-03-24-runtime-log-implementation.md
验证结果
.venv/bin/python -m pytest -v
git diff --check
.venv/bin/python -m svs_label_ocr.cli --help
PYTHONPATH=src .venv/bin/python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from svs_label_ocr.export import process_batch


class DummyProvider:
    def recognize(self, image):
        return "ok"


class DummySlide:
    associated_images = {"label": Image.new("RGB", (16, 16), "white")}
    level_dimensions = [(64, 64)]

    def get_thumbnail(self, size):
        return Image.new("RGB", size, "gray")


def open_dummy_slide(path):
    return DummySlide()


with TemporaryDirectory() as tmp:
    root = Path(tmp) / "input"
    root.mkdir()
    (root / "sample.svs").write_bytes(b"fake")
    output_csv = Path(tmp) / "output" / "results.csv"
    result = process_batch(
        root,
        output_csv,
        local_provider=DummyProvider(),
        fallback_provider=None,
        slide_opener=open_dummy_slide,
        preview_rows=1,
    )
    print(result.run_log.exists(), result.run_log)
PY

v1.0.0 - 2026-03-24
用户需求
用户要求进一步改进 CLI：OpenAI fallback 不应再依赖环境变量隐式取 key，而应通过显式参数指定；同时程序运行结束后应输出识别总数、成功数、失败数等统计信息
已做改动
版本号升级到 v1.0.0
新增 `docs/plans/2026-03-24-explicit-openai-key-and-summary-design.md`，记录显式 API key 和运行 summary 的设计决策
新增 `docs/plans/2026-03-24-explicit-openai-key-and-summary-implementation.md`，记录本轮实现计划
更新 `src/svs_label_ocr/cli.py`，新增 `--openai-api-key` 参数、CLI 参数校验，以及运行结束后的 summary 输出
更新 `src/svs_label_ocr/ocr.py`，让 OpenAI fallback provider 接收显式 API key
更新 `src/svs_label_ocr/export.py`，返回结构化 batch summary，包括总数、成功数、失败数和输出路径
新增 `tests/test_cli_summary.py`、`tests/test_ocr_provider_config.py`、`tests/test_summary.py`，覆盖显式 key 和 summary 行为
更新 `tests/test_cli.py` 与 `tests/test_integration_smoke.py`，覆盖新的 CLI 约束和结构化 batch 结果
更新 `README.md`、`docs/DEMANDS.MD`、`docs/CHANGELOG.md`，同步新的 CLI 要求与运行输出说明
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/cli.py
src/svs_label_ocr/export.py
src/svs_label_ocr/ocr.py
tests/test_cli.py
tests/test_cli_summary.py
tests/test_integration_smoke.py
tests/test_ocr_provider_config.py
tests/test_summary.py
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-24-explicit-openai-key-and-summary-design.md
docs/plans/2026-03-24-explicit-openai-key-and-summary-implementation.md
验证结果
.venv/bin/python -m pytest -v
git diff --check
.venv/bin/python -m svs_label_ocr.cli --help

v0.4.0 - 2026-03-23
用户需求
用户要求把此前确认过的两个设计需求真正实现到代码中：CSV 增加相对输入目录的 `slide_path` 列，并生成包含 WSI 缩略图、label 缩略图和分行识别文本的预览总图
已做改动
版本号升级到 v0.4.0
新增 `src/svs_label_ocr/preview.py`，实现 `4096x4096` 预览总图渲染、缩略图布局和按 OCR 行边界绘制文本
更新 `src/svs_label_ocr/pipeline.py`，让单个 slide 处理返回结构化结果，包括识别文本、识别行、label 图像和 WSI 缩略图
更新 `src/svs_label_ocr/export.py`，让 CSV 输出增加 `slide_path` 列，并在批处理完成后生成预览总图
更新 `src/svs_label_ocr/cli.py`，新增 `--preview-image` 和 `--preview-rows` 参数，并默认在 CSV 旁边输出预览图
更新 `tests/test_export.py`、`tests/test_integration_smoke.py`、`tests/test_cli.py`，覆盖新 CSV 列、预览输出和参数校验
新增 `tests/test_preview.py`，覆盖预览图尺寸和候选样本数量规则
新增 `docs/plans/2026-03-23-preview-slide-summary-implementation.md`，记录本轮实现计划
更新 `README.md`、`docs/DEMANDS.MD`、`docs/CHANGELOG.md`，同步真实实现行为和用法
影响文件
README.md
pyproject.toml
src/svs_label_ocr/__init__.py
src/svs_label_ocr/cli.py
src/svs_label_ocr/export.py
src/svs_label_ocr/pipeline.py
src/svs_label_ocr/preview.py
tests/test_cli.py
tests/test_export.py
tests/test_integration_smoke.py
tests/test_preview.py
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-23-preview-slide-summary-implementation.md
验证结果
.venv/bin/python -m pytest -v
git diff --check

v0.3.3 - 2026-03-23
用户需求
用户要求在现有 OCR 批处理工具上新增两项输出能力：CSV 增加相对输入目录的 `slide_path` 列，并生成一个包含 WSI 缩略图、label 缩略图和分行识别文本的预览总图；当前阶段先完成设计确认与文档落地
已做改动
版本号升级到 v0.3.3
更新 `docs/DEMANDS.MD`，补充 `slide_path` 与预览总图的确认需求
新增 `docs/plans/2026-03-23-preview-slide-summary-design.md`，记录已确认的产品决策、数据结构方案、CLI 设计、渲染规则、错误边界与测试策略
影响文件
docs/DEMANDS.MD
docs/CHANGELOG.md
docs/plans/2026-03-23-preview-slide-summary-design.md
验证结果
git diff --check
人工核对设计文档与已确认需求一致

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
