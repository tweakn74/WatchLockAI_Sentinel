# Purpose: Run legacy + new tests and summarize compatibility/regressions.
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def run(cmd:list[str])->tuple[int,str]:
    p=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    o,_=p.communicate()
    return p.returncode,o
def main()->int:
    suites = [
        ["python","-m","pytest","-q","tests/unit"],
        ["python","-m","pytest","-q","tests/e2e"]
    ]
    results=[]
    for s in suites:
        code,out=run(s)
        results.append({"cmd":" ".join(s),"ok":code==0,"code":code,"out":out})
    report={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"results":results}
    Path("DOCS").mkdir(exist_ok=True, parents=True)
    Path("DOCS/Compatibility_Report.json").write_text(json.dumps(report,indent=2),"utf-8")
    print(json.dumps(report,indent=2))
    return 0 if all(r["ok"] for r in results) else 1
if __name__=="__main__":
    raise SystemExit(main())