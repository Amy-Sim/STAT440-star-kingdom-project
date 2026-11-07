# Repair cost model candidates for 2027

[English report](report_en.md)

Six CSVs are in `predictions/`: five model candidates plus one reference. Each contains all 28,926 inventory IDs absent from train.csv, with exactly `id,predicted_cost`, sorted by decreasing cost. See the reports before using the 1,686 extrapolated rows.

[Export validation](evidence/export_validation.json) · [Model composition](evidence/candidate_weights.csv) · [Final settings](evidence/final_model_settings.csv) · [Sources](evidence/sources.html)

Training-code snapshots are provided for inspection. They retain their original workspace paths and are not a standalone execution package; the CSV exporter was run in the original reviewed workspace. Fitted model binaries and large intermediate feature tables are not included.

[Repair-all 2027 scenario totals](evidence/repair_all_2027_totals.csv) · [Inputs and outputs](evidence/model_input_contract.json) · [Per-pipe missing-value flags](evidence/input_quality_by_pipe.csv) · [Input-quality audit](evidence/input_quality_audit.json)

To regenerate the report additions and scenario sums from the committed CSVs, run `python notebooks/ensemble_for_cost_prediction/training_code/update_reports.py` from the repository root (pandas, numpy and tabulate required). This updates documentation and audit tables only; it does not retrain or change predictions.
