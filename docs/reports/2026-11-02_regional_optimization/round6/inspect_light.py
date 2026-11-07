from pathlib import Path
import json,joblib,numpy as np,sklearn
out=Path(__file__).resolve().parent
info={}
for name in ['radius','action']:
    st=joblib.load(out/(name+'_stack.joblib'));nn=st['base'][3].estimator_[-1]
    info[name]=dict(base_models=['ExtraTrees','HistGradientBoosting','Ridge','MLP32_16','Nystroem64_Ridge'],
        NN_train_row_cap=10000,NN_max_iterations=100,NN_actual_iterations=nn.n_iter_,NN_parameters=sum(a.size for a in nn.coefs_)+sum(a.size for a in nn.intercepts_),
        kernel_components=64,meta_coefficients_on_standardized_base_predictions=st['meta'][-1].coef_.tolist(),
        coefficient_note='Coefficients may be negative; they are not probability weights.',sklearn_version=sklearn.__version__)
(out/'light_model_details.json').write_text(json.dumps(info,indent=2),encoding='utf8')
print(json.dumps(info,indent=2))
