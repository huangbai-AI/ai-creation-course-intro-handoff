from pathlib import Path
import subprocess,json,wave
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/片头第十二版_双30秒480P';T=W/'剪辑中间文件'
segs=json.loads((O/'剪辑时间表.json').read_text());wav=T/'原声_按帧精确对齐.wav'
with wave.open(str(wav),'wb') as out:
 out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
 for i,s in enumerate(segs):
  pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(T/f'{i:02d}.mp4'),'-vn','-f','s16le','-ac','2','-ar','48000','-'])
  n=s['frames']*1600*4
  out.writeframes((pcm+b'\0'*max(0,n-len(pcm)))[:n])
final=O/'AI创作全能课_第十二版_60秒_480P_剪辑预览.mp4';tmp=O/'修正中.mp4'
fc="[1:a]atrim=duration=60[n];[2:a]volume='if(between(t,0,5.7)+between(t,10.7,12.7),0.45,if(between(t,26,34.5),0.5,0.92))':eval=frame[m];[n][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95:level=false:latency=true[a]"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(final),'-i',str(wav),'-i',str(O/'声音/配乐剪辑_追逐变奏.wav'),'-filter_complex',fc,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-t','60','-movflags','+faststart',str(tmp)],check=True);tmp.replace(final)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(final),'-vn','-ac','1','-ar','16000',str(W/'成片检查.wav')],check=True)
print('已修正全部音轨时间，严格60秒')
