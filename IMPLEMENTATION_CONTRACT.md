# Exam Radar implementation contract

Build a runnable local MVP from the requirement document and upgrade plan. Vue 3 + TypeScript + Vite frontend, FastAPI + LangGraph backend. Default model exactly `gpt-5`, OpenAI Responses API, server-side key. SQLite local persistence so demo launches without Docker. No fabricated live AI or collaboration; clearly labeled demo mode.

## Shared JSON shapes (camelCase)
Course: {id,name,code,examDate,isDemo,topics:Topic[],materials:Material[],sessions:Session[],readiness:number|null}
Topic: {id,title,chapter,mastery:number|null,priority:number,frequency:number,marks:number,recency:number,teachingPlan:number,diversity:number,summary:string,sourceIds:string[],reasoning:string[]}
All factor values 0..100; priority is weighted total (.25 frequency,.20 marks,.15 recency,.15 teachingPlan,.10 diversity,.15 weakness). mastery percent or null.
Material: {id,name,kind,status:'ready'|'processing'|'failed',pages:number,excerpt:string,error?:string,isDemo?:boolean}
Session: {id,title,messages:Message[]}
Message: {id,role:'user'|'assistant',content:string,sourceIds?:string[],isDemo?:boolean}
Question: {id,topicId,prompt,options?:string[],marks:number,difficulty:string,dna:{concept:string,cognitiveLevel:string,reasoning:string[],transformation:string},checks:{name:string,passed:boolean,detail:string}[],sourceIds:string[],isDemo:boolean}. Do not expose solution/rubric before submission.
Feedback: {score,maxScore,feedback,modelAnswer,masteryBefore,masteryAfter,nextTopicId,sourceIds,isDemo}
Pack: {id,title,content,topicIds:string[],createdAt,isDemo}

## API
POST /api/session {name?:string} => {user:{id,name},mode:'demo'|'live',model:'gpt-5'}; signed httponly session cookie, creates isolated demo data once per browser user.
GET /api/bootstrap => {user,mode,model,courses:Course[]}
POST /api/courses {name,code?,examDate?} => Course
POST /api/courses/{id}/sessions {title?} => Session
POST /api/courses/{id}/chat {sessionId,message,language:'en'|'zh'} => Message (nonstream acceptable; show real pending state)
POST /api/courses/{id}/materials multipart file + kind => Material
POST /api/courses/{id}/analyze => Course (explicit AI action; files uploaded but not analyzed until this call)
GET /api/courses/{id}/materials/{materialId} => {material,text}
DELETE /api/courses/{id}/materials/{materialId} => {ok:true}
POST /api/courses/{id}/questions {topicId,language?} => Question
POST /api/courses/{id}/questions/{questionId}/answers {answer} => Feedback
POST /api/courses/{id}/packs {topicIds:string[],format:'notes'|'formulas'|'flashcards',detail:'quick'|'standard'|'full',language?} => Pack
GET /api/courses/{id}/packs => Pack[]
PUT /api/courses/{id}/packs/{packId} {content} => Pack
GET /api/courses/{id}/packs/{packId}/export?format=docx|pdf|md => file
POST /api/courses/{id}/share => {token,url:string} (read-only snapshot of course title, map, shared packs; exclude private sessions, mastery, answers)
GET /api/shared/{token} => {name,topics (without mastery),packs,comments}
POST /api/shared/{token}/comments {body} => {id,author,body,createdAt}; authenticated local identity, persist comments.
GET /api/health => {status,mode,model}

Return errors as {detail:human readable}; never silently fall back from failed real API to fake output.

## Ownership
Root: frontend shell App.vue, state/API integration, global CSS, package/runtime/start scripts, README, browser tests.
Backend agent: backend/app.py, backend/store.py, backend/seed.py, backend/export.py, backend tests for APIs/security, requirements.txt. Coordinate services API with AI agent. Own only backend except ai.py/services.py.
AI agent: backend/ai.py, backend/services.py, backend/test_ai.py, docs/AI_DESIGN.md. Define `AIService` methods called by backend. Independently communicate exact signature; implement async LangGraph generator/critic, grounded analysis/chat/packs/grading with gpt-5; deterministic demo explicitly marked, missing key + real course => actionable error.
UI agent: frontend/src/components/ArtifactPanel.vue, frontend/src/components/KnowledgeMap.vue, frontend/src/components/artifact.css. Use props/events, no API calls. Root communicates signatures.
