"""Spatial engineering EDA, all-pipe context vs initially live targets, metres.
Pipe-midpoint grid assignment is descriptive, not parcel or connectivity data.
"""
from common import *
from scipy.spatial import cKDTree

def main():
    pr,units,n,uy,py,active,before,survival,mean=load();N=len(pr.p)
    tree=cKDTree(pr.mid);features=pd.DataFrame({'pipe_id':pr.p['Pipe ID'],'x_m':pr.mid[:,0],'y_m':pr.mid[:,1],
        'material':pr.mat,'surface':pr.surface,'length_m':pr.length,'age_2027':pr.age,'initial_PU':pr.start,
        'live_iron':pr.iron&~pr.start,'planned_year_G04':py,'conditional_repair_cost_CMS001':mean,
        'leak_probability_2y_F168':1-survival[:,1],'leak_probability_25y_F168':1-survival[:,-1]})
    features.loc[pr.start,['leak_probability_2y_F168','leak_probability_25y_F168']]=0
    features['expected_loss_2y']=features.leak_probability_2y_F168*mean
    groups={**{'material_'+str(m):pr.mat==m for m in sorted(set(pr.mat))},
        **{'surface_'+s:pr.surface==s for s in RATES},'all':np.ones(N,bool),'initial_PU':pr.start,'live_iron':pr.iron&~pr.start,'live_noniron':~pr.iron&~pr.start}
    dictionary=[]
    for radius in [25,50,100,250]:
        near=tree.query_ball_point(pr.mid,radius,workers=2)
        counts=np.array([len(a) for a in near]);features[f'neighbors_{radius}m']=counts-1
        for key,mask in groups.items():
            # Exclude anchor from neighborhood counts and length.
            features[f'{key}_count_{radius}m']=np.fromiter((np.count_nonzero(mask[a]) for a in near),int,N)-mask.astype(int)
            features[f'{key}_length_{radius}m']=np.fromiter((np.sum(pr.length[a]*mask[a]) for a in near),float,N)-pr.length*mask
        print('neighborhood features',radius,flush=True)
    regions=[]
    for cell in [25,50,100,250]:
        xy=np.floor(pr.mid/cell).astype(int)
        f=features[['length_m','age_2027','initial_PU','live_iron','expected_loss_2y']].copy()
        f['grid_x']=xy[:,0];f['grid_y']=xy[:,1];f['pipe_count']=1
        for key,mask in groups.items():f[key+'_count']=mask.astype(int)
        f['historical_repairs']=np.isfinite(pr.event).astype(int)
        histcost=pr.p['Pipe ID'].map(pr.hist.set_index('Pipe ID').Cost).fillna(0).to_numpy()
        f['historical_repair_cost']=histcost
        agg={k:'sum' for k in f if k not in ['grid_x','grid_y','age_2027']};agg['age_2027']='mean'
        a=f.groupby(['grid_x','grid_y']).agg(agg).reset_index();a['cell_m']=cell
        a['x_center_m']=(a.grid_x+.5)*cell;a['y_center_m']=(a.grid_y+.5)*cell
        a['surface_types']=(a[[f'surface_{s}_count' for s in RATES]]>0).sum(axis=1)
        regions.append(a)
    regional=pd.concat(regions,ignore_index=True);regional.to_csv(HERE/'regional_features_25_50_100_250m.csv',index=False)
    features.to_csv(HERE/'pipe_neighborhood_features.csv',index=False)
    circles=[];firstrow=np.full(N,n,int);firstrow[pr.start]=-1
    for j,rep in enumerate(active[:n]):firstrow[rep]=j
    for j,u in enumerate(units[:n]):
        rep=active[j];sf=set(pr.surface[u[2]]);mandatory=set(pr.surface[rep]);factor=(np.pi*u[1]**2)**.85
        rate=sum(RATES[s] for s in sf);must=sum(RATES[s] for s in mandatory)
        center=u[0];k=tree.query_ball_point(center,100)
        circles.append(dict(row=j,year=int(uy[j]),x_m=center[0],y_m=center[1],radius_m=u[1],
            active_pipes=len(rep),contained_pipes=len(u[2]),active_length_m=pr.length[rep].sum(),fixed_cost=u[3],
            surface_types=len(sf),surfaces='+'.join(sorted(sf)),mandatory_surface_types=len(mandatory),
            mix_overhead_upper_bound=(rate-must)*factor,construction_cost=u[3]+200*pr.length[rep].sum(),
            neighborhood_count100=len(k),live_iron100=np.sum(pr.iron[k]&~pr.start[k]),
            expected_loss2=mean[rep]@(1-survival[rep,1]),
            expected_work_probability=1-np.prod(1-before[rep,int(uy[j])-2027]),
            assigned_mean_age=pr.age[rep].mean()))
    c=pd.DataFrame(circles);c['stage']=np.select([c.year<=2031,c.year<=2039],['early','middle'],default='late')
    c['density_quartile']=pd.qcut(c.neighborhood_count100,4,labels=False,duplicates='drop')
    c.to_csv(HERE/'G04_circle_features.csv',index=False)
    for key in ['stage','surfaces','surface_types','density_quartile']:
        a=c.groupby(key).agg(circles=('row','size'),pipes=('active_pipes','sum'),fixed_cost=('fixed_cost','sum'),
            construction=('construction_cost','sum'),mix_overhead_upper_bound=('mix_overhead_upper_bound','sum'),median_radius=('radius_m','median'))
        a.to_csv(HERE/f'G04_by_{key}.csv')
    summary=dict(pipes=N,live_iron=int((pr.iron&~pr.start).sum()),initial_PU=int(pr.start.sum()),historical_repairs=len(pr.hist),
        pipe_features=len(features.columns),region_rows=len(regional),active_circles=n,
        mixed_circles=int((c.surface_types>1).sum()),avoidable_mix_upper_bound=float(c.mix_overhead_upper_bound.sum()),
        fixed_cost=float(c.fixed_cost.sum()),replacement_cost=float(200*sum(pr.length[a].sum() for a in active)),
        length_quantiles=np.quantile(pr.length,[0,.25,.5,.75,.95,1]).tolist(),
        neighborhood100_quantiles=np.quantile(features.neighbors_100m,[0,.25,.5,.75,.95,1]).tolist(),
        surface_counts=pr.p.Surface.value_counts().to_dict(),material_counts=pr.p.Material.fillna('unknown').value_counts().to_dict(),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [BASE,ROOT/'data/pipes.csv',ROOT/'data/train.csv']},
        notes=['Surface is pipe-level class, not measured land-area fractions.','Midpoint neighborhoods do not imply physical connectivity.','Mix overhead is an upper bound, not necessarily removable cost.','All historical features end 2026; no official Public annual outcomes used as predictors.'])
    save_json('eda_summary.json',summary);np.savez_compressed(HERE/'G04_state.npz',firstrow=firstrow)
    print(json.dumps(summary,ensure_ascii=True),flush=True)

if __name__=='__main__':main()
