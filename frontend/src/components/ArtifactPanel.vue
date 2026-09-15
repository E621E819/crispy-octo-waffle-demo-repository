<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { BookOpen, Check, ChevronDown, Download, FileText, FlaskConical, FolderOpen, Loader2, LockKeyhole, Map, Pencil, Plus, Radar, RefreshCw, Sparkles, Trash2, Upload, CircleAlert } from 'lucide-vue-next'
import type { Course, ExamAnalysis, Pack, Question, Tab } from '../types'
import KnowledgeMap from './KnowledgeMap.vue'
import './artifact.css'

const props = defineProps<{
  course: Course
  tab: Tab
  selectedTopicId: string
  question: Question | null
  examAnalysis?: ExamAnalysis | null
  packs: Pack[]
  busy: boolean
  language: 'en' | 'zh'
}>()
const emit = defineEmits<{
  (e: 'update:tab', value: Tab): void
  (e: 'select-topic', id: string): void
  (e: 'practice', topicId: string): void
  (e: 'source', materialId: string): void
  (e: 'upload'): void
  (e: 'analyze'): void
  (e: 'analyze-exams'): void
  (e: 'delete-material', id: string): void
  (e: 'generate-pack', value: { topicIds: string[]; format: 'notes' | 'formulas' | 'flashcards'; detail: 'quick' | 'standard' | 'full' }): void
  (e: 'save-pack', value: { id: string; content: string }): void
  (e: 'export-pack', value: { id: string; format: 'docx' | 'pdf' | 'md' }): void
}>()

