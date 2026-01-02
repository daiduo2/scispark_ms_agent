# SciSpark MS Agent

面向科研工作流的命令行应用，基于 ms-agent 思想与现有技能（skills）脚本实现。项目支持从自然语言主题出发，检索与处理学术文献，并将阶段性产物保存到本地目录，便于审阅与后续优化。

> 远程仓库：<https://github.com/daiduo2/scispark_ms_agent>

## Features
- 端到端工作流：一次性执行“事实抽取 → 假设生成 → 初始方案 → 技术优化 → MoA（多代理评审） → 人机协作”各阶段并产出文件
- 队列模式：先入队后由 worker 异步处理，适合批量或离线运行
- 可配置输出：所有产物按 user_id 与 task_id 分目录保存，便于归档与检查

## Directory
- 项目根目录（Windows）：`E:\cli\scispark_ms_skills`
- 输出目录（默认）：`./scispark_ms_skills_output`
  - 结构：`OUTPUT_PATH/user_id/task_id/topic/<Idea|Paper|MOA|Review>/...`

## Quick Start
1) 安装依赖（建议虚拟环境）

```powershell
cd E:\cli\scispark_ms_skills
py -3.10 -m venv .venv
.\.venv\Scripts\activate

pip install --upgrade pip
pip install jinja2 pydantic-settings openpyxl requests beautifulsoup4 arxiv scihub-cn py2neo tiktoken openai agentscope dashscope pandas
```

2) 配置 .env（在项目根或运行目录确保可读取）

```ini
# 必需
QWEN_API_TOKEN=your_qwen_token
DEEPSEEK_API_TOKEN=your_deepseek_token
DEEPSEEK_API_BASE_URL=https://api.deepseek.com/v1

# 可选
OUTPUT_PATH=./scispark_ms_skills_output
HTTP_PROXY=
HTTPS_PROXY=
# Neo4j（可留空）
NEO4J_USERNAME=
NEO4J_PASSWORD=
NEO4J_HOST=
NEO4J_PORT=
```

3) 冒烟测试（完整工作流）

```powershell
Set-Location E:\cli
python -m scispark_ms_skills.cli workflow --topic "battery materials" --num 1 --compression false --user-id "cli_user"
```

## CLI Usage

- 完整工作流（同步执行并输出 JSON 路径结果）

```powershell
python -m scispark_ms_skills.cli workflow --topic "<主题>" --num 3 --compression true --user-id "cli_user"
```

- 入队任务（异步处理）

```powershell
python -m scispark_ms_skills.cli enqueue --topic "<主题>" --num 3 --compression false --user-id "cli_user"
```

- worker 处理队列

```powershell
# 仅处理一次
python -m scispark_ms_skills.cli worker --interval 3 --once
# 持续轮询
python -m scispark_ms_skills.cli worker --interval 3
```

> 注意：主题字符串请尽量使用英文或下划线，避免 Windows 路径非法字符：`<>:"/\|?*`

## Environment & Proxy
- 若网络需要代理，设置环境变量：

```powershell
$env:HTTP_PROXY="http://<host>:<port>"
$env:HTTPS_PROXY="http://<host>:<port>"
```

- .env 的读取基于当前工作目录。若从 `E:\cli` 运行模块但 .env 在 `E:\cli\scispark_ms_skills`，请将 .env 复制到运行目录或改到项目根运行。

## Common Issues
- `ModuleNotFoundError: scispark_ms_skills`：请从 `E:\cli` 运行模块（`python -m scispark_ms_skills.cli ...`），或设置 `PYTHONPATH=E:\cli` 再按路径运行。
- `httpx.LocalProtocolError: Illegal header value b'Bearer '`：令牌为空或 .env 未被加载；确认 `DEEPSEEK_API_TOKEN`/`QWEN_API_TOKEN` 非空并在当前目录可读取。
- 写文件失败：多数是主题包含非法路径字符或无写权限；调整主题或以管理员身份运行。

## Roadmap
- 自然语言调度入口（NL Routing）：解析自由文本为意图与参数，路由到工作流或任务管理命令
- 任务管理增强：`status/list/cancel/continue` 与阶段级进度记录、重试策略
- 技能注册与分层加载：按 Level 控制资源与上下文加载，贴合 ms-agent 的 AgentSkills 设计

## License
本仓库用于科研与工程实践，许可证待补充。默认遵循依赖项各自的许可证约束。

