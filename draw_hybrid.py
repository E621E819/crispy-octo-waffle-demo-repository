from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
W,H=2048,1152; im=Image.new('RGB',(W,H),'#F7F7F5'); d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/segoeui.ttf'; bold='C:/Windows/Fonts/segoeuib.ttf'
def F(n,b=False): return ImageFont.truetype(bold if b else font,n)
# left nav
d.rectangle((0,0,300,H),fill='#202123'); d.text((32,30),'Exam Radar',font=F(24,1),fill='#F3F4F6'); d.rounded_rectangle((24,88,276,138),10,fill='#343541'); d.text((45,103),'+  New study session',font=F(16),fill='#F3F4F6')
d.text((32,176),'PROJECTS',font=F(12,1),fill='#9CA3AF')
for i,t in enumerate(['Data Structures','Machine Learning','Algorithms']):
 y=210+i*45; d.rounded_rectangle((24,y-7,276,y+31),8,fill='#2B2C31' if i==0 else '#202123'); d.text((44,y),t,font=F(16),fill='#FFFFFF' if i==0 else '#C5C7CE')
d.text((32,380),'RECENT SESSIONS',font=F(12,1),fill='#9CA3AF')
for i,t in enumerate(['KNN exam focus','Build revision pack','Precision vs Recall']): d.text((42,418+i*40),t,font=F(15),fill='#C5C7CE')
d.line((22,1000,278,1000),fill='#3B3D43',width=1); d.text((42,1025),'Mina Chen',font=F(15,1),fill='#FFFFFF'); d.text((42,1052),'Settings · Help',font=F(13),fill='#9CA3AF')
# main header
d.text((350,32),'Data Structures  /  Study workspace',font=F(15),fill='#6B7280'); d.text((350,75),'Exam Radar',font=F(31,1),fill='#202123'); d.text((350,122),'12 days until exam  ·  4 collaborators online',font=F(15),fill='#6B7280')
d.rounded_rectangle((1660,38,1815,82),12,fill='#FFFFFF',outline='#D7D8D5'); d.text((1695,51),'Share',font=F(15,1),fill='#202123');
for x,c in [(1850,'#F4A091'),(1887,'#8FB8D8'),(1924,'#A8D5BA')]: d.ellipse((x,43,x+34,77),fill=c)
# chat area
d.rounded_rectangle((350,170,1420,1030),18,fill='#FFFFFF',outline='#E2E3E0',width=2)
d.text((390,208),'AI study session',font=F(18,1),fill='#202123'); d.text((390,238),'Course-grounded answers with source citations',font=F(14),fill='#6B7280')
# user msg
d.rounded_rectangle((760,300,1360,390),16,fill='#F1F1EF'); d.text((790,324),'What should I revise first for the exam?',font=F(18),fill='#202123'); d.text((790,357),'Use my course materials and past papers.',font=F(15),fill='#6B7280')
# ai response
d.ellipse((395,430,435,470),fill='#202123'); d.text((460,425),'Exam Radar',font=F(16,1),fill='#202123'); d.text((460,468),'Start with KNN and Logistic Regression.',font=F(21,1),fill='#202123'); d.text((460,505),'They combine high exam frequency with your Recall weakness.',font=F(16),fill='#4B5563')
# insight chips
for i,(t,c) in enumerate([('Priority 91','#FDE3DE'),('Recall mastery 58%','#DFF4EE'),('5-year evidence','#E8E9FD')]):
 x=460+i*190; d.rounded_rectangle((x,548,x+170,584),18,fill=c); d.text((x+14,558),t,font=F(13,1),fill='#374151')
# citations
d.rounded_rectangle((460,620,1300,758),14,fill='#F8F8F6',outline='#E5E6E2'); d.text((485,642),'Evidence from your workspace',font=F(14,1),fill='#374151'); d.text((485,678),'[1] Past Paper 2025, Q3 · [2] Teaching Plan, Week 9 · [3] Answer log',font=F(14),fill='#6B7280'); d.text((485,715),'Open Knowledge Map   ·   Explain this score',font=F(14,1),fill='#2563EB')
# composer
d.rounded_rectangle((390,890,1380,990),18,fill='#FFFFFF',outline='#C9CAC7',width=2); d.text((425,918),'Ask about this course or generate a practice question…',font=F(16),fill='#9CA3AF'); d.text((425,958),'＋ Attach   @ Cite sources',font=F(14),fill='#6B7280'); d.ellipse((1315,918,1365,968),fill='#202123'); d.text((1330,929),'↑',font=F(22,1),fill='#FFFFFF')
# right context rail
d.rounded_rectangle((1450,170,1988,1030),18,fill='#FFFFFF',outline='#E2E3E0',width=2); d.text((1485,207),'Workspace context',font=F(18,1),fill='#202123'); d.text((1485,240),'Claude-like document rail',font=F(14),fill='#6B7280')
d.text((1485,298),'KNOWLEDGE MAP',font=F(12,1),fill='#8A8F98');
for i,(t,s,c) in enumerate([('KNN','91 · Critical','#F06A58'),('Logistic Regression','94 · Critical','#F06A58'),('Model Evaluation','78 · Important','#F4B84A'),('Precision / Recall','42% mastery','#2DD4BF')]):
 y=335+i*92; d.text((1485,y),t,font=F(16,1),fill='#202123'); d.text((1485,y+28),s,font=F(14),fill=c); d.line((1485,y+62,1950,y+62),fill='#ECEDE9',width=1)
d.text((1485,745),'SOURCES',font=F(12,1),fill='#8A8F98');
for i,t in enumerate(['Teaching Plan.pdf','Past Papers 2021–2025','Your answer history']): d.text((1485,785+i*38),t,font=F(15),fill='#4B5563')
d.rounded_rectangle((1485,935,1950,987),12,fill='#202123'); d.text((1610,950),'Practice this weakness',font=F(15,1),fill='#FFFFFF')
out=Path('output/imagegen/exam-radar-gpt-claude-preview.png'); out.parent.mkdir(parents=True,exist_ok=True); im.save(out); print(out.resolve())
