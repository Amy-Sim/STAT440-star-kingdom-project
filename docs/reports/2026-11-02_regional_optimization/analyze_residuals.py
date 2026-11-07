"""Describe existing temporal OOF cost errors using static spatial attributes.
2027 PU/age/priority attributes are deliberately not used for historical errors.
"""
from common import *

def main():
    f=pd.read_csv(HERE/'pipe_neighborhood_features.csv')
    e=pd.read_csv(ROOT/'output/2026-11-02_robustness_paper/evidence/cost_predictions_common_2024_2026.csv')
    e=e.merge(f[['pipe_id','surface','material','neighbors_100m','length_m']],on='pipe_id',validate='many_to_one')
    assert len(e)==6766
    e['density_quartile']=pd.qcut(e.neighbors_100m,4,labels=False,duplicates='drop')
    e['length_band']=pd.cut(e.length_m,[0,5,10,20,40,np.inf],right=False).astype(str)
    rows=[]
    for key in ['event_year','surface','material','density_quartile','length_band']:
        for name,g in e.groupby(key):
            err=g.CMS001-g.cost
            rows.append(dict(dimension=key,group=str(name),events=len(g),actual_total=g.cost.sum(),predicted_total=g.CMS001.sum(),
                RMSE=np.sqrt(np.mean(err**2)),MAE=np.abs(err).mean(),total_bias_pct=100*err.sum()/g.cost.sum()))
    pd.DataFrame(rows).to_csv(HERE/'cost_OOF_spatial_diagnostics.csv',index=False)
    regions=pd.read_csv(HERE/'regional_features_25_50_100_250m.csv')
    checks=[]
    for cell,g in regions.groupby('cell_m'):
        assert g.pipe_count.sum()==len(f)
        assert g.live_iron.sum()==f.live_iron.sum()
        assert g.historical_repairs.sum()==14113
        checks.append(dict(cell_m=int(cell),occupied_cells=len(g),pipes=int(g.pipe_count.sum()),live_iron=int(g.live_iron.sum())))
    # Independently verify direct neighborhood distances on deterministic anchors.
    xy=f[['x_m','y_m']].to_numpy();errors=[]
    for i in np.random.default_rng(20261102).choice(len(f),24,replace=False):
        for radius in [25,50,100,250]:
            count=int((np.linalg.norm(xy-xy[i],axis=1)<=radius).sum()-1)
            assert count==f.loc[i,f'neighbors_{radius}m']
    save_json('feature_quality_checks.json',dict(grid_reconciliations=checks,independent_neighborhood_checks=96,
        unique_pipe_ids=bool(f.pipe_id.is_unique),missing_numeric_values=int(f.select_dtypes('number').isna().sum().sum()),
        historical_residuals_used_only_static_features=True))
    dictionary=[]
    for col in f:
        if '_count_' in col or col.startswith('neighbors_'):definition='Count of other pipe midpoints within the specified radius, excluding the focal pipe'
        elif '_length_' in col:definition='Total straight length of other pipes whose midpoints lie within the radius, excluding the focal pipe; not clipped physical length inside the boundary (m)'
        else:definition={'pipe_id':'Pipe ID','x_m':'Midpoint x coordinate (m)','y_m':'Midpoint y coordinate (m)','material':'Recorded material; unknown denotes eight missing-material pipes','surface':'Surface classification attached to a pipe, not an area fraction','length_m':'Straight endpoint-to-endpoint distance (m)','age_2027':'Age based on 2027','initial_PU':'Originally PU or replaced after a leak by the end of 2026','live_iron':'Iron pipes that have not been replaced as of the start of 2027','planned_year_G04':'G04 construction year from a no-future-leak replay; unexecuted units use 2052','conditional_repair_cost_CMS001':'Predicted dollar repair cost conditional on a leak','leak_probability_2y_F168':'Cumulative leak probability for 2027-2028. 0 for replaced at start','leak_probability_25y_F168':'Cumulative leak probability from 2027 to 2051. 0 for replaced at start','expected_loss_2y':'2-year cumulative leak probability x conditional repair cost. Forecast before planned replacement'}[col]
        dictionary.append(dict(column=col,definition=definition,availability='static_geometry' if ('_count_' in col or '_length_' in col or col in ['x_m','y_m','material','surface','length_m'] or col.startswith('neighbors_')) else '2027_planning_only'))
    pd.DataFrame(dictionary).to_csv(HERE/'feature_dictionary.csv',index=False,encoding='utf-8-sig')
    print(pd.DataFrame(rows).query("dimension == 'density_quartile'").to_string(index=False),flush=True)

if __name__=='__main__':main()
