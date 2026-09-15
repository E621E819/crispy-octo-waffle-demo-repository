<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUpRight, LockKeyhole, Network } from 'lucide-vue-next'
import type { Course, Topic } from '../types'

const props = defineProps<{ course: Course; selectedTopicId: string; language: 'en' | 'zh' }>()
const emit = defineEmits<{
  (event: 'select-topic', id: string): void
  (event: 'practice', id: string): void
}>()
const zh = computed(() => props.language === 'zh')
const selected = computed(() => props.course.topics.find(topic => topic.id === props.selectedTopicId))
const groups = computed(() => {
  const chapters = [...new Set(props.course.topics.map(topic => topic.chapter))]
  let rowTop = 114
  return chapters.map((chapter, index) => {
    if (index > 0 && index % 2 === 0) {
      const previous = chapters.slice(index - 2, index)
      rowTop += Math.max(...previous.map(name => props.course.topics.filter(topic => topic.chapter === name).length)) * 77 + 101
    }
    return {
      chapter,
      x: index % 2 === 0 ? 112 : 328,
      y: rowTop,
      topics: props.course.topics.filter(topic => topic.chapter === chapter),
    }
  })
})
const mapHeight = computed(() => Math.max(255, ...groups.value.map(group => group.y + group.topics.length * 77 + 49)))

function wrapTitle(value: string, maxLength = 23): string[] {
  if (value.length <= maxLength) return [value]
  let split = value.lastIndexOf(' ', maxLength)
  if (split < maxLength / 2) split = maxLength
  return [value.slice(0, split).trim(), value.slice(split).trim().slice(0, maxLength - 1) + (value.slice(split).trim().length >= maxLength ? '…' : '')]
}
function nodeState(topic: Topic) {
  if (topic.priority >= 80) return 'map-urgent'
  if (topic.mastery !== null && topic.mastery >= 75) return 'map-strong'
  return 'map-neutral'
}
</script>

<template>
  <div class="map-workspace">
    <div class="map-heading">
      <span class="artifact-eyebrow">{{ zh ? '一眼看懂你的课程' : 'YOUR COURSE, CONNECTED' }}</span>
      <h3>{{ zh ? '知识地图' : 'Knowledge map' }}</h3>
      <p>{{ zh ? '从章节到知识点，找到值得优先学习的部分。' : 'From chapters to concepts. Find your next focus.' }}</p>
    </div>

    <div v-if="!course.topics.length" class="map-empty">
      <Network :size="28" :stroke-width="1.3" />
      <h4>{{ zh ? '知识地图尚待建立' : 'Your map starts here' }}</h4>
      <p>{{ zh ? '在资料页上传课程文件并运行分析，知识点会自动归入所属章节。' : 'Upload course materials and run analysis to organize concepts into chapters.' }}</p>
    </div>
    <template v-else>
      <div class="map-legend" :aria-label="zh ? '图例' : 'Map legend'">
        <span><i class="map-dot map-urgent"></i>{{ zh ? '优先学习' : 'High priority' }}</span>
        <span><i class="map-dot map-strong"></i>{{ zh ? '已掌握' : 'Strong' }}</span>
        <span><i class="map-dot map-neutral"></i>{{ zh ? '其他概念' : 'Other concepts' }}</span>
      </div>
      <div class="map-canvas">
        <svg class="map-graph" :viewBox="`0 0 440 ${mapHeight}`" role="group" :aria-label="zh ? '按章节分组的知识点。使用 Tab 选择节点。' : 'Concepts grouped by chapter. Use Tab to select nodes.'">
          <g class="map-connectors" aria-hidden="true">
            <path v-for="group in groups" :key="group.chapter" :d="`M 220 64 L 220 ${group.y - 28} Q 220 ${group.y - 14} ${group.x} ${group.y - 14} L ${group.x} ${group.y}`" />
          </g>
          <g class="map-root" transform="translate(220, 42)">
            <rect x="-125" y="-24" width="250" height="48" rx="11" />
            <text y="-3" class="map-root-eyebrow">{{ course.code || (zh ? '课程' : 'COURSE') }}</text>
            <text y="13" class="map-root-title">{{ course.name.length > 31 ? course.name.slice(0, 30) + '…' : course.name }}</text>
          </g>
          <g v-for="group in groups" :key="group.chapter">
            <g class="map-chapter" :transform="`translate(${group.x},${group.y})`">
              <rect x="-91" y="-12" width="182" height="38" rx="9" />
              <text y="10">{{ group.chapter.length > 25 ? group.chapter.slice(0, 24) + '…' : group.chapter }}</text>
              <title>{{ group.chapter }}</title>
            </g>
            <g v-for="(topic, index) in group.topics" :key="topic.id">
              <path class="map-branch" :d="`M ${group.x - 84} ${group.y + 26} L ${group.x - 84} ${group.y + 60 + index * 77} Q ${group.x - 84} ${group.y + 69 + index * 77} ${group.x - 75} ${group.y + 69 + index * 77} L ${group.x - 66} ${group.y + 69 + index * 77}`" aria-hidden="true" />
              <g
                class="map-node"
                :class="[nodeState(topic), { 'map-selected-node': selectedTopicId === topic.id }]"
                :transform="`translate(${group.x + 9},${group.y + 69 + index * 77})`"
                role="button"
                tabindex="0"
                :aria-label="`${topic.title}. ${zh ? '优先级' : 'Priority'} ${Math.round(topic.priority)}`"
                :aria-pressed="selectedTopicId === topic.id"
                @click="emit('select-topic', topic.id)"
                @keydown.enter="emit('select-topic', topic.id)"
                @keydown.space.prevent="emit('select-topic', topic.id)"
              >
                <rect x="-76" y="-27" width="159" height="55" rx="9" />
                <circle class="map-node-dot" cx="-62" cy="-12" r="3" />
                <text class="map-node-priority" x="70" y="-9">{{ Math.round(topic.priority) }}</text>
                <text class="map-node-title" x="-62" :y="wrapTitle(topic.title).length > 1 ? 5 : 10">
                  <tspan v-for="(line, lineIndex) in wrapTitle(topic.title)" :key="lineIndex" x="-62" :dy="lineIndex === 0 ? 0 : 13">{{ line }}</tspan>
                </text>
                <title>{{ topic.title }}</title>
              </g>
            </g>
          </g>
        </svg>
      </div>

      <div v-if="selected" class="map-topic-detail">
        <div class="map-topic-detail-top">
          <span class="artifact-eyebrow">{{ zh ? '已选择的概念' : 'SELECTED CONCEPT' }}</span>
          <span class="map-priority-label">{{ Math.round(selected.priority) }} {{ zh ? '优先级' : 'priority' }}</span>
        </div>
        <h4>{{ selected.title }}</h4>
        <p>{{ selected.summary }}</p>
        <button class="map-practice-button" @click="emit('practice', selected.id)">{{ zh ? '练习这个知识点' : 'Practice this concept' }}<ArrowUpRight :size="15" /></button>
      </div>
      <p class="map-footnote"><LockKeyhole :size="12" />{{ zh ? '掌握度仅你可见 · 连线表示章节归属' : 'Mastery is private · connections show chapter membership' }}</p>
    </template>
  </div>
</template>
