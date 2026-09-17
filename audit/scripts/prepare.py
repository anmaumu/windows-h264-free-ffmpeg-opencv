import os, platform, sys, shutil, json
from pathlib import Path
from common import *
GEN = Path(r'C:\Program Files\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe')
PROBE = GEN.with_name('ffprobe.exe')
save('environment', {'platform': platform.platform(), 'machine': platform.machine(), 'python': sys.version, 'python_executable': sys.executable, 'PATH': os.environ['PATH'], 'tools': {x:shutil.which(x) for x in ['python','py','uv','ffmpeg','ffprobe','gcc','cmake','ninja','cl','mingw32-make','git']}, 'generator':digest(GEN), 'ffprobe':digest(PROBE)})
for opt in ['version','buildconf','decoders','encoders','demuxers']:
    run('generator_'+opt, [GEN, '-'+opt])
run('gcc_version', ['gcc','--version'])
run('cmake_version', ['cmake','--version'])
run('existing_opencv', [sys.executable, '-c', 'import cv2;print(cv2.__file__);print(cv2.__version__);print(cv2.getBuildInformation())'])
source='testsrc2=size=320x240:rate=30:duration=4'
results=[]
for codec, encoder, extra in [('vp9','libvpx-vp9',['-lossless','1']),('h264','libx264',['-crf','18','-preset','fast'])]:
    path=ROOT/'media'/f'{codec}.mkv'
    p=run('generate_'+codec,[GEN,'-y','-f','lavfi','-i',source,'-frames:v','120','-an','-c:v',encoder,*extra,'-pix_fmt','yuv420p',path])
    assert p.returncode==0
    p=run('probe_'+codec,[PROBE,'-v','error','-count_frames','-show_streams','-show_format','-of','json',path])
    assert p.returncode==0
    info=json.loads(p.stdout); stream=info['streams'][0]
    assert stream['codec_name']==codec and int(stream['nb_read_frames'])==120
    p=run('reference_decode_'+codec,[GEN,'-v','error','-xerror','-i',path,'-map','0:v:0','-frames:v','120','-progress','pipe:1','-f','null','-'])
    assert p.returncode==0 and b'frame=120' in p.stdout
    results.append({**digest(path),'codec':codec,'frames':120,'width':stream['width'],'height':stream['height'],'source':source,'reference_decode_exit':p.returncode})
save('media',results)