const zh = computed(() => props.language === 'zh')
const selectedTopic = computed(() => props.course.topics.find(t => t.id === props.selectedTopicId) || props.course.topics[0])
const selectedIds = ref<string[]>([])
const noteFormat = ref<'notes' | 'formulas' | 'flashcards'>('notes')
const noteDetail = ref<'quick' | 'standard' | 'full'>('standard')
const editing = ref<Record<string, string>>({})
const openEditor = ref<Record<string, boolean>>({})
const expandedPastQuestion = ref<Record<string, boolean>>({})
const sortedTopics = computed(() => [...props.course.topics].sort((a, b) => b.priority - a.priority))
const topicGroups = computed(() => [...new Set(props.course.topics.map(topic => topic.chapter))].map(chapter => ({ chapter, topics: props.course.topics.filter(topic => topic.chapter === chapter) })))
const packFormats = computed(() => [{ id: 'notes' as const, label: zh.value ? '复习笔记' : 'Notes' }, { id: 'formulas' as const, label: zh.value ? '公式速查' : 'Formulas' }, { id: 'flashcards' as const, label: zh.value ? '记忆卡片' : 'Flashcards' }])
const packDetails = computed(() => [{ id: 'quick' as const, label: zh.value ? '速览' : 'Quick' }, { id: 'standard' as const, label: zh.value ? '标准' : 'Standard' }, { id: 'full' as const, label: zh.value ? '详细' : 'Detailed' }])
const examLabel = computed(() => {
  if (!props.course.examDate) return zh.value ? '尚未设置考试日期' : 'Exam date not set'
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const exam = new Date(`${props.course.examDate}T00:00:00`)
  const days = Math.round((exam.getTime() - today.getTime()) / 86400000)
  if (!Number.isFinite(days)) return zh.value ? '考试日期待确认' : 'Exam date to be confirmed'
  if (days < 0) return zh.value ? '考试日期已过' : 'Exam date has passed'
  return zh.value ? `距离考试还有 ${days} 天` : `${days} days until your exam`
})
const pastPaperCount = computed(() => props.course.materials.filter(material => material.kind === 'past_paper').length)
const canAnalyzeExams = computed(() => props.course.materials.some(material => material.kind === 'past_paper' && material.status === 'ready'))
watch(() => props.course.id, () => {
  selectedIds.value = props.course.topics.some(topic => topic.id === props.selectedTopicId) ? [props.selectedTopicId] : props.course.topics.slice(0, 1).map(topic => topic.id)
  editing.value = {}
  openEditor.value = {}
  expandedPastQuestion.value = {}
}, { immediate: true })
watch(() => props.course.topics, (topics) => {
  selectedIds.value = selectedIds.value.filter(id => topics.some(topic => topic.id === id))
})
const tabItems = computed(() => [
  { id: 'radar' as Tab, label: zh.value ? '雷达' : 'Radar', icon: Radar },
  { id: 'map' as Tab, label: zh.value ? '知识地图' : 'Map', icon: Map },
  { id: 'dna' as Tab, label: 'Question DNA', icon: FlaskConical },
  { id: 'notes' as Tab, label: zh.value ? '复习包' : 'Packs', icon: FileText },
  { id: 'materials' as Tab, label: zh.value ? '资料' : 'Materials', icon: FolderOpen },
])
const factorItems = computed(() => selectedTopic.value ? [
  { label: zh.value ? '出题频率' : 'Exam frequency', value: selectedTopic.value.frequency, weight: 25 },
  { label: zh.value ? '分值占比' : 'Mark allocation', value: selectedTopic.value.marks, weight: 20 },
  { label: zh.value ? '近期趋势' : 'Recency', value: selectedTopic.value.recency, weight: 15 },
  { label: zh.value ? '教学计划' : 'Teaching plan', value: selectedTopic.value.teachingPlan, weight: 15 },
  { label: zh.value ? '题型多样性' : 'Question variety', value: selectedTopic.value.diversity, weight: 10 },
  { label: zh.value ? '个人薄弱度' : 'Personal weakness', value: selectedTopic.value.mastery === null ? 50 : 100 - selectedTopic.value.mastery, weight: 15 },
] : [])
function toggleTopic(id: string) { selectedIds.value = selectedIds.value.includes(id) ? selectedIds.value.filter(x => x !== id) : [...selectedIds.value, id] }
function toggleChapter(chapter: string) {
  const ids = props.course.topics.filter(topic => topic.chapter === chapter).map(topic => topic.id)
  const selected = ids.every(id => selectedIds.value.includes(id))
  selectedIds.value = selected ? selectedIds.value.filter(id => !ids.includes(id)) : [...new Set([...selectedIds.value, ...ids])]
}
function chapterSelected(chapter: string) { return props.course.topics.filter(topic => topic.chapter === chapter).every(topic => selectedIds.value.includes(topic.id)) }
function savePack(pack: Pack) { emit('save-pack', { id: pack.id, content: editing.value[pack.id] ?? pack.content }) }
function packText(pack: Pack) { return editing.value[pack.id] ?? pack.content }
function markdown(content: string) { return DOMPurify.sanitize(marked.parse(content, { async: false, breaks: true }) as string) }
function sourceName(id: string) { return props.course.materials.find(material => material.id === id)?.name ?? (zh.value ? '查看来源' : 'View source') }
function formattedDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString(zh.value ? 'zh-CN' : 'en-US', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <aside class="artifact-panel" :aria-label="zh ? 'Exam Radar 智能工作区' : 'Exam Radar artifact workspace'">
    <header class="artifact-header">
      <div class="artifact-title-wrap">
        <div class="artifact-eyebrow"><Sparkles :size="13" />{{ zh ? '你的学习工作区' : 'YOUR LEARNING WORKSPACE' }}</div>
        <h2>{{ zh ? '学习产物' : 'Artifacts' }}<span class="artifact-header-dot"></span></h2>
      </div>
      <span v-if="course.isDemo" class="artifact-demo-badge">{{ zh ? '示例课程' : 'DEMO COURSE' }}</span>
      <span v-else class="artifact-course-badge">{{ course.code || (zh ? '个人课程' : 'Personal course') }}</span>
    </header>
    <nav class="artifact-tabs" :aria-label="zh ? '学习工具' : 'Learning tools'">
      <button v-for="item in tabItems" :key="item.id" :class="['artifact-tab', { active: tab === item.id }]" :aria-current="tab === item.id ? 'page' : undefined" @click="emit('update:tab', item.id)">
        <component :is="item.icon" :size="14" /><span>{{ item.label }}</span>
      </button>
    </nav>

    <section v-if="tab === 'radar'" class="artifact-scroll">
      <div class="readiness-card">
        <div><span class="artifact-label">{{ zh ? '考试准备度' : 'Exam readiness' }}</span><strong>{{ course.readiness == null ? '—' : `${course.readiness}%` }}</strong><p>{{ examLabel }}</p></div>
        <div class="readiness-ring" :style="{ '--progress': `${course.readiness ?? 0}%` }" aria-hidden="true"><span>{{ course.readiness ?? '—' }}</span></div>
      </div>
      <template v-if="selectedTopic">
        <div class="topic-detail-card">
          <div class="topic-detail-heading">
            <div><span class="artifact-label">{{ selectedTopic.chapter }}</span><h3>{{ selectedTopic.title }}</h3></div>
            <span class="priority-pill">{{ Math.round(selectedTopic.priority) }}<span>{{ zh ? '优先级' : 'priority' }}</span></span>
          </div>
          <p class="topic-summary">{{ selectedTopic.summary }}</p>
          <div class="mastery-row"><span>{{ zh ? '掌握度' : 'Mastery' }}</span><span class="private-badge"><LockKeyhole :size="10" />{{ zh ? '仅你可见' : 'Only you' }}</span><strong>{{ selectedTopic.mastery == null ? (zh ? '待评估' : 'Unassessed') : `${Math.round(selectedTopic.mastery)}%` }}</strong></div>
          <div class="mastery-track"><i :style="{ width: `${selectedTopic.mastery ?? 0}%` }"></i></div>
          <button class="primary-btn full" :disabled="busy" @click="emit('practice', selectedTopic.id)"><Sparkles :size="14" />{{ zh ? '练习这个知识点' : 'Practice this concept' }}</button>
          <div v-if="selectedTopic.sourceIds.length" class="artifact-sources">
            <span>{{ zh ? '来源' : 'Sources' }}</span>
            <button v-for="(sourceId, index) in selectedTopic.sourceIds" :key="sourceId" :title="sourceName(sourceId)" @click="emit('source', sourceId)"><BookOpen :size="10" />{{ index + 1 }}</button>
          </div>
        </div>
        <details class="factor-card" open>
          <summary><h3>{{ zh ? '为什么值得优先学习' : 'Why this is next' }}</h3><ChevronDown :size="13" /></summary>
          <div class="artifact-factor-key"><span>{{ zh ? '评估因素' : 'Factor' }}</span><span>{{ zh ? '评分 / 权重' : 'Score / weight' }}</span></div>
          <div v-for="factor in factorItems" :key="factor.label" class="factor-row">
            <span>{{ factor.label }}</span><div class="factor-bar"><i :style="{ width: `${factor.value}%` }"></i></div><b>{{ Math.round(factor.value) }}</b><small>{{ factor.weight }}%</small>
          </div>
          <p v-if="selectedTopic.mastery === null" class="artifact-factor-note">{{ zh ? '掌握度未知时，个人薄弱度暂按中性值 50 计分。' : 'Until assessed, personal weakness uses a neutral score of 50.' }}</p>
          <div v-if="selectedTopic.reasoning.length" class="reasoning-list"><p v-for="reason in selectedTopic.reasoning" :key="reason"><Check :size="12" />{{ reason }}</p></div>
        </details>
        <div class="section-heading topic-list-heading"><h3>{{ zh ? '课程雷达' : 'Course radar' }}</h3><span class="muted">{{ course.topics.length }} {{ zh ? '个知识点' : 'concepts' }}</span></div>
        <button v-for="topic in sortedTopics" :key="topic.id" :class="['topic-list-item', { selected: topic.id === selectedTopicId }]" :aria-pressed="topic.id === selectedTopicId" @click="emit('select-topic', topic.id)">
          <span class="topic-dot" :class="{ urgent: topic.priority >= 80 }"></span><span class="topic-name">{{ topic.title }}<small>{{ topic.chapter }}</small></span><span class="topic-score">{{ Math.round(topic.priority) }}</span><ChevronDown :size="13" class="rotate-270" />
        </button>
      </template>
      <div v-else class="empty-state compact">
        <div class="empty-icon"><Radar :size="24" :stroke-width="1.4" /></div>
        <h3>{{ zh ? '建立你的学习雷达' : 'Build your learning radar' }}</h3>
        <p>{{ zh ? '从课程资料开始，找出重点知识、出题规律与个人薄弱点。' : 'Start with course materials to discover key concepts, exam patterns, and your next focus.' }}</p>
        <button class="primary-btn" @click="emit('update:tab', 'materials')"><FolderOpen :size="14" />{{ zh ? '添加课程资料' : 'Add course materials' }}</button>
      </div>
    </section>

    <section v-else-if="tab === 'map'" class="artifact-scroll">
      <KnowledgeMap :course="course" :selected-topic-id="selectedTopicId" :language="language" @select-topic="id => emit('select-topic', id)" @practice="id => !busy && emit('practice', id)" />
      <button v-if="!course.topics.length" class="outline-btn full" @click="emit('update:tab', 'materials')"><FolderOpen :size="14" />{{ zh ? '前往课程资料' : 'Go to materials' }}</button>
    </section>

    <section v-else-if="tab === 'dna'" class="artifact-scroll dna-section">
      <div class="artifact-section-intro"><span class="artifact-eyebrow">{{ zh ? '从历年题目到下一次练习' : 'FROM PAST PAPERS TO WHAT’S NEXT' }}</span><h3>Question DNA</h3><p>{{ zh ? '看清历年卷的考查模式，再把知识转化为练习。' : 'Discover exam patterns, then turn insight into practice.' }}</p></div>
      <div class="artifact-exam-section">
        <div class="artifact-exam-heading"><h4>{{ zh ? '历年卷分析' : 'Past paper analysis' }}</h4><span>{{ pastPaperCount }} {{ zh ? '份资料' : 'sources' }}</span></div>
        <button class="outline-btn full artifact-exam-analyze" :disabled="busy || !canAnalyzeExams" @click="emit('analyze-exams')"><Loader2 v-if="busy" class="spin" :size="14" /><FlaskConical v-else :size="14" />{{ busy ? (zh ? '正在处理…' : 'Working…') : (zh ? '分析历年卷' : 'Analyze past papers') }}</button>
        <p v-if="!canAnalyzeExams" class="artifact-exam-help">{{ zh ? '请在资料页上传可读取的历年试卷。' : 'Upload readable past papers in Materials to begin.' }}<button @click="emit('update:tab', 'materials')">{{ zh ? '前往资料' : 'Go to materials' }}</button></p>
        <template v-if="examAnalysis">
          <div class="artifact-exam-overview">
            <div class="artifact-exam-metrics"><div><b>{{ examAnalysis.sampleSize }}</b><span>{{ zh ? '道可识别题目' : 'identified questions' }}</span></div><div><b class="artifact-exam-years">{{ examAnalysis.yearRange ? examAnalysis.yearRange.start + '–' + examAnalysis.yearRange.end : '—' }}</b><span>{{ zh ? '年份覆盖' : 'year coverage' }}</span></div><span v-if="examAnalysis.isDemo" class="artifact-demo-badge">{{ zh ? '示例分析' : 'DEMO ANALYSIS' }}</span></div>
            <div v-if="examAnalysis.patterns.length" class="artifact-exam-patterns">
              <span class="artifact-subheading">{{ zh ? '题目任务分布' : 'Question task distribution' }}</span>
              <div v-for="(pattern, index) in examAnalysis.patterns" :key="`${pattern.task}-${index}`" class="artifact-pattern-row"><div><span>{{ pattern.task }}</span><small>{{ pattern.count }} {{ zh ? '题' : 'questions' }}<b>{{ Math.round(pattern.percentage) }}%</b></small></div><div class="artifact-pattern-track"><i :style="{ width: `${Math.max(0, Math.min(100, pattern.percentage))}%` }"></i></div></div>
            </div>
            <p v-else class="artifact-exam-help">{{ zh ? '尚未识别出足够的题目模式。' : 'No question patterns were identified in this sample.' }}</p>
            <p class="artifact-coverage-note"><CircleAlert :size="12" /><span>{{ examAnalysis.coverageNote || (zh ? '分析只覆盖已上传且可读取的历年卷。' : 'Analysis covers only the uploaded, readable past papers.') }}</span></p>
          </div>
          <div v-if="examAnalysis.questions.length" class="artifact-past-questions">
            <div class="artifact-exam-heading"><h4>{{ zh ? '历年题目 DNA' : 'Past question DNA' }}</h4><span>{{ examAnalysis.questions.length }} {{ zh ? '条记录' : 'records' }}</span></div>
            <article v-for="(pastQuestion, index) in examAnalysis.questions" :key="pastQuestion.id" class="artifact-past-question">
              <button class="artifact-past-question-trigger" :aria-expanded="!!expandedPastQuestion[pastQuestion.id]" @click="expandedPastQuestion[pastQuestion.id] = !expandedPastQuestion[pastQuestion.id]"><span class="artifact-past-number">{{ String(index + 1).padStart(2, '0') }}</span><span class="artifact-past-title"><b>{{ pastQuestion.concept }}</b><small>{{ pastQuestion.year ?? (zh ? '年份未知' : 'Year unknown') }} · {{ pastQuestion.marks }} {{ zh ? '分' : 'marks' }}</small></span><ChevronDown :size="14" :class="{ 'artifact-past-expanded': expandedPastQuestion[pastQuestion.id] }" /></button>
              <div v-if="expandedPastQuestion[pastQuestion.id]" class="artifact-past-body"><dl><div><dt>{{ zh ? '考查任务' : 'Task' }}</dt><dd>{{ pastQuestion.task }}</dd></div><div><dt>{{ zh ? '布鲁姆层级' : 'Bloom’s level' }}</dt><dd>{{ pastQuestion.cognitiveLevel }}</dd></div></dl><div v-if="pastQuestion.reasoningSkills.length" class="artifact-reasoning-skills"><span>{{ zh ? '考查的推理能力' : 'Reasoning skills' }}</span><div><span v-for="skill in pastQuestion.reasoningSkills" :key="skill">{{ skill }}</span></div></div><div v-if="pastQuestion.sourceIds.length" class="artifact-sources"><span>{{ zh ? '来源' : 'Sources' }}</span><button v-for="(sourceId, sourceIndex) in pastQuestion.sourceIds" :key="sourceId" :title="sourceName(sourceId)" :aria-label="sourceName(sourceId)" @click="emit('source', sourceId)"><BookOpen :size="10" />{{ sourceIndex + 1 }}</button></div></div>
            </article>
          </div>
        </template>
        <div v-else-if="canAnalyzeExams" class="artifact-exam-awaiting"><FileText :size="16" :stroke-width="1.4" /><p>{{ zh ? '分析已上传的历年卷，查看题型分布、认知层级与每道题的来源。' : 'Analyze your uploaded past papers to reveal task patterns, cognitive levels, and each question’s source.' }}</p></div>
      </div>
      <template v-if="question">
        <div class="artifact-exam-heading artifact-generated-heading"><h4>{{ zh ? '当前生成的练习' : 'Your generated practice' }}</h4><Sparkles :size="12" /></div>
        <article class="dna-card">
          <div class="dna-card-header"><div><span class="artifact-label">{{ zh ? '当前练习' : 'Current practice' }}</span><h3>{{ question.prompt }}</h3></div><span v-if="question.isDemo" class="artifact-demo-badge">DEMO</span></div>
          <div class="dna-meta"><span>{{ question.marks }} {{ zh ? '分' : 'marks' }}</span><span>{{ question.difficulty }}</span><span>{{ question.dna.cognitiveLevel }}</span></div>
          <div class="dna-grid"><div><span>{{ zh ? '核心概念' : 'Core concept' }}</span><b>{{ question.dna.concept }}</b></div><div><span>{{ zh ? '变式方法' : 'Transformation' }}</span><b>{{ question.dna.transformation }}</b></div></div>
          <div class="artifact-subheading">{{ zh ? '生成器与评审器检查' : 'Generator & critic checks' }}</div>
          <div v-if="question.checks.length" class="check-list">
            <div v-for="check in question.checks" :key="check.name" :class="['dna-check', { passed: check.passed }]"><Check v-if="check.passed" :size="14" /><CircleAlert v-else :size="14" /><span><b>{{ check.name }}</b><small>{{ check.detail }}</small></span></div>
          </div>
          <p v-else class="artifact-factor-note">{{ zh ? '该题尚无评审记录。' : 'No critic checks are available for this question.' }}</p>
          <p class="artifact-dna-note"><LockKeyhole :size="12" />{{ zh ? '提交答案后查看评分、解析和掌握度变化。' : 'Submit your answer to reveal feedback and mastery updates.' }}</p>
          <div v-if="question.sourceIds.length" class="artifact-sources"><span>{{ zh ? '依据资料' : 'Grounded in' }}</span><button v-for="(sourceId, index) in question.sourceIds" :key="sourceId" :title="sourceName(sourceId)" @click="emit('source', sourceId)"><BookOpen :size="10" />{{ index + 1 }}</button></div>
        </article>
      </template>
      <div v-else class="empty-state compact">
        <div class="empty-icon"><FlaskConical :size="24" :stroke-width="1.4" /></div><h3>{{ zh ? '拆解下一道好题' : 'Unpack your next question' }}</h3><p>{{ zh ? '选择一个知识点开始练习，即可查看核心概念、认知层级与变式检查。' : 'Start a practice question to see its core concept, cognitive level, and validation checks.' }}</p>
        <button v-if="selectedTopic" class="primary-btn" :disabled="busy" @click="emit('practice', selectedTopic.id)"><Sparkles :size="14" />{{ zh ? '开始练习' : 'Start practice' }}</button>
        <button v-else class="outline-btn" @click="emit('update:tab', 'materials')">{{ zh ? '先添加课程资料' : 'Add course materials first' }}</button>
      </div>
    </section>

    <section v-else-if="tab === 'notes'" class="artifact-scroll notes-section">
      <div class="artifact-section-intro"><span class="artifact-eyebrow">{{ zh ? '属于你的复习资料' : 'MADE FOR YOUR NEXT EXAM' }}</span><h3>{{ zh ? '复习包' : 'Study packs' }}</h3><p>{{ zh ? '把课程知识整理成可以带走的复习资料。' : 'Turn course knowledge into something you can keep.' }}</p></div>
      <div v-if="course.topics.length" class="notes-controls">
        <div class="section-heading"><h3>{{ zh ? '选择复习范围' : 'Choose your focus' }}</h3><span class="muted">{{ selectedIds.length }} {{ zh ? '项已选' : 'selected' }}</span></div>
        <div class="topic-checks">
          <div v-for="group in topicGroups" :key="group.chapter" class="artifact-check-group">
            <label class="artifact-chapter-check"><input type="checkbox" :checked="chapterSelected(group.chapter)" @change="toggleChapter(group.chapter)" /><span>{{ group.chapter }}</span><small>{{ group.topics.length }}</small></label>
            <label v-for="topic in group.topics" :key="topic.id" class="topic-check"><input type="checkbox" :checked="selectedIds.includes(topic.id)" @change="toggleTopic(topic.id)" /><span>{{ topic.title }}</span></label>
          </div>
        </div>
        <span class="artifact-input-label">{{ zh ? '形式' : 'Format' }}</span>
        <div class="segmented"><button v-for="format in packFormats" :key="format.id" :class="{ active: noteFormat === format.id }" :aria-pressed="noteFormat === format.id" @click="noteFormat = format.id">{{ format.label }}</button></div>
        <span class="artifact-input-label">{{ zh ? '详细程度' : 'Level of detail' }}</span>
        <div class="segmented"><button v-for="detail in packDetails" :key="detail.id" :class="{ active: noteDetail === detail.id }" :aria-pressed="noteDetail === detail.id" @click="noteDetail = detail.id">{{ detail.label }}</button></div>
        <button class="primary-btn full" :disabled="busy || !selectedIds.length" @click="emit('generate-pack', { topicIds: selectedIds, format: noteFormat, detail: noteDetail })"><Loader2 v-if="busy" class="spin" :size="14" /><Sparkles v-else :size="14" />{{ busy ? (zh ? '正在处理…' : 'Working…') : (zh ? '生成复习包' : 'Generate study pack') }}</button>
      </div>
      <div v-else class="artifact-pack-empty"><p>{{ zh ? '先分析课程资料，选择知识点后即可生成复习包。' : 'Analyze your course materials first, then choose concepts for a study pack.' }}</p><button class="outline-btn" @click="emit('update:tab', 'materials')">{{ zh ? '前往课程资料' : 'Go to materials' }}</button></div>
      <div class="saved-packs">
        <div class="section-heading"><h3>{{ zh ? '已保存的复习包' : 'Your saved packs' }}</h3><span class="muted">{{ packs.length }}</span></div>
        <div v-if="!packs.length" class="inline-empty"><FileText :size="15" />{{ zh ? '生成的复习包将出现在这里。' : 'Your generated packs will live here.' }}</div>
        <article v-for="pack in packs" :key="pack.id" class="pack-card">
          <div class="pack-card-head"><div><h4>{{ pack.title }}</h4><small>{{ formattedDate(pack.createdAt) }} · {{ pack.topicIds.length }} {{ zh ? '个知识点' : 'concepts' }} <span v-if="pack.isDemo" class="artifact-demo-badge">DEMO</span></small></div><button class="icon-btn" :aria-label="openEditor[pack.id] ? (zh ? '预览复习包' : 'Preview pack') : (zh ? '编辑复习包' : 'Edit pack')" :title="zh ? '编辑 / 预览' : 'Edit / preview'" :aria-pressed="!!openEditor[pack.id]" @click="openEditor[pack.id] = !openEditor[pack.id]"><BookOpen v-if="openEditor[pack.id]" :size="14" /><Pencil v-else :size="14" /></button></div>
          <textarea v-if="openEditor[pack.id]" :value="packText(pack)" :aria-label="zh ? '编辑复习包 Markdown' : 'Edit study pack markdown'" @input="editing[pack.id] = ($event.target as HTMLTextAreaElement).value"></textarea>
          <div v-else class="artifact-pack-content" v-html="markdown(packText(pack))"></div>
          <div v-if="packText(pack) !== pack.content" class="artifact-save-row"><span>{{ zh ? '有未保存修改' : 'Unsaved changes' }}</span><button class="outline-btn" :disabled="busy" @click="savePack(pack)"><Check :size="12" />{{ zh ? '保存修改' : 'Save changes' }}</button></div>
          <div class="export-row"><Download :size="12" /><button :disabled="busy || packText(pack) !== pack.content" @click="emit('export-pack', { id: pack.id, format: 'docx' })">Word</button><button :disabled="busy || packText(pack) !== pack.content" @click="emit('export-pack', { id: pack.id, format: 'pdf' })">PDF</button><button :disabled="busy || packText(pack) !== pack.content" @click="emit('export-pack', { id: pack.id, format: 'md' })">Markdown</button></div>
        </article>
      </div>
    </section>

    <section v-else class="artifact-scroll materials-section">
      <div class="material-toolbar"><div><span class="artifact-eyebrow">{{ zh ? '一切知识的起点' : 'WHERE KNOWLEDGE BEGINS' }}</span><h3>{{ zh ? '课程资料' : 'Course materials' }}</h3><p>{{ course.materials.length }} {{ zh ? '个来源文件' : 'source files' }}</p></div><button class="primary-btn" :disabled="busy" @click="emit('upload')"><Upload :size="14" />{{ zh ? '上传' : 'Upload' }}</button></div>
      <p v-if="course.materials.length" class="artifact-material-explainer">{{ zh ? '上传后点击分析，将资料整理成知识地图与考试重点。' : 'After uploading, analyze your materials to build a grounded map and exam priorities.' }}</p>
      <button v-if="course.materials.length" class="outline-btn full" :disabled="busy || !course.materials.some(material => material.status === 'ready')" @click="emit('analyze')"><Loader2 v-if="busy" class="spin" :size="14" /><RefreshCw v-else :size="14" />{{ busy ? (zh ? '正在处理…' : 'Working…') : (zh ? '分析课程资料' : 'Analyze course') }}</button>
      <div class="material-list">
        <article v-for="material in course.materials" :key="material.id" class="material-item">
          <div class="material-icon"><FileText :size="17" :stroke-width="1.5" /></div>
          <div class="material-main"><div class="material-name" :title="material.name">{{ material.name }}</div><small>{{ material.kind }}<template v-if="material.pages"> · {{ material.pages }} {{ zh ? '页' : 'pages' }}</template><span v-if="material.isDemo" class="artifact-demo-badge">DEMO</span></small>
            <p v-if="material.status === 'failed'" class="material-error">{{ material.error || (zh ? '无法处理该文件，请重新上传。' : 'Unable to process this file. Please upload it again.') }}</p><p v-else-if="material.excerpt">{{ material.excerpt }}</p>
            <span v-if="material.status === 'processing'" class="status-label processing"><Loader2 class="spin" :size="11" />{{ zh ? '处理中' : 'Processing' }}</span><span v-else-if="material.status === 'failed'" class="status-label failed"><CircleAlert :size="11" />{{ zh ? '处理失败' : 'Failed' }}</span><span v-else class="status-label ready"><Check :size="11" />{{ zh ? '可读取' : 'Ready to read' }}</span>
          </div>
          <div class="material-actions"><button v-if="material.status === 'ready'" class="icon-btn" :aria-label="`${zh ? '查看来源' : 'Read source'}: ${material.name}`" :title="zh ? '查看来源' : 'Read source'" @click="emit('source', material.id)"><BookOpen :size="14" /></button><button class="icon-btn danger" :disabled="busy" :aria-label="`${zh ? '删除' : 'Delete'}: ${material.name}`" :title="zh ? '删除文件' : 'Delete file'" @click="emit('delete-material', material.id)"><Trash2 :size="13" /></button></div>
        </article>
      </div>
      <div v-if="!course.materials.length" class="empty-state compact"><div class="empty-icon"><FolderOpen :size="24" :stroke-width="1.4" /></div><h3>{{ zh ? '让学习有据可循' : 'Give your learning a source' }}</h3><p>{{ zh ? '添加讲义、历年试卷或教学大纲。每个知识点都能回到它的来源。' : 'Add lecture notes, past exams, or a syllabus. Every concept can point back to its source.' }}</p><button class="primary-btn" @click="emit('upload')"><Plus :size="14" />{{ zh ? '选择课程文件' : 'Choose course files' }}</button></div>
    </section>
    <footer class="artifact-footer"><LockKeyhole :size="11" />{{ zh ? '个人学习数据私密保存' : 'Your learning data stays private' }}</footer>
  </aside>
</template>


