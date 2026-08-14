# 中国药物临床试验登记信息采集器

面向 [中国药物临床试验登记与信息公示平台](https://www.chinadrugtrials.org.cn/) 的临床试验信息采集工具。支持关键词与高级条件检索、自动分页、详情页归档、RAG JSON 生成、网页原样 Word 下载及基于内容指纹的增量同步。

> 仅采集有权访问的公开信息。请遵守目标网站规则、合理设置请求间隔，并使用本人浏览器会话取得的 Cookie；不要尝试绕过网站的访问控制或反爬机制。

## 功能

- 关键词检索与高级检索：登记号、适应症、方案编号、药物名称/类型、申请人、伦理委员会、研究者、参加机构、试验状态。
- 自动解析列表分页信息，遍历全部结果页和详情页。
- 始终保存详情页原始 HTML，作为结构化数据的可追溯来源。
- 从已落盘的 HTML 提取结构化 RAG JSON，包含章节、全文、文本块和 `content_hash`。
- 严格模拟详情页“下载”按钮所属表单，保存服务器原样 `.doc` 文件及原始响应副本。
- 在 macOS 上把 WordML `.doc` 额外转换为兼容 `.docx`；WPS 可直接打开平台的原始 `.doc`。
- 增量同步：以“登记号 + 正文内容哈希”识别未变化记录，避免重复写入 JSON 与重复下载文档。
- 交互式菜单：管理检索条件、更新 Cookie、全量/增量同步、离线回建 JSON、查看运行状态。

## 项目结构

```text
.
├── scraper.py                  # 命令行主抓取器
├── main.py                     # 交互式菜单入口
├── cookie_tools.py             # Cookie 提取、合并与配置写入
├── build_json_from_raw.py      # 从 raw HTML 离线重建 RAG JSON
├── config.example.json         # 可复制的配置模板
├── requirements.txt            # Python 依赖
├── china-drug-trials-skills/  # 独立可部署的 WorkBuddy Skill
└── output/<关键词>/
    ├── raw/                    # 详情原始 HTML
    ├── json/                   # RAG JSON
    ├── word/                   # 原始 .doc 与兼容 .docx
    │   └── source/             # 服务器原始响应副本
    ├── logs/                   # 运行日志
    ├── state.json              # 增量内容指纹索引
    └── summary.json            # 最近一次抓取汇总
```

## 安装

需要 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
```

`config.json` 可能包含会话 Cookie，已被 `.gitignore` 排除，不应提交到版本库。

## 配置 Cookie

平台会校验浏览器会话及反爬 Cookie。推荐在已正常访问平台的浏览器开发者工具中，对一个站内请求使用“复制为 cURL”，然后使用交互菜单粘贴该命令。工具会提取 `-b/--cookie` 参数并合并写入 `config.json`。

```bash
python3 main.py
```

菜单中的 Cookie 更新方式：

1. 粘贴浏览器复制的 cURL（推荐，通常含完整会话字段）；
2. 粘贴 `curl -i` 或 `curl -D` 响应头，提取 `Set-Cookie`；
3. 请求平台入口页，更新平台下发的基础反爬 Cookie。

Cookie 失效时重新获取。不要把 Cookie、`config.json` 或含敏感响应头的日志上传到 GitHub。

## 快速开始

### 交互式模式

```bash
python3 main.py
```

可在菜单中配置条件，并选择：

- **全量同步**：重新写入全部详情 JSON，并重新归档 Word；
- **增量同步**：读取详情页后比较正文指纹，只保存新增或正文变化的记录；
- **离线补建 JSON**：不访问网站，直接从已有 `raw/` 重新生成 JSON。

### 命令行模式

```bash
# 从配置文件运行
python3 scraper.py --config config.json

# 基本关键词检索
python3 scraper.py --keywords "胰腺癌" --cookies "name=value; name2=value2"

# 高级检索：关键词 + 招募中 + 化学药物
python3 scraper.py --keywords "肺癌" --state "招募中" --drugs-type 2 --cookies "..."

# 限制为前两页，并跳过已有 JSON（适合中断恢复）
python3 scraper.py --keywords "胰腺癌" --max-pages 2 --resume --cookies "..."

# 每日增量同步
python3 scraper.py --config config.json --incremental
```

支持的高级参数：

| 参数 | 含义 |
|---|---|
| `--reg-no` | 登记号 |
| `--indication` | 适应症 |
| `--case-no` | 试验方案编号 |
| `--drugs-name` | 药物名称 |
| `--drugs-type` | `1` 中药/天然药物，`2` 化学药物，`3` 生物制品 |
| `--appliers` | 申请人 |
| `--communities` | 伦理委员会 |
| `--researchers` | 主要研究者 |
| `--agencies` | 临床参加机构 |
| `--state` | 试验状态，例如“招募中” |

## 输出说明

每个检索词写入单独目录 `output/<关键词>/`。例如 `output/胰腺癌/`。

### RAG JSON

`json/<登记号>.json` 的核心字段：

- `source`：平台信息、详情接口、原始 HTML 相对来源与检索页码；
- `reg_no`、`list_info`：登记号与列表页基础信息；
- `details`、`sections`：从详情表格提取的键值与章节；
- `full_text`：可直接索引的全文；
- `rag_chunks`：按章节切分、超长时按约 4,000 字符拆分的文本块；
- `content_hash`：规范化正文 SHA-256，用于增量去重。

### Word 文件

平台下载的 `.doc` 当前实际为 Word 2003 XML（WordML），不是二进制 DOC 或 OOXML DOCX：

- `word/<登记号>.doc`：与网页“下载”响应保持字节一致；
- `word/source/<登记号>.source.doc`：同一原始响应的溯源副本；
- `word/<登记号>.docx`：macOS 上由 `textutil` 转换的兼容版。

若 Apple Pages 无法打开原始 `.doc`，请使用 WPS/Word，或优先打开对应 `.docx`。非 macOS 环境不会自动生成 `.docx`，但仍会保留服务器原样 `.doc`。

## 离线重建 JSON

适用于抓取后需要调整 JSON 解析策略，或 JSON 目录丢失而 `raw/` 尚在的场景：

```bash
python3 build_json_from_raw.py --output "output/胰腺癌"

# 强制覆盖已有 JSON
python3 build_json_from_raw.py --output "output/胰腺癌" --force
```

该操作不访问平台，并会保留或更新 `state.json` 中的内容指纹。

## 增量策略

增量模式不会只根据文件是否存在就跳过。流程为：

1. 获取最新详情页并更新 `raw/` HTML；
2. 从 raw HTML 生成规范化 `full_text`；
3. 计算 `content_hash`，并与 `state.json` 或已有 JSON 的哈希比较；
4. 无变化：保留既有 JSON/Word，不重复下载；
5. 新增或正文变化：重写 JSON、下载原始 Word，并更新状态索引。

因此，`summary.json` 中的 `skip_count` 表示“正文无变化”，不代表文件缺失。

## 常见问题

### 未找到搜索结果或跳转登录页

通常是 Cookie 已失效或不完整。重新从可正常访问网站的浏览器请求复制 cURL，并在 `main.py` 菜单中更新 Cookie。

### 只有 raw HTML，没有 JSON

运行离线回建：

```bash
python3 build_json_from_raw.py --output "output/<关键词>"
```

### `.doc` 无法在 Pages 打开

这是 WordML 与客户端兼容性问题。原始 `.doc` 是平台响应，不是本工具从 HTML 拼接得到的文件。使用 WPS/Word，或打开对应的 `.docx`。

### 想确认本次抓取总量与成功数

读取 `output/<关键词>/summary.json`。其中包含总页数、总记录数、成功/失败/跳过数量以及逐登记号结果。

## 独立 Skill

`china-drug-trials-skills/` 是自包含的 WorkBuddy Skill，可单独复制或使用其中打包的 ZIP 部署，不依赖当前项目根目录。详见该目录中的 `SKILL.md` 与 `README.md`。

## 免责声明

本项目用于研究、信息管理与数据处理。使用者应自行确认其使用场景符合目标平台规则、数据使用要求及适用法律法规。临床登记信息不构成医疗建议、诊断、治疗建议或监管结论。
