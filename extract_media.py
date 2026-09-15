import zipfile,os
from PIL import Image,ImageDraw
p=r'C:\Users\34618\Documents\xwechat_files\wxid_wrwgkmyr8c6m12_cf06\msg\file\2026-09\Exam Radar_lastest.docx'
z=zipfile.ZipFile(p); names=[n for n in z.namelist() if n.startswith('word/media/') and not n.endswith('/')]
out=os.path.abspath('doc_media'); os.makedirs(out,exist_ok=True)
ims=[]
for idx,n in enumerate(names):
 fn=os.path.join(out,f'{idx+1}.png'); open(fn,'wb').write(z.read(n))
 try:
  im=Image.open(fn).convert('RGB'); im.thumbnail((320,220)); c=Image.new('RGB',(340,260),'white'); c.paste(im,((340-im.width)//2,10)); ImageDraw.Draw(c).text((10,235),os.path.basename(n),fill='black'); ims.append(c)
 except Exception as e: print('skip',n,e)
cols=3; rows=(len(ims)+cols-1)//cols; sheet=Image.new('RGB',(cols*340,rows*260),(230,230,230))
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*340,(i//cols)*260))
sheet.save('doc_media_contact.jpg'); print('extracted',len(names),'contact',os.path.abspath('doc_media_contact.jpg'))
