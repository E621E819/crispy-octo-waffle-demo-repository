# Exam Radar 升级方案

## 一、从需求文档提炼出的原始要求

项目要把教学大纲、讲义、Tutorial、作业、历年试卷和个人答题记录，串成一条可验证的学习闭环：

`课程资料 → Course Knowledge Map → Question DNA → Exam Priority → 变式练习 → 作答反馈 → Knowledge Tracing → 下一题`

三个核心模块：

1. **Course Intelligence**：多格式上传、解析、课程知识地图/思维导图、知识点与 CLO/题目/来源关联。
2. **Exam Intelligence**：提取每道题的 Question DNA，分析教授题型分布，计算可解释的 Exam Priority Score。
3. **Adaptive Practice**：改变情境、数据和措辞但保留推理结构；通过 Critic、Similarity Checker、Difficulty Evaluator、Answer Validator 后再入库；依据知识点 × 认知层级掌握度推荐下一题。

文档样例中的有效数据可以直接作为 Demo 数据：Exam Readiness 78%、KNN Priority 91、Logistic Regression Priority 94；教授题型分布为 Explain 27%、Compare 24%、Calculation 21%、Scenario 18%、Definition 10%；示例中 Precision 92% / Recall 58% / F1 31%。

## 二、建议的产品定位

把 Exam Radar 定位为 **Exam-aware learning OS**：面向国际高校课程的“有来源依据的考试情报与个性化练习工作区”。差异化不是生成一份总结，而是把每道题拆成 Question DNA，用课程目标、历年题型和个人薄弱点共同决定先学什么，并验证每道变式题是否真的改变了情境而保留了推理。

## 三、升级后的信息架构

左侧固定导航：Overview / Knowledge Map / Exam DNA / Practice Studio / Revision Pack / Study Room。

首页重点展示：

- 考试倒计时与 Exam Readiness
- Top 5 Priority Topics
- 掌握度与薄弱认知层级
- “Why this score” 解释入口
- Next best question
- 课程协作成员与最近活动

关键页面：

- **Course Onboarding**：拖拽上传 PDF、DOCX、图片，自动识别资料类型；显示解析进度、章节覆盖、缺失材料和引用覆盖率。
- **Knowledge Map**：章节 → CLO → 知识点 → 历年题的可缩放关系图；点击节点查看页码来源、相关题目和生成资料入口。
- **Exam DNA**：按知识点、Bloom 层级、题型、年份和分值筛选；展示题型分布和 Question DNA 详情。
- **Practice Studio**：选择章节、难度、认知层级和题型；生成后展示“context/data/wording changed, reasoning preserved”和 Critic 评分；提交后显示引用式反馈。
- **Revision Pack**：勾选章节生成 Notes、Key Concepts、Formula Sheet、Cheat Sheet、Model Answers；支持 Quick 5 / Standard 15 / Full 30，并导出 PDF/DOCX。
- **Study Room**：共享课程资料、知识地图和复习包，支持评论、@提及、题集分享；个人答案和薄弱点默认私密。

## 四、必须修正的算法表达

文档把加权求和称为“逻辑回归”，比赛版建议改成可解释归一化加权分数，并在界面显示贡献条：

`Priority = .25 Frequency + .20 Marks + .15 Recency + .15 TeachingPlan + .10 QuestionDiversity + .15 StudentWeakness`

等真实答题结果和标签积累后，再训练模型校准权重。教师命题模式必须显示样本量、年份范围和置信度，不能包装成确定性押题。

首版掌握度可用简化 BKT/mastery：按“知识点 × 认知层级”记录，答对上调、答错下调并随时间衰减；推荐优先选择高 Priority 且 mastery < 0.6 的项目，并解释推荐原因。

## 五、多人和国际化升级

借鉴 Linear 的导航与信息密度、Notion 的工作区、Miro 的画布、Quizlet/Anki 的练习反馈、Khan Academy 的掌握度路径。支持中英切换、原文与中文解释并列、时区、成绩制式、WCAG 键盘导航、LaTeX/代码题和 RTL 预留。协作先做共享课程空间、评论和共同复习包，不急于实现完整实时多人画布。

## 六、技术落地

Vue 3 + Vite + TypeScript；Tailwind + Radix；Vue Flow/Cytoscape.js；FastAPI；LangGraph；Celery/Redis；PostgreSQL 存课程、题目、权限和成绩；Qdrant 做文档检索；S3 存原文件；OIDC（Google/Microsoft）+ RBAC；解析链加入 OCR、版面分析、异步进度、失败重试。每个结论和答案保留 `source_ref`（文件、页码、段落）与 confidence。

## 七、比赛迭代顺序

- **P0（1 周）**：上传 → 解析 → 知识地图 → 3 个重点 → 3 道示例题。
- **P1（2 周）**：Priority Score、Question DNA、变式生成、Critic、答题反馈。
- **P2（2 周）**：简化知识追踪、Revision Pack、来源引用、共享评论。
- **P3**：教师模式、题型趋势、PWA/LMS 集成、实时协同。

