"""Recompute absolute pooled and annual errors from the saved past-only forecasts."""
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
d=pd.read_csv(HERE/'evidence/cost_predictions_common_2024_2026.csv')
assert len(d)==6766 and d.event_id.is_unique
rows=[]
for model in ['CMS001','team_stable','material_surface_mean']:
    for period,q in [('pooled_2024_2026',d),*[(str(y),d[d.event_year==y]) for y in [2024,2025,2026]]]:
        e=q[model].to_numpy()-q.cost.to_numpy()
        rows.append(dict(model=model,period=period,n=len(q),RMSE=float(np.sqrt(np.mean(e*e))),MAE=float(np.mean(abs(e)))))
result=pd.DataFrame(rows)
expected=pd.read_csv(HERE/'evidence/cost_prediction_errors_by_year.csv')
pd.testing.assert_frame_equal(result,expected,check_exact=False,rtol=1e-12,atol=1e-8)
print(result.to_string(index=False))
summary=pd.read_csv(HERE/'evidence/absolute_metrics_summary.csv')
for model in summary.cost_model.unique():
    q=summary[summary.cost_model==model]
    errors=d[model]-d.cost
    worst=result[(result.model==model)&(result.period!='pooled_2024_2026')].RMSE.max()
    bias=100*errors.sum()/d.cost.sum()
    k=int(np.ceil(.1*len(d)));ix=np.lexsort((d.event_id.astype(str).to_numpy(),-d[model].to_numpy()))[:k]
    capture=100*d.cost.iloc[ix].sum()/d.cost.sum()
    np.testing.assert_allclose(q.worst_year_RMSE,worst,rtol=0,atol=1e-7)
    np.testing.assert_allclose(q.total_bias_pct,bias,rtol=0,atol=1e-9)
    np.testing.assert_allclose(q.top10_cost_capture_pct,capture,rtol=0,atol=1e-9)
print('All three additional absolute diagnostics verified')
