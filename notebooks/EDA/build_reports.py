"""Build the English HTML report after run_eda.py, using the installed report runtime."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"eda/output"
HOME=Path.home()
NODE=HOME/".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
PLUGIN=HOME/".codex/plugins/cache/openai-curated-remote/data-analytics/1.0.11"

SECTIONS={
"en":[("quality","1. Data scope and quality"),("inventory","2. What is in the network?"),("time","3. When were leaks recorded?"),("risk","4. Which groups experienced leaks?"),("cost","5. What drives historical repair dollars?"),("space","6. Where are pipes and recorded replacements?")],

}


def narratives(m,lang):
# Both editions use the same validated metrics.
    if lang=="en":
        return {
        "title":"Star Kingdom: leak costs are concentrated, and 26.2k iron pipes remain",
        "intro":"An exploratory analysis of the gas network, historical leaks, and the starting point for the 2027–2051 replacement project.",
        "summary":f"## Executive Summary\n\n- **Start from the repaired inventory.** The {m['pipe_rows']:,} original pipe records include {m['original_iron']:,} iron pipes. Every pipe recorded in train.csv is treated as polyurethane after its leak; eight unknown-material pipes remain unresolved.\n- **Severity matters alongside leak probability.** The {m['leak_rows']:,} historical leaks cost **${m['historical_cost']/1e6:.1f}M**. The most expensive 1% account for **{m['top1_cost_share']:.1%}** of repair dollars. Median cost is **${m['median_cost']:,.0f}**, far below the **${m['mean_cost']:,.0f}** mean.\n- **Original material is not a causal risk estimate.** Historical leak fractions differ markedly by material, but age, surface, location, and repair-driven removal are intertwined. The age comparison therefore includes a separate original-iron-only view.\n- **Within-material unit costs vary by year.** Annual mean and median repair dollars per pipe metre are shown within each original material, together with an indexed red–blue heatmap. These nominal values are descriptive and can be moved by extreme repairs or changing surface and location mix.",
        "quality_intro":"The supplied files contain one row per pipe and one recorded leak per leaking pipe. All leak IDs join successfully; no duplicate pipe IDs, nonpositive lengths, or leaks preceding known installation dates were found. The brief names the leak file costs.csv; the supplied train.csv is treated as that history. The supplied competition window is used through 2026-12-31, even though it extends beyond the current real-world date. No real-world freshness claim is made.",
        "preview":"### Source preview\n\nThe first five records are shown in source-file order. Full derived data, chart evidence, and validation results are exported beside this report.",
        "methods":"## Methods and interpretation\n\n**Observation window.** 2019-01-01 through 2026-12-31; 2027-01-01 is the project-start reference. The supplied history is assumed complete for that window. All known installation dates precede it. The original state at 2019 is assumed to be the stated original material; unrecorded earlier replacements cannot be reconstructed.\n\n**Inventory update.** Every pipe with a recorded historical leak is set to polyurethane for 2027, following the competition rule. Unknown materials stay unknown. Original-installation age must not be used as the actual age of newly installed polyurethane.\n\n**Geometry.** Each pipe length is the straight-line Euclidean distance between its supplied endpoints; the length distribution is therefore a distribution across individual pipe records, not total network length. Coordinates are local metres without a geographic basemap. Surface regions are nearest-pipe estimates used only for display, not measured land boundaries.\n\n**Fractions versus incidence.** An eight-year leak fraction divides leaking pipes by the source inventory. Original-material incidence divides recorded first leaks by pipe-years until leak/replacement or the end of observation. Missing installation dates are assigned observation entry at 2019-01-01 for exposure only; no age is imputed. Wilson intervals summarize binomial fractions; exact Poisson intervals summarize incidence. Their independence assumptions do not model spatial clustering or competing unrecorded changes.\n\n**Cost analysis.** Costs are nominal competition dollars; no inflation adjustment is assumed. Cost per metre divides each recorded repair cost by that pipe's endpoint-to-endpoint length. Annual mean values are sensitive to extreme repairs, so medians and event counts are shown alongside them. Spearman correlation compares rank order on a -1 to +1 scale; LOWESS summarizes local log-cost tendency. Both are descriptive, not forecasts or causal effects.\n\n**Python libraries.** pandas joins and aggregates; NumPy computes geometry and arrays; Matplotlib exports PNG/SVG; Seaborn draws statistical plots; SciPy computes rank correlation, nearest-neighbour surface estimates, and Poisson interval quantiles; statsmodels supplies Wilson intervals, ECDF, and LOWESS. A fixed seed is unnecessary because this analysis uses no random subsampling.\n\n**Reproducibility.** eda/run_eda.py regenerates the figures, tables, metrics and source hashes. eda/build_reports.py rebuilds the English HTML report from the same evidence. Package versions and validation checks are saved in validation.json. This EDA does not train a forecast, simulate future leaks, or construct a submission.",
        "next":"",
        "nav":"Contents", "download":"Download PNG", "source_label":"Preview of supplied data"}


JSX='''import React from "react";
import { DataComponent, ReportSection, RichNarrative, useDataApp } from "../../data-app-public.jsx";
import content from "./content.json";
import "./report.css";

// Render reviewed evidence without recalculation.
export function ReportContent() {
  const { snapshot, visible, appTitle } = useDataApp();
  const rows=(id)=>snapshot.queries[id]?.rows ?? [];
  const n=content.narrative;
  const assets=Object.fromEntries(rows("figure_assets").map(r=>[r.id,r.image]));
  return <article className="report-content eda-report" lang={content.language}>
    <header className="report-hero"><h1>{appTitle}</h1>
      <RichNarrative id="eda-intro" value={n.intro}/></header>
    <ReportSection id="eda-summary" title="Executive Summary" queryId="key_metrics" sourceRows={rows("key_metrics")} showHeading={false}>
      <RichNarrative id="eda-summary-body" value={n.summary}/>
    </ReportSection>
    <nav className="eda-nav" aria-label={n.nav}>{content.sections.map(([id,label])=><a key={id} href={"#section-"+id}>{label}</a>)}<a href="#methods">{"Methods and interpretation"}</a></nav>
    {content.sections.map(([section,label])=><section id={"section-"+section} key={section} className="eda-section">
      <RichNarrative id={"heading-"+section} value={"## "+label}/>
      {section==="quality" && <><RichNarrative id="quality-intro" value={n.quality_intro}/><RichNarrative id="preview-intro" value={n.preview}/>
        {["source_preview","leak_preview"].map(q=><DataComponent key={q} id={"preview-"+q} queryId={q} kind="table" title={q==="source_preview"?"pipes.csv — head(5)":"train.csv — head(5)"} displayRows={rows(q)} sourceRows={rows(q)}>
          <div className="eda-table-scroll" data-reviewed-rows><table><thead><tr>{Object.keys(rows(q)[0]??{}).map(k=><th key={k}>{k}</th>)}</tr></thead><tbody>{rows(q).map((r,i)=><tr key={i}>{Object.keys(r).map(k=><td key={k}>{r[k]===null?"NA":String(r[k])}</td>)}</tr>)}</tbody></table></div>
        </DataComponent>)}</>}
      {content.charts.filter(c=>c.section===section).map(c=>visible(c.id)&&<div key={c.id} className="eda-figure-block">
        <DataComponent id={c.id} title={c.title} kind="custom" queryId={c.query} displayRows={rows(c.query)} sourceRows={rows(c.query)}>
          <img className="eda-chart-image" src={assets[c.id]} alt={c.title} loading="lazy"/>
          <a className="eda-download" href={assets[c.id]} download={c.id+".png"}>{n.download}</a>
          <RichNarrative id={c.id+"-interpretation"} value={c[content.language]}/>
        </DataComponent>
      </div>)}
    </section>)}
    <section id="methods" className="eda-section"><RichNarrative id="eda-methods" value={n.methods}/>
      {n.next&&<RichNarrative id="eda-next" value={n.next}/>}</section>
  </article>;
}
'''

CSS='''.report-page { --data-app-layout-intent: authored-report; --data-app-content-width: 1080px; }
.eda-report { color: var(--text); max-width: 1128px; margin: 0 auto; padding: 32px 24px 64px; box-sizing: border-box; font-size: 16px; line-height: 1.75; }
.eda-report p, .eda-report li { font-size: 16px; line-height: 1.75; }
.eda-report .report-hero { margin-bottom: 30px; }
.eda-report .report-hero h1 { font-size: clamp(28px, 4vw, 44px); line-height: 1.2; letter-spacing: -0.035em; max-width: 980px; }
.eda-report .eda-nav { display: flex; gap: 10px 20px; flex-wrap: wrap; padding: 22px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 28px 0; }
.eda-report .eda-nav a { color: var(--accent); font-size: 14px; text-decoration: none; }
.eda-report .eda-section { margin-top: 48px; scroll-margin-top: 90px; }
.eda-report .eda-figure-block { margin: 28px 0 50px; }
.eda-report .eda-chart-image { display: block; width: 100%; height: auto; background: white; border-radius: 6px; }
.eda-report .eda-download { display: inline-block; font-size: 13px; margin: 8px 0 16px; color: var(--accent); }
.eda-report .eda-table-scroll { overflow-x: auto; margin: 12px 0 26px; }
.eda-report table { border-collapse: collapse; font-size: 12px; width: 100%; }
.eda-report th { background: var(--muted); font-weight: 600; text-align: left; }
.eda-report td, .eda-report th { border-bottom: 1px solid var(--border); padding: 9px 11px; white-space: nowrap; }
@media(max-width: 600px) { .eda-report { padding: 24px 16px 40px; } .eda-report .eda-section { margin-top: 30px; } .eda-report .eda-nav { gap: 10px; } }
@media print { .eda-report .eda-download, .eda-report .eda-nav { display:none; } .eda-report .eda-figure-block { break-inside:avoid; } }
'''


def main(build=True):
    data=json.loads((OUT/"report_content.json").read_text(encoding="utf-8"))
    # Add concrete findings from reviewed tables.
    pipes=pd.read_csv(OUT/"tables/pipe_features.csv")
    leak_rows=pipes[pipes.leaked]
    road=leak_rows[leak_rows.Surface=="road"]
    material=pd.read_csv(OUT/"tables/material_summary.csv").set_index("original_material")
    for c in data["charts"]:
        if c["id"]=="19_cost_by_surface":
            c["en"]=f"Road-associated pipes account for {len(road):,} recorded leaks ({len(road)/len(leak_rows):.1%} of events) but {road.Cost.sum()/leak_rows.Cost.sum():.1%} of repair dollars. Their median repair cost is ${road.Cost.median():,.0f}. This is conditional severity, not a causal surface effect or the work-unit earthwork tariff. All outliers are retained."
        if c["id"]=="12_material_leak_fraction":
            c["en"]=f"The observed eight-year fraction is {material.loc['brass','observed_leak_share']:.1%} for brass and {material.loc['copper','observed_leak_share']:.1%} for copper, versus roughly 30–34% for the three iron groups. These are original-material, unadjusted fractions—not annual probabilities or causal effects. Wilson 95% intervals do not account for spatial dependence."
    for lang in ["en"]:
        app=ROOT/f"eda/report_{lang}_app"
        if not app.exists():
            subprocess.run([str(NODE),str(PLUGIN/"scripts/prepare-data-app.mjs"),"--surface","report","--output",str(app),"--snapshot",str(OUT/"reviewed_snapshot.json")],check=True)
        # Preserve identity while refreshing evidence.
        prior=json.loads((app/"src/data.json").read_text(encoding="utf-8"))
        snap=json.loads((OUT/"reviewed_snapshot.json").read_text(encoding="utf-8"))
        n=narratives(data["metrics"],lang)
        snap.update({"id":prior["id"],"title":n["title"],"buildStatus":"complete"})
        snap["queries"]["figure_assets"]={"rows":[{"id":c["id"],"image":c["image"]} for c in data["charts"]],"payloadColumns":["image"],"source":{"label":"Python-generated figure assets","files":["eda/run_eda.py"],"metricDefinitions":[{"label":"Figure assets","definition":"PNG images generated from the reviewed tables by eda/run_eda.py; scientific plotting was explicitly requested in Python."}]}}
        (app/"src/data.json").write_text(json.dumps(snap,ensure_ascii=False),encoding="utf-8")
        folder=app/"src/content/report"
        chart_copy=[{k:v for k,v in c.items() if k!="image"} for c in data["charts"]]
        sections=SECTIONS[lang]
        (folder/"content.json").write_text(json.dumps({"charts":chart_copy,"metrics":data["metrics"],"versions":data["versions"],"language":lang,"narrative":n,"sections":sections},ensure_ascii=False),encoding="utf-8")
        (folder/"ReportContent.jsx").write_text(JSX,encoding="utf-8")
        (folder/"report.css").write_text(CSS,encoding="utf-8")
        # Export a Markdown companion (also saves text version).
        md=["# "+n["title"],n["intro"],n["summary"]]
        for section,label in sections:
            md.append("## "+label)
            if section=="quality":md.append(n["quality_intro"])
            for c in chart_copy:
                if c["section"]==section:md.extend(["### "+c["title"],f"![{c['title']}](figures/{c['id']}.png)",c[lang]])
        md.append(n["methods"])
        if n["next"]:md.append(n["next"])
        (OUT/f"eda_report_{lang}.md").write_text("\n\n".join(md),encoding="utf-8")
        if build:
            subprocess.run([str(NODE),str(PLUGIN/"scripts/data-app.mjs"),"build","--project-dir",str(app),"--separate-data"],check=True)
            target=app/f".data-app-offline/exports/eda_report_{lang}.html"
            subprocess.run([str(NODE),str(PLUGIN/"scripts/data-app.mjs"),"export-offline","--project-dir",str(app),"--output",str(target)],check=True)
            shutil.copy2(target,OUT/f"eda_report_{lang}.html")
            print(f"Saved {OUT/f'eda_report_{lang}.html'}",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--no-build",action="store_true")
    main(not parser.parse_args().no_build)
