# Exam Radar

Exam Radar 是一个面向大学课程的 AI 考试复习工作区。它把课程大纲、讲义、教程、作业、历年试卷和答题记录连接起来，帮助学生回答三个问题：课程在考什么、我应该先复习什么、下一道题应该练什么。

界面采用 GPT 式对话工作流和 Claude 式项目上下文 / Artifact 工作区：左侧是课程与历史学习会话，中间是课程助手对话，右侧是可切换的 Exam Radar、Knowledge Map、Question DNA、Revision Packs 和 Course Materials。

## 当前功能

- **课程工作区**：创建多个课程，设置课程代码和考试日期；每个浏览器用户的数据使用签名 Cookie 隔离。
- **Course Intelligence**：上传 PDF、DOCX、PPTX、TXT、MD；查看解析状态、来源摘录和页码/偏移提示；显式点击 Analyze course 后生成知识地图。
- **Exam Radar**：展示 Exam Readiness、知识点掌握度、可解释 Priority Score 和每个因素的贡献。优先级是透明加权分数，不是未经训练的逻辑回归。
- **Knowledge Map**：按章节查看课程知识点关系，点击节点打开详情或开始练习。
- **Exam DNA**：分析已上传的历年卷，提取题目概念、题型、Bloom/认知层级、分值、年份和推理技能，并按 Explain、Compare、Calculation、Scenario、Definition 统计分布。
- **Adaptive Practice**：由 Generator → Critic → Similarity / Difficulty → Answer Verifier 生成变式题。提交答案后才显示评分、参考答案和掌握度变化。
- **Revision Packs**：按章节勾选知识点，生成 Notes、Formula Sheet 或 Flashcards，选择 Quick / Standard / Detailed，支持 Markdown、DOCX、PDF 导出和在线编辑。
- **共享课程**：创建只读课程快照与评论链接。分享内容只包含课程地图与复习包，个人会话、答案和 mastery 保持私密。
- **中文界面**：界面固定为简体中文；回答会带来源引用。
- **混合 AI 模式**：默认优先使用本地 Ollama 模型处理课程资料、检索和常规任务；配置 OpenAI API Key 后，复杂推理任务可升级到 GPT-5。

示例课程是明确标注的 authored demo，包含 Machine Learning 课程资料和示例题，可以不用 API Key 演示完整交互。示例数据不是任何大学真实试卷，也不代表预测考题。

## 环境要求

- Windows PowerShell、Python 3.11+
- Node.js 20+（建议 22 LTS）
- 可选：Ollama 本地模型（混合模式默认使用）和 OpenAI API Key。没有 API Key 时，本地模型仍可处理真实课程；未启动本地模型时，示例课程仍可运行。

## 安装

在项目根目录执行：

```powershell
uv venv .venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt

cd frontend
npm install
cd ..
```

如果没有 uv，也可以用 Python 自带虚拟环境和 pip install -r requirements.txt。

## 配置混合 AI 模式（可选）

```powershell
Copy-Item .env.example .env
notepad .env
```

在 .env 中填写：

```env
AI_MODE=hybrid
LOCAL_BASE_URL=http://127.0.0.1:11434
LOCAL_MODEL=qwen2.5:7b
OPENAI_API_KEY=你的服务端密钥
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-5
```

`AI_MODE=hybrid` 在本机优先调用 Ollama；在 Vercel 上会直接使用 GPT-5，因为云端无法访问你电脑的 Ollama。若密钥来自兼容 OpenAI 的服务商，请同时填写其 `OPENAI_BASE_URL`；官方 OpenAI Key 留空即可。不要把密钥放进 frontend、浏览器代码或提交到 Git。没有密钥且没有 Ollama 时，示例课程仍可运行，新课程会收到明确的配置提示，不会静默伪造结果。

首次使用本地模型时安装并下载一次模型：

```powershell
# 安装 Ollama：https://ollama.com/download/windows
ollama pull qwen2.5:7b
ollama serve
```

下载完成后，课程资料和常规 AI 请求可以在断网状态下运行；只有 GPT-5 升级任务需要网络和 API Key。

## 运行网站

推荐打开两个 PowerShell 窗口。

也可以在依赖安装完成后直接运行根目录脚本（脚本会先构建前端，再启动 FastAPI）：

