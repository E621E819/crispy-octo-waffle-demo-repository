<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ArrowUp, ArrowUpRight, BookOpen, Check, ChevronDown, ChevronRight, CircleHelp, FileText, Folder, GraduationCap, LoaderCircle, LockKeyhole, Menu, MessageSquare, PanelRightClose, PanelRightOpen, Paperclip, Plus, Search, Settings2, Share2, Sparkles, Target, Upload, X } from 'lucide-vue-next'
import ArtifactPanel from './components/ArtifactPanel.vue'
import MarkdownText from './components/MarkdownText.vue'
import { post, request } from './api'
import type { Course, ExamAnalysis, Feedback, Material, Message, Pack, Question, Session, Tab } from './types'

type Bootstrap = { user: { id: string; name: string }; mode: 'demo' | 'live' | 'hybrid' | 'local'; model: string; localModel?: string; courses: Course[] }
type Shared = { name: string; topics: Array<{ id: string; title: string; chapter: string; summary: string }>; packs: Pack[]; comments: Array<{ id: string; author: string; body: string; createdAt: string }> }
const data = ref<Bootstrap | null>(null)
const loading = ref(true)
const bootError = ref('')
const courseId = ref('')
const sessionId = ref('')
const tab = ref<Tab>('radar')
const selectedTopicId = ref('')
const composer = ref('')
const search = ref('')
const language = ref<'en' | 'zh'>('zh')
const busy = ref('')
const error = ref('')
const notice = ref('')
const sidebarOpen = ref(false)
const artifactOpen = ref(true)
const modal = ref<'create' | 'upload' | 'source' | 'share' | 'settings' | 'auth' | null>(null)
const modalElement = ref<HTMLElement>()
const courseName = ref('')
const courseCode = ref('')
const examDate = ref('')
const uploadKind = ref('lecture')
const uploadFiles = ref<File[]>([])
const source = ref<{ material: Material; text: string } | null>(null)
const shareUrl = ref('')
const displayName = ref(localStorage.getItem('exam-radar-name') || 'Mina Chen')
const question = ref<Question | null>(null)
const feedback = ref<Feedback | null>(null)
const answer = ref('')
const packs = ref<Pack[]>([])
const examAnalysis = ref<ExamAnalysis | null>(null)
const threadElement = ref<HTMLElement>()
const sharedToken = new URLSearchParams(window.location.search).get('share')
const shared = ref<Shared | null>(null)
const authConfig = ref<{ reviewerEnabled: boolean; zhihuEnabled: boolean; zhihuReason?: string }>({ reviewerEnabled: false, zhihuEnabled: false })
const authBusy = ref(false)
const authError = ref('')
const reviewerUsername = ref('')
const reviewerPassword = ref('')
const comment = ref('')
const activeCourse = computed(() => data.value?.courses.find(c => c.id === courseId.value) || null)
const session = computed(() => activeCourse.value?.sessions.find(s => s.id === sessionId.value))
const messages = computed(() => session.value?.messages ?? [])
const topics = computed(() => [...(activeCourse.value?.topics ?? [])].sort((a, b) => b.priority - a.priority))
const weakTopic = computed(() => [...topics.value].sort((a, b) => (a.mastery ?? 50) - (b.mastery ?? 50))[0])
const visibleSessions = computed(() => activeCourse.value?.sessions.filter(s => s.title.toLowerCase().includes(search.value.toLowerCase())) ?? [])
const daysLeft = computed(() => { if (!activeCourse.value?.examDate) return null; const today=new Date(); today.setHours(0,0,0,0); return Math.max(0, Math.round((new Date(activeCourse.value.examDate+'T00:00:00').getTime()-today.getTime())/86400000)) })
const initials = computed(() => (data.value?.user.name || 'You').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase())
const isBusy = computed(() => !!busy.value)
const t = (_en: string, zh: string) => zh
function formatDate(value: string) { return value ? new Date(value + 'T12:00:00').toLocaleDateString('zh-CN', { day: 'numeric', month: 'short' }) : '' }
function routeLabel(route?: string) { return ({ exam_generation: '模拟试卷生成', review_or_analysis: '考点分析', summary: '资料总结', review_plan: '复习计划', question_explanation: '题目讲解', question_answering: '题目解答', flashcards: '闪卡生成', clarification: '需要确认', general_chat: '课程问答' } as Record<string,string>)[route || ''] || '' }
function fail(e: unknown) { error.value = e instanceof Error ? e.message : String(e) }
async function scrollToBottom() { await nextTick(); threadElement.value?.scrollTo({ top: threadElement.value.scrollHeight, behavior: 'smooth' }) }
async function loadPacks() { if (courseId.value) packs.value = await request<Pack[]>('/courses/' + courseId.value + '/packs') }
async function loadExamAnalysis() { if (courseId.value) examAnalysis.value = await request<ExamAnalysis | null>('/courses/' + courseId.value + '/exam-analysis') }
async function refresh() {
  data.value = await request<Bootstrap>('/bootstrap')
  if (!data.value.courses.some(c => c.id === courseId.value)) courseId.value = data.value.courses[0]?.id ?? ''
  if (!activeCourse.value?.sessions.some(s => s.id === sessionId.value)) sessionId.value = activeCourse.value?.sessions[0]?.id ?? ''
  if (!activeCourse.value?.topics.some(p => p.id === selectedTopicId.value)) selectedTopicId.value = weakTopic.value?.id ?? ''
}
async function loadAuthConfig() { try { authConfig.value = await request('/auth/config') } catch { authConfig.value = { reviewerEnabled: false, zhihuEnabled: false } } }
async function boot() {
  loading.value = true; bootError.value = ''
  try {
    await loadAuthConfig()
    await post('/session', { name: displayName.value })
    await refresh()
    await loadPacks(); await loadExamAnalysis()
    if (sharedToken) shared.value = await request<Shared>('/shared/' + encodeURIComponent(sharedToken))
  } catch (e) { bootError.value = e instanceof Error ? e.message : 'Could not connect to the server.' }
  finally { loading.value = false }
}
async function reviewerLogin() {
  if (authBusy.value || !reviewerUsername.value.trim() || !reviewerPassword.value) return
  authBusy.value = true; authError.value = ''
  try { await post('/auth/reviewer', { username: reviewerUsername.value.trim(), password: reviewerPassword.value }); await refresh(); modal.value = null; reviewerPassword.value = ''; notice.value = '评审账号登录成功。' }
  catch (e) { authError.value = e instanceof Error ? e.message : '登录失败，请检查账号和密码。' } finally { authBusy.value = false }
}
function zhihuLogin() { window.location.href = '/api/auth/zhihu/start' }
async function logout() {
  if (authBusy.value) return
  authBusy.value = true
  try { await request('/auth/logout', { method: 'POST' }); window.location.reload() }
  catch (e) { authError.value = e instanceof Error ? e.message : '退出失败。'; authBusy.value = false }
}
function openModal(value: typeof modal.value) {
  modal.value = value
  nextTick(() => modalElement.value?.focus())
}
function closeModal() { if (!isBusy.value) modal.value = null }
function trapModal(e: KeyboardEvent) {
  if (e.key === 'Escape') closeModal()
  if (e.key !== 'Tab' || !modalElement.value) return
  const elements = Array.from(modalElement.value.querySelectorAll<HTMLElement>('button:not([disabled]), input, select, textarea, a[href]')).filter(el => el.offsetParent !== null)
  const first = elements[0], last = elements.at(-1)
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus() }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus() }
}
async function changeCourse(id: string) {
  if (isBusy.value) return
  courseId.value = id; sessionId.value = activeCourse.value?.sessions[0]?.id ?? ''; examAnalysis.value = null
  selectedTopicId.value = weakTopic.value?.id ?? ''; question.value = null; feedback.value = null
  tab.value = 'radar'; sidebarOpen.value = false
  try { await loadPacks(); await loadExamAnalysis() } catch (e) { fail(e) }
}
async function newSession() {
  if (!activeCourse.value || isBusy.value) return
  busy.value = 'Creating a session'
  try {
    const result = await post<Session>('/courses/' + courseId.value + '/sessions', { title: t('New study session', '新的学习对话') })
    await refresh(); sessionId.value = result.id; question.value = null; feedback.value = null; sidebarOpen.value = false
  } catch (e) { fail(e) } finally { busy.value = '' }
}
async function createCourse() {
  if (!courseName.value.trim() || isBusy.value) return
  busy.value = 'Creating course'
  try {
    const course = await post<Course>('/courses', { name: courseName.value.trim(), code: courseCode.value.trim(), examDate: examDate.value || null })
    await refresh(); await changeCourseAfterCreate(course.id)
    courseName.value = ''; courseCode.value = ''; modal.value = 'upload'
  } catch (e) { fail(e) } finally { busy.value = '' }
}
async function changeCourseAfterCreate(id: string) { courseId.value = id; sessionId.value = activeCourse.value?.sessions[0]?.id ?? ''; selectedTopicId.value = ''; packs.value = []; examAnalysis.value = null; question.value = null; feedback.value = null; tab.value = 'materials'; artifactOpen.value = true }
async function sendChat(value?: string) {
  const content = (value ?? composer.value).trim()
  if (!content || isBusy.value || !activeCourse.value) return
  error.value = ''; busy.value = t('Reading course sources', '正在阅读课程资料')
  try {
    if (!sessionId.value) {
      const created = await post<Session>('/courses/' + courseId.value + '/sessions', { title: content.slice(0, 55) })
      await refresh(); sessionId.value = created.id
    }
    composer.value = ''
    const target = session.value
    const temporary: Message = { id: 'pending-' + Date.now(), role: 'user', content }
    target?.messages.push(temporary)
    await scrollToBottom()
    try { await post<Message>('/courses/' + courseId.value + '/chat', { sessionId: sessionId.value, message: content, language: language.value }) }
    catch (e) { composer.value = content; throw e }
    finally { await refresh() }
    await scrollToBottom()
  } catch (e) { fail(e) } finally { busy.value = '' }
}
function onComposerKey(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); void sendChat() }
}
function startUpload() {
  error.value = ''
  if (activeCourse.value?.isDemo) { openModal('create'); notice.value = t('Create your course to upload real materials. The example course stays available.', '新建课程即可上传真实资料，示例课程会保留。') }
  else { uploadFiles.value = []; openModal('upload') }
}
function selectFiles(e: Event) { uploadFiles.value = Array.from((e.target as HTMLInputElement).files ?? []) }
async function upload() {
  if (!uploadFiles.value.length || isBusy.value) return
  error.value = ''
  try {
    for (const file of uploadFiles.value) {
      busy.value = t('Uploading ', '正在上传 ') + file.name
      const form = new FormData(); form.append('file', file); form.append('kind', uploadKind.value)
      await request('/courses/' + courseId.value + '/materials', { method: 'POST', body: form })
    }
    await refresh(); tab.value = 'materials'; artifactOpen.value = true; modal.value = null
    notice.value = t('Materials uploaded. Select Analyze course to build your knowledge map.', '资料已上传，点击分析课程即可建立知识地图。')
  } catch (e) { fail(e); await refresh().catch(() => {}) } finally { busy.value = '' }
}
async function analyze() {
  if (isBusy.value) return
  busy.value = t('GPT-5 is analyzing your course', 'GPT-5 正在分析课程'); error.value = ''
  try { await post('/courses/' + courseId.value + '/analyze'); await refresh(); tab.value = 'map'; notice.value = t('Your knowledge map is ready.', '知识地图已生成。') }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function analyzeExams() {
  if (isBusy.value) return
  busy.value = t('Reading past papers', '正在分析历年试卷'); error.value = ''
  try { examAnalysis.value = await post<ExamAnalysis>('/courses/' + courseId.value + '/exam-analysis', { language: language.value }); tab.value = 'dna'; artifactOpen.value = true; notice.value = t('Past paper patterns are ready.', '历年试卷模式分析已完成。') }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function viewSource(id: string) {
  try { source.value = await request('/courses/' + courseId.value + '/materials/' + id); openModal('source') } catch (e) { fail(e) }
}
async function deleteMaterial(id: string) {
  if (isBusy.value) return
  busy.value = 'Removing material'
  try { await request('/courses/' + courseId.value + '/materials/' + id, { method: 'DELETE' }); await refresh(); await loadPacks() }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function practice(topicId: string) {
  if (!topicId || isBusy.value) return
  busy.value = t('Generating and checking your question', '正在出题并验证答案'); error.value = ''; feedback.value = null; question.value = null; answer.value = ''
  try { question.value = await post<Question>('/courses/' + courseId.value + '/questions', { topicId, language: language.value }); selectedTopicId.value = topicId; tab.value = 'dna'; artifactOpen.value = true; await scrollToBottom() }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function submitAnswer() {
  if (!question.value || !answer.value.trim() || isBusy.value || feedback.value) return
  busy.value = t('Reviewing your reasoning', '正在评估作答')
  try { feedback.value = await post<Feedback>('/courses/' + courseId.value + '/questions/' + question.value.id + '/answers', { answer: answer.value, language: language.value }); await refresh(); await scrollToBottom() }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function generatePack(options: { topicIds: string[]; format: string; detail: string }) {
  if (isBusy.value) return
  busy.value = t('Building your revision pack', '正在生成复习资料'); error.value = ''
  try { await post('/courses/' + courseId.value + '/packs', { ...options, language: language.value }); await loadPacks(); tab.value = 'notes'; notice.value = t('Revision pack saved.', '复习资料已保存。') }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function savePack(value: { id: string; content: string }) {
  if (isBusy.value) return
  busy.value = 'Saving notes'
  try { await request('/courses/' + courseId.value + '/packs/' + value.id, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: value.content }) }); await loadPacks(); notice.value = t('Changes saved.', '修改已保存。') }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function exportPack(value: { id: string; format: string }) {
  try {
    const response = await fetch('/api/courses/' + courseId.value + '/packs/' + value.id + '/export?format=' + value.format)
    if (!response.ok) { const result = await response.json(); throw new Error(result.detail || 'Export failed.') }
    const url = URL.createObjectURL(await response.blob()); const a = document.createElement('a')
    a.href = url; a.download = 'Exam-Radar-revision.' + value.format; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { fail(e) }
}
async function shareCourse() {
  if (isBusy.value) return
  shareUrl.value = ''; openModal('share')
}
async function createShareLink() {
  if (isBusy.value) return
  busy.value = 'Creating shared snapshot'
  try { const result = await post<{ token: string; url: string }>('/courses/' + courseId.value + '/share'); shareUrl.value = window.location.origin + '/?share=' + encodeURIComponent(result.token) }
  catch (e) { fail(e) } finally { busy.value = '' }
}
async function copyLink() { try { await navigator.clipboard.writeText(shareUrl.value); notice.value = t('Share link copied.', '分享链接已复制。') } catch { notice.value = t('Select and copy the link above.', '请选择并复制链接。') } }
async function saveSettings() {
  document.documentElement.lang = 'zh-CN'
  localStorage.setItem('exam-radar-name', displayName.value)
  try { await post('/session', { name: displayName.value }); await refresh(); modal.value = null; notice.value = t('Preferences saved.', '设置已保存。') } catch (e) { fail(e) }
}
async function addComment() {
  if (!comment.value.trim() || isBusy.value || !sharedToken) return
  busy.value = 'Saving comment'
  try { await post('/shared/' + sharedToken + '/comments', { body: comment.value }); comment.value = ''; shared.value = await request('/shared/' + sharedToken) }
  catch (e) { fail(e) } finally { busy.value = '' }
}
function setTab(value: Tab) { tab.value = value; artifactOpen.value = true; sidebarOpen.value = false }
function messageContent(message: Message) {
  if (language.value !== 'zh' || !message.isDemo || !message.content.startsWith('Welcome to your Machine Learning workspace.')) return message.content
  return '欢迎来到 Machine Learning 示例工作区。我已将示例课程笔记、练习试卷和学习目标整理成学习地图。\n\n建议先复习 **Precision & Recall** 和 **F1 Score**。你可以让我解释概念、生成练习题，或将选中的知识点整理成复习包。\n\n这是明确标注的示例课程，资料和初始掌握度均为演示数据。新建自己的课程后，可使用 GPT-5 分析你上传的真实资料。'
}
onMounted(() => { localStorage.removeItem('exam-radar-language'); document.documentElement.lang = 'zh-CN'; void boot() })
</script>

<template>
  <div v-if="loading || bootError" class="boot-screen">
    <div class="brand"><span class="brand-symbol"><Target :size="25" /></span>Exam Radar</div>
    <LoaderCircle v-if="loading" class="spin" :size="28"/><h2>{{ loading ? t('Opening your workspace…','正在打开工作区…') : t('Could not reach your workspace','无法连接工作区') }}</h2>
    <p v-if="bootError">{{ bootError }}</p><button v-if="bootError" class="btn primary" @click="boot">{{ t('Try again','重试') }}</button>
  </div>
  <div v-else-if="sharedToken && shared" class="shared-page">
    <header class="shared-header"><a href="/" class="brand"><Target :size="24"/>Exam Radar</a><a href="/" class="btn">{{ t('Open my workspace','打开我的工作区') }} <ArrowUpRight :size="15"/></a></header>
    <main class="shared-main"><span class="kicker">{{ t('SHARED COURSE SNAPSHOT','共享课程快照') }}</span><h1>{{ shared.name }}</h1><p class="subtle">{{ t('A shared course map and revision library. Personal answers and mastery stay private.','共享的课程地图与复习资料库。个人答案和掌握度始终保持私密。') }}</p>
      <section class="shared-topics"><article v-for="topic in shared.topics" :key="topic.id"><small>{{ topic.chapter }}</small><h3>{{ topic.title }}</h3><p>{{ topic.summary }}</p></article></section>
      <section v-for="pack in shared.packs" :key="pack.id" class="shared-pack"><h2>{{ pack.title }}</h2><MarkdownText :content="pack.content"/></section>
      <section class="shared-discussion"><h2>{{ t('Course discussion','课程讨论') }}</h2><p v-if="!shared.comments.length" class="subtle">{{ t('Be the first to add a study note.','添加第一条学习笔记。') }}</p><article v-for="item in shared.comments" :key="item.id"><b>{{ item.author }}</b><p>{{ item.body }}</p></article><form @submit.prevent="addComment"><label for="comment">{{ t('Comment as','评论身份') }} {{ data?.user.name }}</label><textarea id="comment" v-model="comment" maxlength="3000" :placeholder="t('Share a useful explanation…','分享一个有用的解释…')" required></textarea><button class="btn primary" :disabled="isBusy || !comment.trim()">{{ t('Post comment','发表评论') }}</button></form></section>
    </main>
  </div>
  <div v-else class="app-shell" :class="{ 'artifact-hidden': !artifactOpen }">
    <div v-if="sidebarOpen" class="sidebar-scrim" @click="sidebarOpen = false"></div>
    <aside class="sidebar" :class="{ 'is-open': sidebarOpen }">
      <a class="brand" href="/"><span class="brand-symbol"><Target :size="24"/></span>Exam Radar</a>
      <button class="new-session" @click="newSession" :disabled="isBusy"><Plus :size="18"/>{{ t('New study session','新建学习对话') }}</button>
      <label class="sidebar-search"><Search :size="16"/><input v-model="search" :placeholder="t('Search conversations','搜索学习对话')" :aria-label="t('Search conversations','搜索学习对话')"/></label>
      <div class="nav-section-label">{{ t('YOUR COURSES','我的课程') }}<button @click="openModal('create')" :disabled="isBusy" :aria-label="t('Create course','新建课程')"><Plus :size="15"/></button></div>
      <div class="course-list"><button v-for="item in data?.courses" :key="item.id" class="course-item" :class="{active: courseId === item.id}" :disabled="isBusy" @click="changeCourse(item.id)"><Folder :size="18"/><span><b>{{ item.name }}</b><small>{{ item.code || t('Course workspace','课程工作区') }}<template v-if="item.isDemo"> · {{ t('Example','示例') }}</template></small></span><ChevronDown v-if="courseId === item.id" :size="14"/></button></div>
      <div class="nav-section-label workspace-label">{{ t('WORKSPACE','学习工作区') }}</div>
      <button class="nav-item" :class="{active:tab==='radar' && artifactOpen}" @click="setTab('radar')"><Target :size="17"/>{{ t('Exam Radar','考试重点') }}<span class="nav-count">{{ topics.length }}</span></button>
      <button class="nav-item" :class="{active:tab==='map' && artifactOpen}" @click="setTab('map')"><BookOpen :size="17"/>{{ t('Knowledge map','知识地图') }}</button>
      <button class="nav-item" :class="{active:tab==='dna' && artifactOpen}" @click="setTab('dna')"><Sparkles :size="17"/>{{ t('Practice studio','练习工作室') }}</button>
      <button class="nav-item" :class="{active:tab==='notes' && artifactOpen}" @click="setTab('notes')"><FileText :size="17"/>{{ t('Revision packs','复习资料') }}</button>
      <button class="nav-item" :class="{active:tab==='materials' && artifactOpen}" @click="setTab('materials')"><Paperclip :size="17"/>{{ t('Course materials','课程资料') }}<span class="nav-count">{{ activeCourse?.materials.length }}</span></button>
      <div class="nav-section-label">{{ t('RECENT SESSIONS','近期对话') }}</div>
      <div class="session-list"><button v-for="item in visibleSessions" :key="item.id" :class="{selected:sessionId===item.id}" @click="sessionId=item.id; question=null; feedback=null; sidebarOpen=false" :disabled="isBusy"><MessageSquare :size="14"/><span>{{ item.title }}</span></button><p v-if="!visibleSessions.length" class="no-results">{{ t('No conversations yet','暂无对话') }}</p></div>
      <div class="sidebar-bottom">
        <div class="exam-date" v-if="daysLeft !== null"><GraduationCap :size="20"/><div><small>{{ t('FINAL EXAM','考试日期') }}</small><b>{{ formatDate(activeCourse?.examDate || '') }} <span>· {{ daysLeft }} {{ t('days left','天后') }}</span></b></div></div>
        <button class="profile" @click="openModal('settings')"><span class="avatar">{{ initials }}</span><span><b>{{ data?.user.name }}</b><small>{{ t('Personal workspace','个人工作区') }}</small></span><Settings2 :size="17"/></button>
      </div>
    </aside>
    <div class="workspace-body">
      <header class="topbar">
        <div class="breadcrumb"><button class="icon-button mobile-menu" @click="sidebarOpen=true" :aria-label="t('Open navigation','打开导航')"><Menu :size="20"/></button><span>{{ activeCourse?.name }}</span><ChevronRight :size="14"/><b>{{ session?.title || t('Study workspace','学习工作区') }}</b></div>
        <div class="topbar-actions"><span class="privacy"><LockKeyhole :size="12"/>{{ t('Only you','仅自己可见') }}</span><button class="btn auth-entry" @click="openModal('auth')">登录</button><button class="btn share-button" @click="shareCourse" :disabled="isBusy"><Share2 :size="14"/>{{ t('Share course','分享课程') }}</button><button class="icon-button" @click="artifactOpen=!artifactOpen" :aria-label="artifactOpen ? t('Hide context panel','隐藏学习面板') : t('Show context panel','显示学习面板')"><PanelRightClose v-if="artifactOpen" :size="19"/><PanelRightOpen v-else :size="19"/></button></div>
      </header>
      <div class="work-area">
        <main class="conversation">
          <div class="conversation-top"><div class="workspace-chip"><span class="status-dot"></span>{{ t('Course assistant','课程助手') }}</div><span class="model-badge">{{ data?.mode === 'local' ? '本地模型' : data?.mode === 'live' ? 'GPT-5' : data?.mode === 'demo' ? '演示模式' : '混合模式' }} <span v-if="activeCourse?.isDemo">· {{ t('Demo','示例') }}</span></span></div>
          <div class="thread-scroll" ref="threadElement" aria-live="polite">
            <div class="thread-content">
              <section class="welcome" v-if="!messages.length"><span class="welcome-symbol"><Sparkles :size="26"/></span><h1>{{ t('A clearer path\nto your exam.','让每一步复习，\n都有方向。') }}</h1><p>{{ t('Your course, connected. Let’s turn what you know\ninto what you’re ready for.','连接课程资料，找到重点，\n通过练习真正掌握知识。') }}</p><div class="suggestions"><button @click="sendChat(t('What should I revise first? Explain the priorities using my course sources.','我应该先复习什么？请结合课程来源解释优先级。'))" :disabled="isBusy"><Target :size="17"/>{{ t('Find my revision priorities','找到我的复习重点') }}<ArrowUpRight :size="15"/></button><button @click="practice(weakTopic?.id || '')" :disabled="isBusy || !topics.length"><Sparkles :size="17"/>{{ t('Practice my weakest topic','练习我的薄弱知识点') }}<ArrowUpRight :size="15"/></button><button @click="startUpload" :disabled="isBusy"><Paperclip :size="17"/>{{ t('Add course materials','添加课程资料') }}<ArrowUpRight :size="15"/></button></div></section>
              <article v-for="message in messages" :key="message.id" class="chat-message" :class="message.role">
                <div v-if="message.role==='user'" class="user-message">{{ message.content }}</div>
                <template v-else><div class="assistant-heading"><span class="assistant-icon"><Sparkles :size="16"/></span><b>Exam Radar</b><small v-if="routeLabel(message.route)">{{ routeLabel(message.route) }}</small><small v-if="message.isDemo">{{ t('Example response','示例回答') }}</small></div><MarkdownText :content="messageContent(message)"/><div class="source-chips" v-if="message.sourceIds?.length"><button v-for="id in message.sourceIds" :key="id" @click="viewSource(id)"><FileText :size="12"/>{{ activeCourse?.materials.find(m=>m.id===id)?.name || t('Source','来源') }}<ArrowUpRight :size="11"/></button></div></template>
              </article>
              <div class="quick-actions" v-if="messages.length && !question"><button :disabled="isBusy || !weakTopic" @click="practice(weakTopic?.id || '')"><Sparkles :size="14"/>{{ t('Practice this weakness','练习薄弱点') }}</button><button @click="setTab('notes')"><FileText :size="14"/>{{ t('Build a revision pack','生成复习资料') }}</button></div>
              <section v-if="question" class="practice-card">
                <div class="practice-eyebrow"><span><Sparkles :size="15"/> {{ t('ADAPTIVE PRACTICE','个性化练习') }}</span><span>{{ question.marks }} {{ t('marks','分') }} · {{ question.difficulty }}</span></div>
                <h2>{{ question.dna.concept }}</h2><MarkdownText :content="question.prompt"/><p v-if="question.isDemo" class="demo-note">{{ t('Example question · guided demonstration','示例题目 · 用于演示学习流程') }}</p>
                <form @submit.prevent="submitAnswer"><fieldset v-if="question.options?.length" :disabled="!!feedback || isBusy"><legend>{{ t('Choose your answer','选择答案') }}</legend><label v-for="option in question.options" :key="option" class="answer-option"><input type="radio" v-model="answer" :value="option" name="answer" required/><span>{{ option }}</span></label></fieldset><template v-else><label for="answer">{{ t('Explain your reasoning','写下你的推理过程') }}</label><textarea id="answer" v-model="answer" :disabled="!!feedback || isBusy" :placeholder="t('Work through the problem here…','在此写下解题思路…')" required rows="5"></textarea></template><button v-if="!feedback" class="btn primary" :disabled="isBusy || !answer.trim()">{{ t('Submit answer','提交答案') }}<ArrowUpRight :size="15"/></button></form>
                <div class="feedback" v-if="feedback"><div class="feedback-score"><b>{{ feedback.score }} / {{ feedback.maxScore }}</b><span>{{ t('Mastery','掌握度') }} {{ feedback.masteryBefore ?? '—' }}% → {{ feedback.masteryAfter }}%</span></div><MarkdownText :content="feedback.feedback"/><details><summary>{{ t('View model answer','查看参考答案') }}</summary><MarkdownText :content="feedback.modelAnswer"/></details><button class="btn primary" :disabled="isBusy" @click="practice(feedback.nextTopicId)">{{ t('Try the next question','练习下一题') }}<ArrowUpRight :size="14"/></button></div>
              </section>
              <div class="working" v-if="isBusy"><LoaderCircle :size="17" class="spin"/><span>{{ busy }}…</span></div>
            </div>
          </div>
          <div class="composer-wrap"><form class="composer" @submit.prevent="sendChat()"><textarea v-model="composer" @keydown="onComposerKey" :placeholder="t('Ask about your course, or try something new…','询问课程问题，或开始新的学习任务…')" :aria-label="t('Message Exam Radar','向 Exam Radar 提问')" rows="2" maxlength="12000"></textarea><div class="composer-bottom"><button type="button" class="composer-attach" @click="startUpload" :disabled="isBusy" :aria-label="t('Attach course material','添加课程资料')"><Plus :size="20"/></button><button class="context-button" type="button" @click="setTab('materials')"><BookOpen :size="14"/><span>{{ activeCourse?.materials.length || 0 }} {{ t('course sources','份课程来源') }}</span><ChevronDown :size="12"/></button><span class="composer-spacer"></span><button class="send-button" type="submit" :disabled="isBusy || !composer.trim()" :aria-label="t('Send message','发送消息')"><LoaderCircle v-if="busy.includes('sources')" class="spin" :size="17"/><ArrowUp v-else :size="19"/></button></div></form><p class="composer-caption"><template v-if="activeCourse?.isDemo">{{ t('Example course with sample responses. Create a course to use GPT-5.','当前为示例课程与示例回答。新建课程即可使用 GPT-5。') }}</template><template v-else>{{ t('Answers grounded in your course. Check linked sources.','回答基于课程资料，请核对引用来源。') }}</template></p></div>
        </main>
        <section v-if="artifactOpen && activeCourse" class="artifact-host"><ArtifactPanel :course="activeCourse" :tab="tab" :selected-topic-id="selectedTopicId" :question="question" :exam-analysis="examAnalysis" :packs="packs" :busy="isBusy" :language="language" @update:tab="tab=$event" @select-topic="selectedTopicId=$event" @practice="practice" @source="viewSource" @upload="startUpload" @analyze="analyze" @analyze-exams="analyzeExams" @delete-material="deleteMaterial" @generate-pack="generatePack" @save-pack="savePack" @export-pack="exportPack"/></section>
      </div>
    </div>
  </div>
  <div v-if="error" class="toast error-toast" role="alert"><CircleHelp :size="18"/><span>{{ error }}</span><button @click="error=''" :aria-label="t('Dismiss error','关闭错误提示')"><X :size="16"/></button></div>
  <div v-else-if="notice" class="toast" role="status"><Check :size="17"/><span>{{ notice }}</span><button @click="notice=''" :aria-label="t('Dismiss notification','关闭通知')"><X :size="16"/></button></div>
  <div v-if="modal" class="modal-backdrop" @click.self="closeModal">
    <section class="modal" :class="{ 'source-modal':modal==='source' }" ref="modalElement" role="dialog" aria-modal="true" :aria-label="modal" tabindex="-1" @keydown="trapModal">
      <button class="modal-close icon-button" @click="closeModal" :disabled="isBusy" :aria-label="t('Close dialog','关闭窗口')"><X :size="20"/></button>
      <template v-if="modal==='create'"><span class="modal-symbol"><Folder :size="23"/></span><h2>{{ t('Make room for your next exam.','创建你的课程工作区') }}</h2><p>{{ t('A dedicated space for your materials, insights, and practice.','在一个空间内管理课程资料、考试重点与练习。') }}</p><form @submit.prevent="createCourse"><label for="course-name">{{ t('Course name','课程名称') }}</label><input id="course-name" v-model="courseName" required maxlength="120" placeholder="e.g. Machine Learning"/><div class="form-row"><div><label for="course-code">{{ t('Course code','课程代码') }}</label><input id="course-code" v-model="courseCode" maxlength="30" placeholder="CS-204"/></div><div><label for="exam-date">{{ t('Exam date','考试日期') }}</label><input id="exam-date" type="date" v-model="examDate"/></div></div><button class="btn primary full" :disabled="isBusy || !courseName.trim()">{{ t('Create course','创建课程') }}<ArrowUpRight :size="15"/></button></form></template>
      <template v-else-if="modal==='upload'"><span class="modal-symbol"><Upload :size="23"/></span><h2>{{ t('Give your course some context.','添加课程资料') }}</h2><p>{{ t('Add your syllabus, slides, or past papers. Each insight links back to its source.','上传大纲、课件或历年卷，每条结论都可追溯到来源。') }}</p><form @submit.prevent="upload"><label for="material-kind">{{ t('Material type','资料类型') }}</label><select id="material-kind" v-model="uploadKind"><option value="lecture">{{ t('Lecture / slides','讲义 / 课件') }}</option><option value="syllabus">{{ t('Syllabus / teaching plan','教学大纲') }}</option><option value="past_paper">{{ t('Past paper','历年试卷') }}</option><option value="assignment">{{ t('Assignment / tutorial','作业 / 教程') }}</option><option value="notes">{{ t('Notes','笔记') }}</option></select><label class="dropzone" @dragover.prevent @drop.prevent="uploadFiles=Array.from($event.dataTransfer?.files || [])"><Upload :size="24"/><b>{{ t('Choose files or drop them here','选择文件或拖放至此') }}</b><small>PDF · DOCX · PPTX · TXT · MD</small><input type="file" multiple accept=".pdf,.docx,.pptx,.txt,.md" @change="selectFiles"/></label><ul class="upload-selection" v-if="uploadFiles.length"><li v-for="file in uploadFiles" :key="file.name">{{ file.name }} <small>{{ (file.size/1024).toFixed(0) }} KB</small></li></ul><button class="btn primary full" :disabled="isBusy || !uploadFiles.length"><LoaderCircle v-if="isBusy" class="spin" :size="16"/>{{ isBusy ? busy : t('Upload materials','上传资料') }}</button></form></template>
      <template v-else-if="modal==='source' && source"><span class="kicker">{{ t('COURSE SOURCE','课程来源') }}</span><h2>{{ source.material.name }}</h2><p>{{ source.material.pages }} {{ t('pages','页') }} · {{ source.material.kind }}<template v-if="source.material.isDemo"> · {{ t('Example content','示例内容') }}</template></p><pre class="source-text">{{ source.text }}</pre></template>
      <template v-else-if="modal==='share'"><span class="modal-symbol"><Share2 :size="23"/></span><h2>{{ t('Better, together.','一起学习，分享所知。') }}</h2><p>{{ t('Create a read-only snapshot of the course map and saved revision packs. Anyone with the link can read it and leave comments.','创建课程地图与已保存复习资料的只读快照，持有链接的人可以阅读并评论。') }}</p><div class="privacy-callout"><LockKeyhole :size="18"/>{{ t('Your conversations, answers, and mastery remain private.','个人对话、答案和掌握度不会分享。') }}</div><button class="btn primary full" v-if="!shareUrl" :disabled="isBusy" @click="createShareLink">{{ t('Create share link','创建分享链接') }}</button><template v-else><label for="share-link">{{ t('Share link','分享链接') }}</label><input id="share-link" :value="shareUrl" readonly @focus="($event.target as HTMLInputElement).select()"/><button class="btn primary full" @click="copyLink">{{ t('Copy link','复制链接') }}</button><a class="preview-link" :href="shareUrl" target="_blank" rel="noopener">{{ t('Preview shared course','预览分享内容') }} ↗</a></template></template>
      <template v-else-if="modal==='settings'"><span class="modal-symbol"><Settings2 :size="23"/></span><h2>个人偏好</h2><p>设置你的显示名称与 AI 工作模式。课程资料会保留在本机，混合模式会优先使用本地模型。</p><div class="auth-actions"><button class="btn" type="button" @click="openModal('auth')">登录 / 切换账号</button><button class="btn" type="button" @click="logout">退出登录</button></div><form @submit.prevent="saveSettings"><label for="display-name">显示名称</label><input id="display-name" v-model="displayName" required maxlength="60"/><div class="settings-model"><Sparkles :size="19"/><div><b>混合模式 · GPT-5 + 本地模型</b><p v-if="data?.mode==='hybrid'">优先使用本地模型处理资料与常规任务；复杂推理可调用 GPT-5。</p><p v-else-if="data?.mode==='local'">当前使用本地模型，课程资料不会离开本机。</p><p v-else-if="data?.mode==='live'">当前使用 GPT-5 在线模式。</p><p v-else>当前为演示模式。配置 Ollama 或 OPENAI_API_KEY 后可分析自己的课程。</p></div></div><button class="btn primary full">保存设置</button></form></template>
      <template v-else-if="modal==='auth'"><span class="modal-symbol"><LockKeyhole :size="23"/></span><h2>登录 Exam Radar</h2><p>登录用于保存你的学习进度，并统计项目体验人数。我们只记录必要的账号标识，不收集无关隐私。</p><button v-if="authConfig.zhihuEnabled" class="btn primary full" type="button" @click="zhihuLogin">使用知乎登录 <ArrowUpRight :size="15"/></button><p v-else class="subtle auth-disabled">知乎登录暂不可用：{{ authConfig.zhihuReason || '尚未配置知乎 OAuth 应用凭据。' }}</p><form v-if="authConfig.reviewerEnabled" @submit.prevent="reviewerLogin"><label for="reviewer-username">评审账号</label><input id="reviewer-username" v-model="reviewerUsername" autocomplete="username" required/><label for="reviewer-password">密码</label><input id="reviewer-password" v-model="reviewerPassword" type="password" autocomplete="current-password" required/><p v-if="authError" class="form-error" role="alert">{{ authError }}</p><button class="btn primary full" :disabled="authBusy">{{ authBusy ? '登录中…' : '评审账号登录' }}</button></form><p v-else class="subtle">评审账号登录暂未启用，请使用匿名演示工作区。</p></template>
    </section>
  </div>
</template>

