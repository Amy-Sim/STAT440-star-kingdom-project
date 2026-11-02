"""Deterministic randomized incremental smallest enclosing circle.
Two boundary points are held fixed while choosing the extreme circumcircle
on each side of their chord. This avoids combinatorial triplet enumeration.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *

def inside(circle,p):
    return circle is not None and np.linalg.norm(p-circle[0])<=circle[1]+1e-8

def diameter(p,q):return ((p+q)/2,float(np.linalg.norm(p-q)/2))

def circum(p,q,r):
    a=q-p;b=r-p;det=2*(a[0]*b[1]-a[1]*b[0])
    if abs(det)<1e-12:return None
    aa=a@a;bb=b@b
    c=p+np.array([b[1]*aa-a[1]*bb,a[0]*bb-b[0]*aa])/det
    return c,float(np.linalg.norm(c-p))

def cross(a,b):return a[0]*b[1]-a[1]*b[0]

def two(points,p,q):
    d=diameter(p,q);left=right=None;v=q-p
    for r in points:
        if inside(d,r):continue
        side=cross(v,r-p);c=circum(p,q,r)
        if c is None:continue
        z=cross(v,c[0]-p)
        if side>0 and (left is None or z>cross(v,left[0]-p)):left=c
        elif side<0 and (right is None or z<cross(v,right[0]-p)):right=c
    if left is None:return right if right is not None else d
    if right is None:return left
    return left if left[1]<=right[1] else right

def enclosing(points):
    pts=np.unique(np.asarray(points,float),axis=0)
    np.random.default_rng(440).shuffle(pts)
    c=None
    for i,p in enumerate(pts):
        if inside(c,p):continue
        c=(p.copy(),0.)
        for j,q in enumerate(pts[:i]):
            if inside(c,q):continue
            c=diameter(p,q) if c[1]==0 else two(pts[:j+1],p,q)
    assert c is not None
    # Conservative expansion removes floating point containment ambiguity.
    return c[0],float(np.max(np.linalg.norm(pts-c[0],axis=1)))+1e-6

class FastProblem(Problem):
    def unit(self,ids):
        ids=np.asarray(ids,int);c,r=enclosing(np.vstack([self.a[ids],self.b[ids]]))
        c=np.round(c,9);r=float(f'{r:.9f}');near=self.grid.query(c,r)
        mask=(np.linalg.norm(self.a[near]-c,axis=1)<=r)&(np.linalg.norm(self.b[near]-c,axis=1)<=r)
        ids_inside=near[mask];assert np.isin(ids,ids_inside).all()
        fixed=100+sum(RATES[s] for s in set(self.surface[ids_inside]))*(np.pi*r*r)**.85
        return c,r,ids_inside,float(fixed)

def verify():
    from optimize import enclosing as old_enclosing
    rng=np.random.default_rng(2026110207)
    for n in [2,3,4,8,16,32,64]:
        for _ in range(16):
            pts=rng.normal(size=(n,2))*rng.uniform(.1,100)+rng.uniform(0,7000,size=2)
            c,r=enclosing(pts)
            assert (np.linalg.norm(pts-c,axis=1)<=r).all()
            if n<=16:
                oldc,oldr=old_enclosing(pts)
                assert abs(r-oldr)<1e-5,(n,r,oldr)
    for pts in [np.array([[0,0],[1,0],[2,0]]),np.array([[0,0],[0,0]]),np.array([[0,0],[1,0],[.5,.01]])]:
        c,r=enclosing(pts);assert (np.linalg.norm(pts-c,axis=1)<=r).all()
    print('Fast enclosure: 112 random fixtures and 3 degenerate fixtures passed')

if __name__=='__main__':verify()
