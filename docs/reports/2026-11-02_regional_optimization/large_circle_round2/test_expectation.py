"""Independent exhaustive check of early-merger expectation accounting."""
from fast_geometry import *
from itertools import product
from scipy.optimize import minimize

def main():
    # Leak events occur after work, matching the annual competition rules.
    surv=np.array([[.8,.6,.4],[.7,.5,.3],[.9,.8,.7]])
    before=np.column_stack([np.ones(3),surv])
    means=np.array([1000.,3000.,2000.]);linear=np.array([200.,400.,500.])
    old=[([0,1],1,1200.),([2],2,900.)];new=[([0,1,2],1,1700.)]
    probs=np.column_stack([1-surv[:,0],surv[:,:-1]-surv[:,1:],surv[:,-1]])
    expected=0.
    for first in product(range(4),repeat=3):
        weight=np.prod([probs[i,t] for i,t in enumerate(first)])
        def cost(plan):
            total=0.
            for ids,year,fixed in plan:
                live=[i for i in ids if first[i]>=year]
                if live:total+=fixed+linear[live].sum()
                total+=sum(means[i] for i in ids if first[i]<year)
            return total
        expected+=weight*(cost(old)-cost(new))
    oldfixed=sum((1-np.prod(1-before[ids,y]))*f for ids,y,f in old)
    p=before[:,1];oldp=np.array([before[0,1],before[1,1],before[2,2]])
    closed=oldfixed-(1-np.prod(1-p))*1700+(p-oldp)@(means-linear)
    assert abs(expected-closed)<1e-8,(expected,closed)
    # Compare large-set geometry to a separately formulated convex disk fit.
    rng=np.random.default_rng(2026110208)
    for n in [32,64,96,128]:
        pts=rng.normal(size=(n,2));c,r=enclosing(pts)
        v=np.r_[pts.mean(axis=0),np.max(np.sum((pts-pts.mean(axis=0))**2,axis=1))]
        result=minimize(lambda x:x[2],v,method='SLSQP',constraints=[{'type':'ineq','fun':lambda x:x[2]-np.sum((pts-x[:2])**2,axis=1)}],options={'ftol':1e-11,'maxiter':300})
        assert result.success,result.message
        assert abs(r-(np.sqrt(result.x[2])+1e-6))<1e-5,(n,r,result.x)
    print('Exhaustive 64-case expected-cost accounting and 4 convex geometry crosschecks passed')

if __name__=='__main__':main()
