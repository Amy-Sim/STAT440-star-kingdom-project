from pathlib import Path
import time,json,subprocess,sys,shutil

out=Path(__file__).resolve().parent
tags=['G22_Ryota_fixed3','G23_Ryota_dynamic3','G24_Amy_annualBCR','G25_Amy_submitted_order']
while not all((out/(tag+'_report.json')).exists() for tag in tags):time.sleep(2)
(out/'raw').mkdir(exist_ok=True)
jobs=[]
for tag in tags:
    shutil.copyfile(out/(tag+'_report.json'),out/(tag+'_initial_geometry_report.json'))
    source=out/'raw'/(tag+'.csv');shutil.copyfile(out/'submit'/(tag+'.csv'),source)
    jobs.append(subprocess.Popen([sys.executable,str(out/'larger_circles.py'),'--tag',tag,'--source',str(source),'--distance','350','--neighbors','40','--max-circles','16','--max-pipes','48','--adaptive']))
assert all(p.wait()==0 for p in jobs)
for tag in tags:shutil.copyfile(out/'candidates'/(tag+'.csv'),out/'submit'/(tag+'.csv'))
print('All four final geometry plans ready for paired evaluation.',flush=True)
subprocess.run([sys.executable,str(out/'evaluate_both.py')],check=True)
