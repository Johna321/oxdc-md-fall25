
import os, re, json, sys
import numpy as np
import parmed as pmd

def parse_density(mdout):
    dens=[]
    pat=re.compile(r'\b[Dd]ensity[^=]*=\s*([0-9.]+)')
    with open(mdout,"r",errors="ignore") as f:
        for line in f:
            m=pat.search(line)
            if m:
                dens.append(float(m.group(1)))
    return dens

def last_window_stats(vals, n=20):
    if not vals: return None
    tail = vals[-n:] if len(vals)>=n else vals
    mu = float(np.mean(tail)); sd=float(np.std(tail))
    return dict(mean=mu, sd=sd, n=len(tail))

def any_stars(mdout):
    with open(mdout,"r",errors="ignore") as f:
        for line in f:
            if '***' in line: return True
    return False

def ca_coords(prmtop, rst7):
    s=pmd.load_file(prmtop, rst7)
    sel=[i for i,a in enumerate(s.atoms) if str(getattr(a,'name','')).upper()=="CA"]
    xyz=np.array(s.coordinates)[sel]
    return xyz

def kabsch_rmsd(P,Q):
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    C = Pc.T @ Qc
    V,S,Wt = np.linalg.svd(C)
    if np.linalg.det(V @ Wt) < 0: V[:,-1] *= -1
    U = V @ Wt
    Pp = Pc @ U
    diff = Pp - Qc
    return float(np.sqrt((diff**2).sum()/len(P)))

def main():
    prmtop="./5vg3_solv.prmtop"
    outs=[f for f in os.listdir(".") if f.endswith(".out")]
    dens_reports={}
    star_flags={}
    for md in sorted(outs):
        dens=parse_density(md)
        dens_reports[md]=last_window_stats(dens, n=20)
        star_flags[md]=any_stars(md)
    rmsd={}
    try:
        ref = ca_coords(prmtop,"heat.rst7")
        for tag in ["eq1d","eq2b"]:
            if os.path.exists(f"{tag}.rst7"):
                rmsd[tag]=kabsch_rmsd(ref, ca_coords(prmtop,f"{tag}.rst7"))
    except Exception as e:
        rmsd["error"]=str(e)
    summary=dict(density=dens_reports, stars=star_flags, rmsd=rmsd)
    with open("analysis/qc_summary.json","w") as f: json.dump(summary,f,indent=2)
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
