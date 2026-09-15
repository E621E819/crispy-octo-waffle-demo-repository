from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
W,H=2048,1152
im=Image.new('RGB',(W,H),'#F6F5F1'); d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/segoeui.ttf'; bold='C:/Windows/Fonts/segoeuib.ttf'
def F(n,b=False): return ImageFont.truetype(bold if b else font,n)
# sidebar
d.rectangle((0,0,310,H), fill='#101827'); d.text((46,42),'EXAM RADAR',font=F(27,1),fill='#FFFFFF'); d.text((46,77),'Course intelligence workspace',font=F(15),fill='#9CA8B8')
d.rounded_rectangle((28,140,282,216),18,fill='#25334A'); d.text((52,157),'⌬  Data Structures',font=F(20,1),fill='#FFFFFF'); d.text((52,188),'Spring 2026  ·  4 collaborators',font=F(14),fill='#AEBACB')
items=[('⌂','Overview'),('◈','Knowledge Map'),('◌','Exam DNA'),('✓','Practice Studio'),('▣','Revision Pack'),('◉','Study room')]
for i,(ic,tx) in enumerate(items):
 y=270+i*62
 if i==1: d.rounded_rectangle((28,y-12,282,y+40),14,fill='#2DD4BF'); col='#07131B'
 else: col='#D7DEE8'
 d.text((52,y),ic,font=F(22,1),fill=col); d.text((91,y+3),tx,font=F(18,1 if i==1 else 0),fill=col)
d.text((46,690),'WORKSPACE',font=F(13,1),fill='#718096')
for i,t in enumerate(['Materials  18','Shared notes  6','Settings']): d.text((52,730+i*42),t,font=F(16),fill='#B8C2D0')
d.rounded_rectangle((28,1018,282,1108),16,fill='#18263A'); d.ellipse((51,1041,91,1081),fill='#F59E8B'); d.text((108,1042),'Mina Chen',font=F(16,1),fill='#FFFFFF'); d.text((108,1066),'Student · Online',font=F(13),fill='#9CA8B8')
# main top
d.text((360,46),'Knowledge Map',font=F(32,1),fill='#101827'); d.text((360,91),'See how course concepts connect to exam evidence.',font=F(17),fill='#687486')
d.rounded_rectangle((1420,38,1662,92),16,fill='#FFFFFF',outline='#E3E4E1',width=2); d.text((1450,55),'⌕  Search workspace',font=F(16),fill='#7A8492'); d.rounded_rectangle((1680,38,1816,92),16,fill='#101827'); d.text((1710,55),'+  Invite',font=F(16,1),fill='#FFFFFF')
# avatars
for x,c in [(1842,'#F59E8B'),(1880,'#8FB8D8'),(1918,'#A8D5BA'),(1956,'#D7A5E5')]: d.ellipse((x,48,x+36,84),fill=c,outline='#F6F5F1',width=3)
# readiness card
d.rounded_rectangle((360,144,720,360),22,fill='#FFFFFF',outline='#E5E5E1',width=2); d.text((392,177),'EXAM READINESS',font=F(14,1),fill='#7C8795'); d.ellipse((405,214,570,379),outline='#E8ECEA',width=18); d.arc((405,214,570,379),-90,190,fill='#2DD4BF',width=18); d.text((439,265),'78%',font=F(42,1),fill='#101827'); d.text((429,316),'on track',font=F(16),fill='#4D8B76'); d.text((595,221),'12 days',font=F(26,1),fill='#101827'); d.text((595,259),'until exam',font=F(15),fill='#7B8794'); d.text((595,303),'↑ 9% this week',font=F(15,1),fill='#2B9D7E')
# radar score panel
d.rounded_rectangle((748,144,1320,360),22,fill='#FFFFFF',outline='#E5E5E1',width=2); d.text((780,177),'NEXT BEST FOCUS',font=F(14,1),fill='#7C8795'); d.text((780,214),'KNN · curse of dimensionality',font=F(23,1),fill='#101827'); d.text((780,255),'Priority score',font=F(15),fill='#7A8492'); d.text((1040,245),'91',font=F(34,1),fill='#F06A58'); d.text((1110,255),'/ 100',font=F(15),fill='#7A8492');
for i,(t,v,c) in enumerate([('Frequency',.82,'#F06A58'),('Marks',.68,'#F4B84A'),('Weakness',.74,'#2DD4BF')]):
 y=300+i*20; d.text((780,y),t,font=F(12),fill='#697586'); d.rounded_rectangle((884,y+3,1125,y+13),5,fill='#EEF0ED'); d.rounded_rectangle((884,y+3,884+int(241*v),y+13),5,fill=c)