```powershell
.\start.ps1
```

如果 PowerShell 禁止本地脚本，当前窗口可执行：`Set-ExecutionPolicy -Scope Process Bypass`，然后再次运行脚本。

窗口一，启动 FastAPI：

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

窗口二，启动 Vue/Vite：

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

浏览器打开：http://127.0.0.1:5173/。

生产预览：

```powershell
cd frontend
npm run build
cd ..
.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

当 frontend/dist 存在时，FastAPI 会自动托管构建后的前端，打开 http://127.0.0.1:8000/ 即可。健康检查：http://127.0.0.1:8000/api/health。

## 推荐演示流程

1. 打开示例课程 Machine Learning，观察左侧项目、中央“混合模式”标识和右侧 Artifacts。
2. 点击右侧 Map，选择 F1 Score 或 KNN，查看掌握度和 Priority Score 的因素解释。
3. 点击 Question DNA → Analyze past papers，查看示例资料中的题型分布、年份范围和题目 DNA。
4. 点击 Practice studio 或 Practice this concept，生成一道变式题；题目只公开题干、DNA 和验证状态。
5. 选择答案并提交，查看评分、引用式反馈、mastery delta 和下一道推荐题。
6. 点击 Packs，勾选章节，选择 Notes / Formulas / Flashcards 和详细程度，生成可编辑复习包并导出 DOCX 或 PDF。
7. 点击 Course materials → Create course，新建自己的课程，再上传资料；上传不会自动调用模型，点击 Analyze course 才开始解析。混合模式会优先使用本地模型。
8. 点击顶部 Share course，生成只读快照，用隐身窗口打开链接确认个人会话和掌握度没有被分享。

## API 快速索引

API 前缀为 /api，所有课程路由按签名浏览器 Cookie 做权限隔离：

| 方法 | 路由 | 用途 |
|---|---|---|
| POST | /session | 初始化本地用户会话 |
| GET | /bootstrap | 当前用户课程和公开工作区数据 |
| POST | /courses | 创建课程 |
| POST | /courses/{id}/materials | 上传资料 |
| POST | /courses/{id}/analyze | 分析课程并生成地图 |
| POST | /courses/{id}/exam-analysis | 分析历年卷 / Exam DNA |
| GET | /courses/{id}/exam-analysis | 读取已保存的分析 |
| POST | /courses/{id}/chat | 课程对话 |
| POST | /courses/{id}/questions | 生成并验证变式题 |
| POST | /courses/{id}/questions/{questionId}/answers | 提交答案并更新掌握度 |
| POST | /courses/{id}/packs | 生成复习包 |
| GET | /courses/{id}/packs/{packId}/export?format=docx\|pdf\|md | 导出复习包 |
| POST | /courses/{id}/share | 创建隐私安全的只读快照 |
| GET | /shared/{token} | 查看共享快照 |
| POST | /shared/{token}/comments | 发布评论 |

## 测试与验证

后端测试不需要 API Key：

```powershell
.venv\Scripts\python.exe -m pytest backend -q
```

当前覆盖：Cookie 隔离与篡改、CSRF 来源校验、上传与解析限制、AI 配置错误、题目私有答案不泄露、答案幂等与 mastery 更新、复习包导出、分享隐私、Exam DNA 持久化和 AI 结构化输出。

前端类型检查和生产构建：

```powershell
cd frontend
npm run build
```

## 资料限制

单文件最大 15 MB，课程最多 40 个文件；PDF/PPTX 最多 500 页/幻灯片，单文件提取文本最多 1,000,000 字符，单次 GPT-5 上下文最多 90,000 字符。PDF 需要可选文本，扫描 PDF、图片公式、手写内容和嵌入图表需要先使用外部 OCR；DOCX 页码可能显示为文本偏移；PPTX 当前提取幻灯片文字，不提取演讲者备注或图片。分析界面会显示覆盖说明，历年趋势不应被解释为确定性押题。

## 相关文件

- EXAM_RADAR_UPGRADE_PLAN.md：原始需求提炼与升级方案
- HYBRID_UI_SPEC.md：GPT × Claude UI 规格
- docs/AI_DESIGN.md：GPT-5 AI 设计与安全边界
- output/imagegen/exam-radar-gpt-claude-preview.png：UI 视觉预览

## 运行状态与数据保存

开发和运行验证已完成：后端测试、浏览器流程测试和 Vue/TypeScript 生产构建均已通过。测试覆盖上传、引用、课程对话、知识地图、历年卷分析、答题、编辑与 Word 导出、分享评论和移动端布局。真实 GPT-5 付费请求不会在测试中自动执行；需要配置你自己的服务端 API Key 后才会启用云端升级。

数据默认保存到 `backend/data/exam-radar.sqlite3`，会话签名文件位于同一目录。重启服务会保留数据；更换浏览器、清除 Cookie 或使用隐身窗口会创建不同的本地用户。该版本使用本地浏览器身份，并非邮箱登录、账号恢复或企业级多租户部署。

分享链接当前是本机地址，另一台电脑不能直接访问你的 `127.0.0.1`。可以先在同一电脑的另一浏览器 / 隐身窗口演示。真实外网多人使用需要正式部署、HTTPS 和账号认证；当前共享功能为快照与评论，不是实时协同编辑或在线成员统计。

停止服务：在对应 PowerShell 窗口按 `Ctrl+C`。如果端口被占用，可以运行 `.\start.ps1 -Port 8001`，然后访问 `http://127.0.0.1:8001/`。开发模式的 Vite 代理默认指向 8000，修改开发后端端口时需同步修改 `frontend/vite.config.ts`。

