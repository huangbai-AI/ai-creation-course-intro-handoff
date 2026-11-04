from pathlib import Path
import subprocess,json,concurrent.futures,shutil
W=Path(__file__).resolve().parent
O=W.parents[1]/'outputs/片头第十二版_双30秒480P';R=O/'原始素材';T=W/'剪辑中间文件';T.mkdir(exist_ok=True)
files={'A':next(R.glob('十二版_A*.mp4')),'B':next(R.glob('十二版_B*.mp4')),'real':R/'实拍_镜像轻调色_仅前两句.mp4'}
segs=[]
def add(src,a,b,start,end,voice=True,desc='',vf=''):
 n0=round(start*30);n1=round(end*30);segs.append(dict(src=src,a=a,b=b,start=n0/30,end=n1/30,frames=n1-n0,voice=voice,desc=desc,vf=vf))
# Remove the brief duplicated identity at the ancient-world entrance; retain all other native A audio.
add('A',0,16.85,0,17.5,True,'片场争执、巨杯与柠檬追逐')
add('A',18,26,17.5,26,True,'删去双人身份错误的入口，接战斗和舞台')
add('A',26,30,26,30,True,'第一句英文演唱、观众')
# A ends with flight. Skip B's repeated flight, keep the second complete line.
add('B',2,5.92,30,34.4236,True,'保留第二句英文演唱；跳过重复的 flight')
add('B',5.92,6.791667,34.4236,36.316,False,'全景舞台动作')
add('B',6.791667,7.666667,36.316,37.2564,False,'观众反应')
add('B',7.666667,9.666667,37.2564,40.0544,False,'舞台动作')
add('B',9.666667,11.541667,40.0544,41.9352,False,'摄影机转到背后')
add('B',11.6,13.7,41.9352,42.8756,False,'太空背影，进入变奏')
# Only valid rear-facing body and head shots, all from the SAME B generation.
valid=[('雨街',13.833334,14.666667),('竹林',17.208334,18.0),('摄影棚',16.041667,16.583334),('未来通道',16.666667,17.125),('太空',12.0,12.85)]
beats=json.loads((W.parents[1]/'outputs/片头第十版_追逐变奏对拍脚本/快切候选拍点.json').read_text())
for i,row in enumerate(beats):
 name,a,b=valid[i%len(valid)]
 dur=row['end']-row['start'];b=min(b,a+dur)
 add('B',a,b,row['start'],row['end'],False,'同背影卡点：'+name)
add('B',21.375,23.125,51.3045,52.2333,True,'回课堂落座')
add('B',23.125,25.6,52.2333,55.8667,True,'摄影机绕到正面，人物保持坐姿')
add('real',0,4.133333,55.8667,60,True,'已镜像轻调色的实拍前两句话')
assert sum(x['frames'] for x in segs)==1800
(O/'剪辑时间表.json').write_text(json.dumps(segs,ensure_ascii=False,indent=2))
def run(i,s):
 p=T/f'{i:02d}.mp4';d=s['frames']/30;speed=(s['b']-s['a'])/d
 vf=f"setpts=(PTS-STARTPTS)/{speed:.10f},fps=30,scale=854:480:flags=lanczos,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={d:.10f}"
 if s['voice']:
  factors=[];rem=speed
  while rem>2:factors.append(2);rem/=2
  while rem<.5:factors.append(.5);rem/=.5
  factors.append(rem)
  af='asetpts=PTS-STARTPTS,'+','.join('atempo='+str(x) for x in factors)+f',aresample=48000,apad,atrim=duration={d:.10f},afade=t=in:d=0.006,afade=t=out:st={max(0,d-.008):.8f}:d=0.008'
 else:af=f'volume=0,asetpts=PTS-STARTPTS,apad,atrim=duration={d:.10f},aresample=48000'
 cmd=['ffmpeg','-v','error','-y','-ss',str(s['a']),'-t',str(s['b']-s['a']),'-i',str(files[s['src']]),'-vf',vf,'-af',af,'-t',str(d),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-c:a','aac','-b:a','192k','-ac','2','-ar','48000','-video_track_timescale','15360',str(p)]
 subprocess.run(cmd,check=True);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for p in ex.map(lambda z:run(*z),enumerate(segs)):print(p.name,flush=True)
lst=T/'concat.txt';lst.write_text(''.join("file '"+str(T/f'{i:02d}.mp4')+"'\n" for i in range(len(segs))))
base=T/'拼接原声_剪辑处理后.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-t','60',str(base)],check=True)
# Use the selected existing score, protect spoken lines and English singing; no new sound effects.
music=O/'声音/配乐剪辑_追逐变奏.wav'
fc="[0:a]aresample=48000,apad,atrim=duration=60[n];[1:a]volume='if(between(t,0,5.7)+between(t,10.7,12.7),0.45,if(between(t,26,34.5),0.5,0.92))':eval=frame[m];[n][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95:level=false[a]"
final=O/'AI创作全能课_第十二版_60秒_480P_剪辑预览.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(base),'-i',str(music),'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-t','60','-movflags','+faststart',str(final)],check=True)
print('完成',final,flush=True)