d.rounded_rectangle((1348,144,1988,360),22,fill='#101827'); d.text((1380,177),'STUDY ROOM',font=F(14,1),fill='#8FA0B4'); d.text((1380,214),'Practice together',font=F(23,1),fill='#FFFFFF'); d.text((1380,253),'4 people are reviewing this map',font=F(15),fill='#B3BFCE'); d.rounded_rectangle((1380,292,1580,334),13,fill='#2DD4BF'); d.text((1415,304),'Open room  →',font=F(15,1),fill='#06151B')
# map card
d.rounded_rectangle((360,394,1320,1078),22,fill='#FFFFFF',outline='#E5E5E1',width=2); d.text((392,428),'COURSE KNOWLEDGE MAP',font=F(14,1),fill='#7C8795'); d.text((392,459),'Click a node to inspect sources and generate practice.',font=F(16),fill='#687486')
# map background grid
for x in range(410,1290,48): d.line((x,520,x,1030),fill='#F0F1EE',width=1)
for y in range(520,1030,48): d.line((410,y,1290,y),fill='#F0F1EE',width=1)
# connectors
nodes=[((600,665),'Supervised\nLearning','#DDF5EF'),((860,590),'Regression','#E5E8FF'),((1080,690),'KNN','#FFE4DC'),((640,875),'Model\nEvaluation','#FFF0C9'),((900,900),'Precision / Recall','#E2F0F8'),((1120,885),'Clustering','#ECE2F7')]
for a,b in [((600,665),(860,590)),((860,590),(1080,690)),((600,665),(640,875)),((640,875),(900,900)),((900,900),(1120,885))]: d.line((*a,*b),fill='#B8C4CA',width=4)
for (x,y),label,c in nodes:
 d.ellipse((x-76,y-42,x+76,y+42),fill=c,outline='#FFFFFF',width=4); lines=label.split('\n');
 for j,line in enumerate(lines):
  box=d.textbbox((0,0),line,font=F(17,1)); d.text((x-(box[2]-box[0])/2,y-17+j*22),line,font=F(17,1),fill='#172231')
# right insight
d.rounded_rectangle((1348,394,1988,1078),22,fill='#FFFFFF',outline='#E5E5E1',width=2); d.text((1380,428),'EXAM RADAR',font=F(14,1),fill='#7C8795'); d.text((1380,459),'Priority topics',font=F(25,1),fill='#101827'); d.text((1380,498),'Explainable ranking from papers, syllabus, and your answers.',font=F(15),fill='#687486')
rows=[('KNN','91','Critical','#F06A58'),('Logistic Regression','94','Critical','#F06A58'),('Model Evaluation','78','Important','#F4B84A'),('Hierarchical Clustering','61','Review','#2DD4BF')]
for i,(name,score,tag,col) in enumerate(rows):
 y=560+i*103; d.line((1380,y-20,1955,y-20),fill='#ECEDE9',width=2); d.text((1380,y),name,font=F(17,1),fill='#182333'); d.text((1860,y),score,font=F(22,1),fill=col); d.rounded_rectangle((1380,y+37,1510,y+66),10,fill=col); d.text((1400,y+43),tag,font=F(12,1),fill='#FFFFFF'); d.text((1535,y+43),'Why this score  ↗',font=F(13),fill='#6B7684')
# footer quick action
d.rounded_rectangle((1380,970,1955,1034),16,fill='#F0F7F5'); d.text((1410,990),'Generate a 15-question revision pack  →',font=F(16,1),fill='#167A68')
out=Path('output/imagegen/exam-radar-ui-preview.png'); out.parent.mkdir(parents=True,exist_ok=True); im.save(out); print(out.resolve())
