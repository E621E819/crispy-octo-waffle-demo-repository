export interface Material { id: string; name: string; kind: string; status: string; pages: number; excerpt: string; error?: string; isDemo?: boolean }
export interface Topic { id: string; title: string; chapter: string; mastery: number | null; priority: number; frequency: number; marks: number; recency: number; teachingPlan: number; diversity: number; summary: string; sourceIds: string[]; reasoning: string[] }
export interface Message { id: string; role: 'user' | 'assistant'; content: string; sourceIds?: string[]; isDemo?: boolean; route?: string; sourceType?: string; taskIntent?: string }
export interface Session { id: string; title: string; messages: Message[] }
export interface Course { id: string; name: string; code: string; examDate: string; isDemo: boolean; topics: Topic[]; materials: Material[]; sessions: Session[]; readiness: number | null }
export interface Question { id: string; topicId: string; prompt: string; options?: string[]; marks: number; difficulty: string; dna: { concept: string; cognitiveLevel: string; reasoning: string[]; transformation: string }; checks: { name: string; passed: boolean; detail: string }[]; sourceIds: string[]; isDemo: boolean }
export interface Feedback { score: number; maxScore: number; feedback: string; modelAnswer: string; masteryBefore: number | null; masteryAfter: number; nextTopicId: string; sourceIds: string[]; isDemo: boolean }
export interface Pack { id: string; title: string; content: string; topicIds: string[]; createdAt: string; isDemo: boolean }
export interface ExamAnalysisQuestion { id: string; concept: string; task: string; cognitiveLevel: string; marks: number | null; year: number | null; sourceIds: string[]; reasoningSkills: string[] }
export interface ExamAnalysisPattern { task: string; count: number; percentage: number }
export interface ExamAnalysis { questions: ExamAnalysisQuestion[]; patterns: ExamAnalysisPattern[]; sampleSize: number; yearRange: {start:number;end:number} | null; coverageNote: string; isDemo: boolean }
export type Tab = 'radar' | 'map' | 'dna' | 'notes' | 'materials';
