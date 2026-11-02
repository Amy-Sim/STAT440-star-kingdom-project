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
        if '_count_' in col or col.startswith('neighbors_'):definition='管の中点が指定半径内にある他管の本数（自身を除く）'
        elif '_length_' in col:definition='管の中点が指定半径内にある他管の直線長合計m（自身を除く。境界内の実延長ではない）'
        else:definition={'pipe_id':'管ID','x_m':'中点x座標m','y_m':'中点y座標m','material':'記録された材質。unknownは欠損8本','surface':'管に紐づく地表分類。区画面積比ではない','length_m':'両端座標の直線距離m','age_2027':'2027年基準の年齢','initial_PU':'元からPUまたは2026年までに漏水交換済み','live_iron':'2027年開始時点で未交換の鉄管','planned_year_G04':'将来漏水なしで再生したG04の施工年。未施工は2052','conditional_repair_cost_CMS001':'漏水した場合の修理費予測ドル','leak_probability_2y_F168':'2027〜2028年累積漏水確率。開始時交換済みは0','leak_probability_25y_F168':'2027〜2051年累積漏水確率。開始時交換済みは0','expected_loss_2y':'2年累積漏水確率×条件付き修理費。未施工の場合の予測値'}[col]
        dictionary.append(dict(column=col,definition=definition,availability='static_geometry' if ('_count_' in col or '_length_' in col or col in ['x_m','y_m','material','surface','length_m'] or col.startswith('neighbors_')) else '2027_planning_only'))
    pd.DataFrame(dictionary).to_csv(HERE/'feature_dictionary_ja.csv',index=False,encoding='utf-8-sig')
    print(pd.DataFrame(rows).query("dimension == 'density_quartile'").to_string(index=False),flush=True)

if __name__=='__main__':main()
