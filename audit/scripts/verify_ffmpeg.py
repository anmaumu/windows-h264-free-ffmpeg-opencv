import re
from pathlib import Path
from common import *

FF = (ROOT/'prefix/ffmpeg/bin/ffmpeg.exe').resolve()
results = {'binary': digest(FF)}
outputs = {}
for opt in ['version','buildconf','decoders','encoders','demuxers','hwaccels']:
    p=run('target_'+opt,[FF,'-'+opt])
    assert p.returncode == 0
    outputs[opt]=(p.stdout+p.stderr).decode(errors='replace')

dec=outputs['decoders']; enc=outputs['encoders']; demux=outputs['demuxers']; conf=outputs['buildconf']
decoder_names=[]
encoder_names=[]
for text,dest in [(dec,decoder_names),(enc,encoder_names)]:
    for line in text.splitlines():
        m=re.match(r'^\s*[VAS\.FSTDXB]{6}\s+(\S+)',line)
        if m: dest.append(m.group(1).lower())
h264_terms=('h264','openh264','qsv','nvenc','cuvid')
h264_dec=[x for x in decoder_names if any(t in x for t in h264_terms)]
h264_enc=[x for x in encoder_names if any(t in x for t in h264_terms)]
vp9_present='vp9' in decoder_names
matroska_present=bool(re.search(r'^\s*D\s+matroska,webm\b',demux,re.M))
conf_h264_enables=[line.strip() for line in conf.splitlines() if '--enable-' in line and any(t in line.lower() for t in h264_terms)]

vp9=run('target_decode_vp9',[FF,'-nostdin','-v','info','-xerror','-i',ROOT/'media/vp9.mkv','-map','0:v:0','-frames:v','100','-progress','pipe:1','-f','null','-'])
h264=run('target_decode_h264',[FF,'-nostdin','-v','info','-xerror','-i',ROOT/'media/h264.mkv','-map','0:v:0','-frames:v','1','-f','null','-'])
vp9_progress=vp9.stdout.decode(errors='replace')
h264_text=(h264.stdout+h264.stderr).decode(errors='replace')
results.update({'vp9_decoder_present':vp9_present,'matroska_demuxer_present':matroska_present,
 'h264_related_decoders':h264_dec,'h264_related_encoders':h264_enc,
 'h264_related_explicit_enables':conf_h264_enables,
 'vp9_decode_exit':vp9.returncode,'vp9_decode_100_frames':vp9.returncode==0 and 'frame=100' in vp9_progress,
 'h264_decode_exit':h264.returncode,'h264_decoder_absence_error':h264.returncode!=0 and ('no decoder found for: h264' in h264_text.lower() or 'decoder (codec h264) not found' in h264_text.lower())})
save('ffmpeg_verification',results)
print(results)
assert all([vp9_present,matroska_present,not h264_dec,not h264_enc,not conf_h264_enables,results['vp9_decode_100_frames'],results['h264_decoder_absence_error']])
