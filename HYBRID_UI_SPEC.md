# Exam Radar — ChatGPT × Claude hybrid UI spec

## Layout
- Desktop 16:10, 1440×900. Three panes: 248px sidebar, fluid conversation (min 560px), 430px artifact inspector.
- Sidebar: workspace/course switcher, New study thread button, grouped recents (Today/This week), persistent modules (Radar, Map, DNA, Practice, Packs, Study Room), profile/settings.
- Conversation: compact top bar with breadcrumb, model/depth selector, share/export. Messages support streaming markdown, citations, tool chips and inline actions. Composer supports attachments, @course context, /commands, voice toggle.
- Artifact inspector: tabs Map / DNA / Notes; each artifact has title, source citations, “Open in thread”, edit, version history and export.

## Core states
1. Welcome: assistant greeting + 3 suggested prompts (“Find my top priorities”, “Explain KNN”, “Start a 5-question drill”).
2. Analysis: assistant streams answer while a slim progress rail shows parse → map → score. Artifact updates in real time.
3. Practice: question card in conversation; right panel shows DNA, difficulty checks, source references. Submit opens rubric feedback and mastery delta.
4. Collaboration: shared thread indicator, avatars and comments; private mastery data visibly marked.

## Visual tokens
- Canvas #FAF9F6; surfaces #FFFFFF/#F7F7F5; text #242424; muted #6B6B68; border #E7E5E0.
- Primary indigo #5B5CE2; AI accent Claude-like tangerine #D97757; success mint #4FAF8F; critical coral #E76F51; important amber #D8A23A.
- Radius 14–16px; border 1px; shadow 0 4px 18px rgba(30,30,30,.06); spacing 8px rhythm.
- Typography Inter (UI) + Noto Sans SC (Chinese), 14–16px body, 12px metadata, 28px page title; optional serif accent for artifact headings.

## Copy style
Calm, concise, transparent: “Priority 94 · based on 12 past questions”; “Why this score”; “Sources · Week 4 slides, p.18”; “Mastery +8%”. Avoid exam guarantees.