## 浏览器测试

先保持网站运行，再执行：

```powershell
cd frontend
npx playwright install chromium
npx playwright test
```

可以用环境变量 `TEST_URL` 指定其他已运行的网站地址。测试使用独立浏览器会话和示例数据，不需要 API Key。

## 实现范围

本版本为可运行的比赛 MVP：Vue 3 + TypeScript + FastAPI + LangGraph。AI 层支持 Ollama 本地模型与 OpenAI Responses API；混合模式默认使用本地模型，GPT-5 作为复杂任务的云端升级路径。

本地存储使用 SQLite，资料检索采用带来源校验的文本摘录。升级方案中的 PostgreSQL、Qdrant、S3、队列 worker、OIDC 登录、实时多人编辑、完整 BKT / 间隔遗忘模型、图片 OCR 与 LMS 集成尚未实现。当前掌握度使用「70% 历史值 + 30% 本次得分率」的可解释更新；考试准备度为已评估知识点掌握度均值，不是分数预测。示例题目每个知识点使用预编写的固定选项，真实课程出题才会调用 GPT-5。

## 比赛提交信息

- 公网 Demo：部署完成后填写真实可访问地址（当前仓库不承诺未验证链接）。
- 健康检查：`<公网 Demo URL>/api/health`
- 登录：支持评审登录；知乎 OAuth 是否可用取决于部署环境中的 `ZHIHU_CLIENT_ID`、`ZHIHU_CLIENT_SECRET` 和已登记的回调地址。
- 测试账号：见 [SUBMISSION_ACCESS.md](SUBMISSION_ACCESS.md)。
- 产品说明：见 [docs/产品说明计划书.md](docs/产品说明计划书.md)。

### 知乎 OAuth 配置

OAuth 仅在服务端读取以下环境变量：`ZHIHU_CLIENT_ID`、`ZHIHU_CLIENT_SECRET`、`ZHIHU_REDIRECT_URI`、`EXAM_RADAR_SESSION_SECRET`。密钥不得写入前端、仓库或构建产物。部署后请在知乎应用后台将回调地址登记为与 `ZHIHU_REDIRECT_URI` 完全一致的 HTTPS 地址。

未配置正式知乎应用凭据时，系统会显示明确的 OAuth 不可用提示，并使用标注为“评审登录”的独立入口；该入口不会伪装成知乎登录。

### 数据与演示边界

内置 Machine Learning 课程是 authored demo 数据，用于展示完整交互，不是真实大学试卷，也不构成确定性押题。线上多人使用需要持久化存储（Vercel Blob 或其他受支持存储）和稳定的会话密钥。

### Reviewer access configuration

Set `EXAM_RADAR_REVIEWER_USERNAME` and a strong `EXAM_RADAR_REVIEWER_PASSWORD` in the deployment environment. Do not commit the password. Set `EXAM_RADAR_ADMIN_TOKEN` only if you need the protected login statistics endpoint `/api/admin/login-stats`.