现场 Demo 只讲一条主线：上传一门课 → 查看地图 → 点击 KNN 看到 91 分及构成 → 生成变式题 → 答错后 Recall/F1 薄弱点变化 → 导出引用式复习包。

## 八、UI 视觉方向

暖白画布 + 深墨色文字 + 靛蓝/青绿主色，珊瑚色表示 Critical，琥珀色表示 Important；16px 圆角、细边框、轻阴影、Swiss editorial grid。字体建议 Inter + Noto Sans SC。页面要像国际化 SaaS 工作区，而不是传统教育后台。

## 九、Image2 生成提示词

```text
Use case: ui-mockup
Asset type: high-fidelity desktop SaaS dashboard
Create a polished collaborative web app UI for “Exam Radar”, an AI exam intelligence and study workspace for international university students. Show a left navigation rail with Overview, Knowledge Map, Exam DNA, Practice Studio, Revision Pack, Study room; a course selector for Data Structures; a top bar with workspace search, exam countdown, language switcher, Invite button, and collaborator avatars. Main dashboard: 78% Exam Readiness ring, priority topic cards with scores 94/91, “Why this score” contribution bars, a clean node-based Course Knowledge Map, a “Next best question” card, and a collaborative Study Room panel. Use concise legible English labels with a few bilingual labels. Warm ivory canvas, near-black typography, indigo primary, mint success, coral critical, amber important. Inspired by Linear, Notion, Miro, Quizlet, and modern international SaaS products. Editorial Swiss grid, subtle borders and shadows, dense but calm, accessible contrast, realistic UI only, no device frame, no marketing poster, no fake logos, no watermark, no unreadable placeholder text. 16:10 desktop composition.
```

Image2 状态：本环境当前没有可调用的内置 image_gen，也没有 `OPENAI_API_KEY`，因此已完成提示词和可评审的本地布局预览，待启用 Image2 后可直接生成成稿。

## 十、按“GPT + Claude 结合体”重构 UI

### 设计定位

将 Exam Radar 设计成**对话式学习工作台**：GPT 风格负责快速多轮对话、工具调用和生成动作；Claude 风格负责项目级资料上下文、长文档阅读和可编辑 Artifact。

### 三栏布局

- **左栏：Project / Session**。课程项目、最近会话、新建学习会话、资料入口和成员状态。
- **中栏：AI Study Session**。用户提问、流式回答、工具调用 chips、`/practice`、`/map`、`/revise` 命令、多模态附件和引用。
- **右栏：Context / Artifact**。可切换 Knowledge Map、Question DNA、Revision Pack、批改结果；支持编辑、版本、来源页码和导出。

### 交互原则

- 用户问“我该先复习什么”，中栏回答优先级；右栏同步打开 Priority Artifact。
- 用户点击“Practice this weakness”，中栏生成题目；右栏展示 Question DNA、变式检查和来源。
- 用户说“整理成复习包”，右栏生成可编辑长文档，支持章节勾选和 PDF/DOCX 导出。
- 把 78% Readiness、94/91 Priority、Recall 58% 等指标做成可被对话调用的 Artifact，而不是孤立卡片。

### 视觉规范

暖象牙背景 `#FAF9F6`、石墨文字、靛蓝主操作色、Claude 风格珊瑚色作为 AI 状态强调；薄边框、柔和圆角、长文本可读性、少量阴影。保留协作者头像、Share、来源脚注和“Explain this score”。避免霓虹渐变、传统教育后台表格和营销海报感。

对应的三栏 UI 预览：

[exam-radar-gpt-claude-preview.png](C:\Users\34618\Desktop\知乎黑客松\output\imagegen\exam-radar-gpt-claude-preview.png)

### 更新后的 Image2 提示词

```text
Use case: ui-mockup
Asset type: high-fidelity desktop collaborative AI study workspace
Create a cohesive hybrid ChatGPT × Claude style desktop web app for “Exam Radar”, an AI exam intelligence workspace for international university students. Three-pane layout: left dark project sidebar with course projects and recent study sessions; center conversational AI study thread with a user question, streaming assistant answer, tool chips, source citations, and a multimodal prompt composer; right light context rail showing an editable Artifact called “Course Knowledge Map” with priority topics KNN 91 and Logistic Regression 94, mastery Recall 58%, source files, and a “Practice this weakness” action. Include top course breadcrumb, exam countdown, Share button, and four collaborator avatars. ChatGPT-inspired fast conversational workflow plus Claude-inspired long-document context and editable artifact panel. Warm ivory canvas #FAF9F6, graphite text, indigo primary action, restrained coral AI accent, thin borders, soft 16px corners, subtle shadows, generous whitespace, excellent typography, realistic legible English UI labels with a few Chinese bilingual labels. Premium international SaaS product design, calm and focused, no device frame, no marketing poster, no fake logos, no watermark, no unreadable placeholder text, no neon gradients. 16:10 desktop composition.
```
