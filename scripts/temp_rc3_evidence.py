import json,os,glob,hashlib
files = sorted(glob.glob("detection/*.py")+["DOCS/mitre/rules/rc3_baseline.yaml"])
h={f:hashlib.sha256(open(f,'rb').read()).hexdigest() for f in files if os.path.exists(f)}
os.makedirs("DOCS/report",exist_ok=True)
out="DOCS/report/rc3_hashes.json"
open(out,"w").write(json.dumps(h,indent=2))
print("rc3_hashes.json SHA256:", hashlib.sha256(open(out,"rb").read()).hexdigest())