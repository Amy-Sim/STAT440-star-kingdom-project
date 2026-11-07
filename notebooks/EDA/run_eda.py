r"""Reproducible Star Kingdom exploratory data analysis.

Run: .venv-eda\Scripts\python.exe eda/run_eda.py
Outputs: eda/output/{figures,tables}, reviewed_snapshot.json, report_content.json
All charts and explanations use English.
"""
from pathlib import Path
import base64
import hashlib
import importlib.metadata
import json
import math
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, LogNorm
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.spatial import cKDTree
from statsmodels.stats.proportion import proportion_confint
from statsmodels.distributions.empirical_distribution import ECDF
from statsmodels.nonparametric.smoothers_lowess import lowess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eda/output"
FIG = OUT / "figures"
TAB = OUT / "tables"
START, END = pd.Timestamp("2019-01-01"), pd.Timestamp("2027-01-01")
IRON = ["cast iron", "gray iron", "wrought iron"]
MC = {"brass":"#BC8C22", "cast iron":"#2879AE", "copper":"#CC6838",
      "gray iron":"#9261B1", "polyurethane":"#249781", "wrought iron":"#536779", "Unknown":"#B9BEC3"}
SC = {"farmland":"#BD902B", "grassland":"#599653", "road":"#596675",
      "structure":"#B16F56", "swamp":"#9876B1", "water":"#388CC1"}
RATE = {"grassland":3, "farmland":7, "swamp":12, "road":17, "structure":50, "water":32}
BLUE, ORANGE = "#2879AE", "#CC6838"
CHARTS, QUERIES = [], {}


def records(frame):
    # Serialize missing values as JSON null (missing values are kept as null).
    return json.loads(frame.to_json(orient="records", date_format="iso", double_precision=8))


def evidence(name, frame, description):
    frame.to_csv(TAB / f"{name}.csv", index=False)
    QUERIES[name] = {"rows":records(frame), "source":{
        "label":description, "files":["data/pipes.csv", "data/train.csv"],
        "evidenceFlow":[{"title":"Local source files", "detail":"Read supplied pipes.csv and train.csv. train.csv is treated as the costs.csv leak history described in the competition brief."},
                        {"title":"Reproducible Python analysis", "detail":f"eda/run_eda.py writes eda/output/tables/{name}.csv. {description}"}],
        "metricDefinitions":[{"label":name, "definition":description}]},
        "methods":[{"language":"text", "code":description + " Reproduce by running eda/run_eda.py."}]}
    return name


def save(fig, slug, title, query, section, en):
    # Export high-resolution PNG and vector SVG (save high-resolution figures).
    fig.savefig(FIG / f"{slug}.png", dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / f"{slug}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    CHARTS.append(dict(id=slug,title=title,query=query,section=section,en=en,
                       image="data:image/png;base64,"+base64.b64encode((FIG/f"{slug}.png").read_bytes()).decode()))
    print(f"Figure {len(CHARTS):02}: {title}", flush=True)


def canvas(title, xlabel="", ylabel="", size=(10,5.5)):
    fig, ax = plt.subplots(figsize=size, layout="constrained")
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    return fig, ax


def map_axes(title):
    fig, ax = canvas(title, "X coordinate (m)", "Y coordinate (m)", (10,9))
    ax.set_aspect("equal")
    ax.grid(False)
    return fig, ax


def main():
    for folder in [FIG, TAB]:
        folder.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook", font="DejaVu Sans",
                  rc={"axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold",
                      "axes.titlesize":15,"axes.labelsize":11,"grid.alpha":.25,"svg.fonttype":"none"})
    p = pd.read_csv(ROOT/"data/pipes.csv")
    t = pd.read_csv(ROOT/"data/train.csv")
    assert not p["Pipe ID"].duplicated().any(), "Duplicate pipe IDs require investigation"
    assert not t["Pipe ID"].duplicated().any(), "Repeated leaks require a different event model"
    assert t["Pipe ID"].isin(p["Pipe ID"]).all(), "Unmatched leak IDs"
    t["event_date"] = pd.to_datetime(t.Date+" "+t.Time, errors="raise")
    assert t.event_date.between(START, END, inclusive="left").all()
    assert (t.Cost>0).all() and np.isfinite(t.Cost).all()
    p["install_date"] = pd.to_datetime(p["Lay date"], errors="raise")
    p["original_material"] = p.Material.fillna("Unknown")
    p["length_m"] = np.hypot(p["GPS x2"]-p["GPS x1"],p["GPS y2"]-p["GPS y1"])
    assert np.isfinite(p.length_m).all() and (p.length_m>0).all()
    p["x"]=(p["GPS x1"]+p["GPS x2"])/2
    p["y"]=(p["GPS y1"]+p["GPS y2"])/2
    d=p.merge(t[["Pipe ID","event_date","Cost"]],on="Pipe ID",how="left",validate="one_to_one")
    d["leaked"]=d.event_date.notna()
    d["current_material"]=np.where(d.leaked,"polyurethane",d.original_material)
    d["remaining_iron"]=d.current_material.isin(IRON)
    d["age_2027"]=(END-d.install_date).dt.total_seconds()/86400/365.25
    d["age_at_leak"]=(d.event_date-d.install_date).dt.total_seconds()/86400/365.25
    # Original-material exposure ends at first leak.
    d["entry"]=d.install_date.where(d.install_date>START,START)
    d.loc[d.install_date.isna(),"entry"]=START
    d["exit"]=d.event_date.fillna(END)
    d["exposure_years"]=(d.exit-d.entry).dt.total_seconds()/86400/365.25
    assert (d.exposure_years>0).all()
    assert not (d.event_date<d.install_date).fillna(False).any()
    d.to_csv(TAB/"pipe_level_enriched.csv",index=False)
    leaks=d[d.leaked].copy()
    source_preview=evidence("source_preview",p[["Pipe ID","Lay date","Material","Surface","GPS x1","GPS y1","GPS x2","GPS y2"]].head(5),"First five raw pipe records in original file order.")
    evidence("leak_preview",t[["Pipe ID","Date","Time","Cost"]].head(5),"First five raw leak records in original file order.")

    missing=pd.concat([p[["Pipe ID","Lay date","Material","Surface","GPS x1","GPS y1","GPS x2","GPS y2"]].isna().sum().rename("pipes.csv"),
                       t[["Pipe ID","Date","Time","Cost"]].isna().sum().rename("train.csv")],axis=1)
    missing=missing.stack().dropna().rename("missing_count").reset_index().rename(columns={"level_0":"column","level_1":"file"})
    q=evidence("missingness",missing,"Missing cells in raw source columns. NA values are parsed as missing, never as zero.")
    fig,ax=canvas("Missing values in source columns","Missing cells","")
    labels=missing.file+" / "+missing.column
    ax.barh(labels,missing.missing_count,color=BLUE)
    ax.invert_yaxis()
    for i,v in enumerate(missing.missing_count):ax.text(v+.2,i,str(int(v)),va="center")
    ax.set_xlim(0,18)
    save(fig,"01_missingness","Missing values in source columns",q,"quality",
         "15 installation dates and 8 materials are missing. No missing values occur in coordinates or leak-record fields. Unknown material must remain unresolved rather than silently classified as iron or polyurethane.")

    summary=d.groupby("original_material").agg(pipes=("Pipe ID","size"),leaks=("leaked","sum"),length_m=("length_m","sum"),
           exposure_years=("exposure_years","sum"),total_cost=("Cost","sum"),median_cost=("Cost","median"),mean_cost=("Cost","mean")).reset_index()
    summary["observed_leak_share"]=summary.leaks/summary.pipes
    lo,hi=proportion_confint(summary.leaks,summary.pipes,method="wilson")
    summary["share_low"],summary["share_high"]=lo,hi
    summary["events_per_100_pipe_years"]=100*summary.leaks/summary.exposure_years
    summary["rate_low"]=100*np.where(summary.leaks>0,stats.chi2.ppf(.025,2*summary.leaks)/2,0)/summary.exposure_years
    summary["rate_high"]=100*stats.chi2.ppf(.975,2*(summary.leaks+1))/2/summary.exposure_years
    qmat=evidence("material_summary",summary,"Original-material counts, recorded first-leak fractions, Wilson 95% intervals, and events per 100 original-material pipe-years with exact Poisson 95% intervals. Exposure stops at leak or 2027-01-01. Intervals assume independent pipes/events and may understate spatial dependence.")
    s=summary.sort_values("pipes")
    fig,ax=canvas("Original pipe materials","Pipes (share of all pipes)","")
    ax.barh(s.original_material,s.pipes,color=[MC[x] for x in s.original_material])
    for i,v in enumerate(s.pipes):ax.text(v+180,i,f"{v:,} ({v/len(d):.1%})",va="center")
    ax.set_xlim(0,s.pipes.max()*1.16)
    save(fig,"02_material_inventory","Original pipe materials",qmat,"inventory",
         "The inventory is dominated by wrought iron. Original material is not the material remaining at the project start: historical leaks trigger polyurethane replacement.")

    state=pd.crosstab(d.original_material,d.current_material).reset_index()
    q=evidence("material_transition",state,"Original material versus reconstructed material on 2027-01-01. Every historical leaking pipe is set to polyurethane; no additional unrecorded changes are assumed.")
    fig,ax=canvas("Material changes after historical leak repairs","Pipes","",(10,6))
    state.set_index("original_material").plot.barh(stacked=True,ax=ax,color=[MC[c] for c in state.columns[1:]])
    ax.set(title="Material changes after historical leak repairs",xlabel="Pipes",ylabel="Original material")
    ax.legend(title="Material at 2027 start",bbox_to_anchor=(1.02,1),loc="upper left")
    save(fig,"03_material_transition","Material changes after historical leak repairs",q,"inventory",
         "This reconstruction is essential before replacement planning. A leak during 2019–2026 removes that pipe from its original material's remaining inventory.")

    surface=d.groupby("Surface").agg(pipes=("Pipe ID","size"),length_m=("length_m","sum"),leaks=("leaked","sum"),remaining_iron=("remaining_iron","sum")).reset_index()
    qs=evidence("surface_summary",surface,"Pipe-level surface labels. Counts and lengths do not measure land area.")
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout="constrained")
    for ax,col,label in zip(axs,["pipes","length_m"],["Pipes","Total pipe length (km)"]):
        vals=surface[col]/(1000 if col=="length_m" else 1)
        ax.barh(surface.Surface,vals,color=[SC[x] for x in surface.Surface]);ax.set_xlabel(label)
    fig.suptitle("Network inventory by surface type",fontweight="bold",fontsize=16)
    save(fig,"04_surface_inventory","Network inventory by surface type",qs,"inventory",
         "Surface is a label attached to each pipe, not a polygon or terrain model. Pipe counts and pipe kilometres must not be interpreted as surface-area proportions.")

    rawcols=["Pipe ID","original_material","current_material","Surface","length_m","age_2027","age_at_leak","leaked","Cost","exposure_years","GPS x1","GPS y1","GPS x2","GPS y2","x","y","remaining_iron"]
    qpipe=evidence("pipe_features",d[rawcols],"One row per pipe. Length is Euclidean endpoint distance in metres, per competition coordinate units; actual bend geometry is unavailable. Age at 2027 is time since original installation, not age of replacement polyurethane. Leak status is observed during 2019–2026, not a future label.")
    fig,ax=canvas("Distribution of individual pipe lengths","Length of one pipe (m)","Number of pipes")
    sns.histplot(d.length_m,bins=60,ax=ax,color=BLUE)
    ax.axvline(d.length_m.median(),color=ORANGE,ls="--",label=f"Median: {d.length_m.median():.1f} m");ax.legend()
    save(fig,"05_length_distribution","Distribution of individual pipe lengths",qpipe,"inventory",
         "This is the distribution of the length of each pipe record—not the total length of the network. Length is computed from the two recorded endpoints and directly affects the $200/m replacement charge.")
    fig,ax=canvas("Time since original installation at 2027","Years since original installation","Pipes")
    sns.histplot(d.age_2027,bins=40,color=BLUE,ax=ax)
    save(fig,"06_age_distribution","Time since original installation at 2027",qpipe,"inventory",
         "All known installation dates precede the 2019 observation window. This is original-installation age, not current polyurethane age; missing dates are excluded.")
    fig,ax=canvas("Installation age differs by original material","Years since original installation at 2027","",(10,6))
    sns.boxplot(data=d,x="age_2027",y="original_material",order=list(MC),hue="original_material",palette=MC,legend=False,ax=ax,fliersize=1)
    save(fig,"07_age_by_material","Installation age differs by original material",qpipe,"inventory",
         "Material and installation age are intertwined. An unadjusted age–leak relationship can reflect material mix rather than an independent aging effect.")
    mix=pd.crosstab(d.original_material,d.Surface)
    q=evidence("material_surface_counts",mix.reset_index(),"Cross-tabulation of original material and surface, one count per pipe.")
    fig,ax=canvas("Surface mix within each original material","Surface","Original material",(10,6))
    sns.heatmap(mix.div(mix.sum(axis=1),axis=0)*100,annot=True,fmt=".1f",cmap="RdBu_r",vmin=0,vmax=100,ax=ax,cbar_kws={"label":"Share within material (%)"})
    save(fig,"08_material_surface_mix","Surface mix within each original material",q,"inventory",
         "Each row sums to 100%. Differences in surface composition can confound comparisons between materials; the Unknown row contains only eight pipes.")

    # Historical time series, not forecasts.
    leaks["year"]=leaks.event_date.dt.year
    annual=leaks.groupby("year").agg(leaks=("Pipe ID","size"),total_cost=("Cost","sum"),median_cost=("Cost","median")).reset_index()
    qa=evidence("annual_leaks",annual,"Recorded historical events and nominal repair dollars by calendar year; future contest years are not included.")
    fig,axs=plt.subplots(2,1,figsize=(11,7),layout="constrained",sharex=True)
    axs[0].bar(annual.year,annual.leaks,color=BLUE);axs[0].set_ylabel("Recorded leaks")
    axs[1].bar(annual.year,annual.total_cost/1e6,color=ORANGE);axs[1].set(ylabel="Repair cost ($M)",xlabel="Year",xticks=list(range(2019,2027)))
    fig.suptitle("Historical leak counts and repair costs",fontweight="bold",fontsize=16)
    save(fig,"09_annual_history","Historical leak counts and repair costs",qa,"time",
         "Counts and total costs do not move identically because leak severity varies. Eight historical years are insufficient to assume a stable future trend or repeat the same years through 2051.")
    monthly=leaks.groupby([leaks.event_date.dt.year.rename("year"),leaks.event_date.dt.month.rename("month")]).size().rename("leaks").reset_index()
    grid=pd.MultiIndex.from_product([range(2019,2027),range(1,13)],names=["year","month"]).to_frame(index=False)
    monthly=grid.merge(monthly,how="left").fillna({"leaks":0})
    q=evidence("monthly_leaks",monthly,"Counts by event year and month; absent calendar cells are zero recorded events.")
    fig,ax=canvas("Monthly leak counts, 2019–2026","Month","Year",(12,5.5))
    sns.heatmap(monthly.pivot(index="year",columns="month",values="leaks"),annot=True,fmt=".0f",cmap="RdBu_r",ax=ax,cbar_kws={"label":"Recorded leaks"})
    save(fig,"10_monthly_heatmap","Monthly leak counts, 2019–2026",q,"time",
         "The year-by-month view distinguishes isolated bursts from recurring seasonality. These are counts without adjustment for the changing material inventory.")
    yearly_mat=leaks.groupby(["year","original_material"]).size().unstack(fill_value=0).reindex(range(2019,2027),fill_value=0)
    q=evidence("year_material_leaks",yearly_mat.reset_index(),"Recorded leaks by year and original material. Original material is not reassigned after repair in this historical classification.")
    fig,ax=canvas("Annual leaks by original material","Year","Recorded leaks")
    for m in yearly_mat.columns:ax.plot(yearly_mat.index,yearly_mat[m],marker="o",label=m,color=MC[m])
    ax.set_xticks(range(2019,2027));ax.legend(ncols=2)
    save(fig,"11_material_time","Annual leaks by original material",q,"time",
         "Separate material series reveal whether aggregate movements are shared across groups. The plot does not establish the cause of any annual surge.")

    fig,ax=canvas("Observed leak fraction by original material","Pipes with a recorded leak, 2019–2026 (%)","")
    s=summary.sort_values("observed_leak_share")
    ax.errorbar(s.observed_leak_share*100,np.arange(len(s)),xerr=np.vstack([(s.observed_leak_share-s.share_low)*100,(s.share_high-s.observed_leak_share)*100]),fmt="o",color=BLUE,capsize=4)
    ax.set_yticks(range(len(s)),[f"{m} (n={n:,})" for m,n in zip(s.original_material,s.pipes)])
    ax.set_xlim(0,100)
    save(fig,"12_material_leak_fraction","Observed leak fraction by original material",qmat,"risk",
         "Points show the eight-year observed fraction, with Wilson 95% intervals. This is neither an annual probability nor a causal material effect. Intervals do not account for spatial dependence.")
    fig,ax=canvas("First-leak incidence by original material","Leaks per 100 original-material pipe-years","")
    s=summary.sort_values("events_per_100_pipe_years")
    ax.errorbar(s.events_per_100_pipe_years,range(len(s)),xerr=np.vstack([s.events_per_100_pipe_years-s.rate_low,s.rate_high-s.events_per_100_pipe_years]),fmt="o",color=ORANGE,capsize=4)
    ax.set_yticks(range(len(s)),s.original_material)
    save(fig,"13_exposure_adjusted_rates","First-leak incidence by original material",qmat,"risk",
         "Exposure ends when a pipe first leaks and is replaced, or at the end of 2026. Exact Poisson 95% intervals are descriptive; zero recorded polyurethane leaks do not prove zero future risk.")
    risk=d.groupby(["original_material","Surface"]).agg(pipes=("Pipe ID","size"),leaks=("leaked","sum")).reset_index()
    risk["fraction"]=risk.leaks/risk.pipes
    q=evidence("material_surface_risk",risk,"Observed eight-year leak fraction within original-material × surface cells. Cells with fewer than 30 pipes are masked on the plot.")
    pp=risk.pivot(index="original_material",columns="Surface",values="fraction")*100
    nn=risk.pivot(index="original_material",columns="Surface",values="pipes")
    fig,ax=canvas("Observed leak fraction: material and surface","Surface","Original material",(11,6))
    sns.heatmap(pp,mask=nn<30,annot=True,fmt=".1f",vmin=0,vmax=100,cmap="RdBu_r",ax=ax,cbar_kws={"label":"Recorded leak fraction (%)"})
    save(fig,"14_material_surface_risk","Observed leak fraction: material and surface",q,"risk",
         "Cross-classification helps reveal heterogeneity hidden by one-variable comparisons. Cells with fewer than 30 pipes are omitted from the graphic; all counts remain in the exported table.")
    bins=[0,45,50,55,60,65,70,75,100]
    d["age_band"]=pd.cut(d.age_2027,bins,right=False)
    age_parts=[]
    for scope,frame in [("All materials",d),("Original iron only",d[d.original_material.isin(IRON)])]:
        part=frame.groupby("age_band",observed=True).agg(pipes=("Pipe ID","size"),leaks=("leaked","sum")).reset_index()
        part["age_band"]=part.age_band.astype(str);part["fraction"]=part.leaks/part.pipes;part["scope"]=scope
        age_parts.append(part)
    age=pd.concat(age_parts,ignore_index=True)
    q=evidence("age_band_leaks",age,"Leak fraction grouped by years since original installation at 2027, shown for all materials and for original iron only. Missing install dates excluded. Bins are descriptive, not learned risk thresholds.")
    fig,axs=plt.subplots(1,2,figsize=(13,5.5),layout="constrained",sharey=True)
    for ax,(scope,part) in zip(axs,age.groupby("scope",sort=False)):
        ax.bar(part.age_band,part.fraction*100,color=BLUE)
        for i,r in part.reset_index(drop=True).iterrows():ax.text(i,r.fraction*100+1,f"n={r.pipes:,}",ha="center",fontsize=8)
        ax.set(title=scope,xlabel="Original-installation age at 2027 (years)",ylabel="Recorded leak fraction (%)")
        ax.tick_params(axis="x",rotation=35)
    fig.suptitle("Observed leaks by original-installation age",fontsize=16,fontweight="bold")
    save(fig,"15_age_leak_fraction","Observed leaks by original-installation age",q,"risk",
         "The left panel includes all materials; the right restricts the comparison to pipes originally made of iron, reducing—but not eliminating—material-mix confounding. Geography and repair-driven removal still affect the pattern, so the bars describe observed groups rather than a causal aging effect.")

    total=float(leaks.Cost.sum());median=float(leaks.Cost.median());mean=float(leaks.Cost.mean())
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout="constrained")
    sns.histplot(leaks.Cost,bins=np.geomspace(leaks.Cost.min(),leaks.Cost.max(),60),ax=axs[0],color=BLUE)
    axs[0].set(xscale="log",xlabel="Repair cost ($, log scale)",ylabel="Recorded leaks")
    ecdf=ECDF(leaks.Cost)
    xx=np.geomspace(leaks.Cost.min(),leaks.Cost.max(),400)
    axs[1].plot(xx,ecdf(xx),color=BLUE);axs[1].set(xscale="log",xlabel="Repair cost ($, log scale)",ylabel="Cumulative fraction of leaks")
    for ax in axs:ax.axvline(median,color=ORANGE,ls="--",label=f"Median: ${median:,.0f}");ax.legend()
    fig.suptitle("Repair costs have a long upper tail",fontsize=16,fontweight="bold")
    save(fig,"16_cost_distribution","Repair costs have a long upper tail",qpipe,"cost",
         f"The median is ${median:,.0f}, versus a mean of ${mean:,.0f}. Logarithmic axes retain all positive costs, including the largest events; the cumulative curve uses statsmodels ECDF.")
    ranked=leaks.Cost.sort_values(ascending=False).to_numpy();n=len(ranked)
    pareto=pd.DataFrame({"top_event_fraction":np.arange(1,n+1)/n,"cumulative_cost_fraction":ranked.cumsum()/total})
    q=evidence("cost_concentration",pareto,"Leaks sorted by descending repair cost; x is cumulative share of events, y is cumulative share of total cost. This is retrospective, not a predictive ranking.")
    top1=float(ranked[:math.ceil(n*.01)].sum()/total);top10=float(ranked[:math.ceil(n*.1)].sum()/total)
    fig,ax=canvas("A small share of leaks drives much of the cost","Highest-cost leaks (% of events)","Cumulative repair cost (%)")
    ax.plot(pareto.top_event_fraction*100,pareto.cumulative_cost_fraction*100,color=BLUE,lw=2)
    ax.plot([0,100],[0,100],ls="--",color="#9AA4AC",label="Equal cost per leak")
    ax.scatter([1,10],[top1*100,top10*100],color=ORANGE,zorder=3)
    ax.annotate(f"Top 1%: {top1:.1%} of cost",(1,top1*100),xytext=(15,top1*100-12),arrowprops={"arrowstyle":"-","color":ORANGE})
    ax.set(xlim=(0,100),ylim=(0,102));ax.legend(loc="lower right")
    save(fig,"17_cost_concentration","A small share of leaks drives much of the cost",q,"cost",
         f"The most expensive 1% of events account for {top1:.1%} of historical repair dollars; the top 10% account for {top10:.1%}. These are hindsight rankings, not an achievable model performance estimate.")
    for field,palette,slug,title in [("original_material",MC,"18_cost_by_material","Repair severity by original material"),("Surface",SC,"19_cost_by_surface","Repair severity by surface type")]:
        fig,ax=canvas(title,"Repair cost ($, log scale)","",(11,6))
        sns.boxplot(data=leaks,x="Cost",y=field,hue=field,palette=palette,legend=False,fliersize=1.7,ax=ax)
        ax.set_xscale("log")
        save(fig,slug,title,qpipe,"cost",
             "Boxplots summarize observed costs conditional on a leak. They do not combine leak probability with severity, and do not by themselves measure replacement priority. Outliers are retained.")
    fig,ax=canvas("Pipe length and observed repair cost","Pipe length (m, log scale)","Repair cost ($, log scale)")
    hb=ax.hexbin(leaks.length_m,leaks.Cost,xscale="log",yscale="log",gridsize=40,mincnt=1,bins="log",cmap="Blues")
    fig.colorbar(hb,ax=ax,label="Leaks per hexagon (log color scale)")
    rho,pvalue=stats.spearmanr(leaks.length_m,leaks.Cost)
    save(fig,"20_length_cost","Pipe length and observed repair cost",qpipe,"cost",
         f"Spearman rank correlation is {rho:.3f}. It compares the rank order of pipe length with the rank order of repair cost: +1 means longer pipes always rank as more expensive, 0 means no monotonic ordering, and -1 means the reverse. Here {rho:.3f} is a weak positive association. Hexagonal bins count overlapping events; this does not show that length causes repair cost.")
    subset=leaks.dropna(subset=["age_at_leak"])
    smooth=lowess(np.log10(subset.Cost),subset.age_at_leak,frac=.3,return_sorted=True)
    age_cost_rho,_=stats.spearmanr(subset.age_at_leak,subset.Cost)
    fig,ax=canvas("Installation age at leak and repair severity","Years since original installation at leak","Repair cost ($, log scale)")
    ax.scatter(subset.age_at_leak,subset.Cost,s=5,alpha=.12,color=BLUE)
    ax.plot(smooth[:,0],10**smooth[:,1],color=ORANGE,lw=2,label="LOWESS of log10(cost)")
    ax.set_yscale("log");ax.legend()
    save(fig,"21_age_cost","Installation age at leak and repair severity",qpipe,"cost",
         f"Each point is one recorded leak, positioned by original-installation age at that leak and repair cost. The orange LOWESS curve summarizes the local tendency of log cost without assuming a straight line; Spearman correlation is {age_cost_rho:.3f}. Read it as evidence about whether older observed pipes tended to have larger repairs, not as a forecast or a causal aging effect. Material, surface, and location can explain part of the pattern.")

    leaks["cost_per_m"]=leaks.Cost/leaks.length_m
    annual_unit=leaks.groupby(["year","original_material"]).agg(
        events=("Pipe ID","size"),mean_cost_per_m=("cost_per_m","mean"),
        median_cost_per_m=("cost_per_m","median")
    ).reset_index()
    material_unit=leaks.groupby("original_material").cost_per_m.mean().rename("material_period_mean")
    annual_unit=annual_unit.join(material_unit,on="original_material")
    annual_unit["difference_from_material_mean_pct"]=(annual_unit.mean_cost_per_m/annual_unit.material_period_mean-1)*100
    q=evidence("annual_material_cost_per_m",annual_unit,"Annual repair cost per endpoint-to-endpoint pipe metre within each original material. Mean and median are nominal dollars; the relative measure compares each annual mean with that material's 2019–2026 mean. Event counts are retained because small cells are unstable.")
    fig,axs=plt.subplots(1,2,figsize=(13,5.5),layout="constrained",sharex=True)
    for ax,column,label in [(axs[0],"mean_cost_per_m","Mean repair cost per metre ($/m)"),(axs[1],"median_cost_per_m","Median repair cost per metre ($/m)")]:
        for material,part in annual_unit.groupby("original_material"):
            ax.plot(part.year,part[column],marker="o",label=material,color=MC[material])
        ax.set(xlabel="Leak year",ylabel=label,yscale="log");ax.set_xticks(range(2019,2027))
    axs[1].legend(loc="upper left",bbox_to_anchor=(1,1),fontsize=8)
    fig.suptitle("Repair cost per pipe metre over time within original material",fontsize=16,fontweight="bold")
    save(fig,"21b_material_cost_per_m_time","Repair cost per metre over time within original material",q,"cost",
         "The left panel shows annual means, which react strongly to rare very expensive repairs; the right shows medians, which describe a typical recorded event. Comparing lines within the same original material removes between-material level differences, but changing surface and location mix can still move the series. Values are nominal dollars and are not inflation-adjusted.")

    relative=annual_unit.pivot(index="original_material",columns="year",values="difference_from_material_mean_pct")
    counts=annual_unit.pivot(index="original_material",columns="year",values="events")
    annotations=relative.copy().astype(object)
    for material in relative.index:
        for year in relative.columns:
            value=relative.loc[material,year];count=counts.loc[material,year]
            annotations.loc[material,year]="" if pd.isna(value) else f"{value:+.0f}%\nn={int(count)}"
    limit=max(25,float(np.nanpercentile(np.abs(relative.to_numpy()),95)))
    fig,ax=canvas("Annual mean repair cost per metre vs each material's own average","Leak year","Original material",(12,6))
    sns.heatmap(relative,annot=annotations,fmt="",cmap="RdBu_r",center=0,vmin=-limit,vmax=limit,ax=ax,cbar_kws={"label":"Difference from material's 2019–2026 mean (%)"})
    save(fig,"21c_material_cost_per_m_heatmap","Annual mean cost per metre relative to each material's own average",q,"cost",
         "Red cells are years above that material's own 2019–2026 mean cost per metre; blue cells are below it. Each cell also shows its number of recorded leaks. This makes within-material rises and falls visible, but extreme repairs can dominate the mean and cells with small n are uncertain.")

    # Plot supplied endpoints and reconstruct post-repair material state.
    segments=d[["GPS x1","GPS y1","GPS x2","GPS y2"]].to_numpy().reshape(-1,2,2)
    fig,ax=map_axes("Pipe-network materials at the start of 2027")
    for cat in d.current_material.value_counts().index:
        ax.add_collection(LineCollection(segments[(d.current_material==cat).to_numpy()],colors=MC[cat],linewidths=.6,label=cat))
    ax.autoscale();ax.legend(loc="upper left",bbox_to_anchor=(1,1),fontsize=9)
    save(fig,"22_material_map","Pipe-network materials at the start of 2027",qpipe,"space",
         "Every pipe appearing in train.csv is treated as replaced with polyurethane after its recorded leak; those pipes are therefore shown as polyurethane. Other pipes retain their original material, and missing material remains Unknown. Coordinates are local metres without a basemap.")

    categories=list(SC)
    surface_codes=pd.Categorical(d.Surface,categories=categories).codes
    sample_points=[];sample_codes=[]
    for segment,code in zip(segments,surface_codes):
        count=max(2,int(np.ceil(np.linalg.norm(segment[1]-segment[0])/10))+1)
        sample_points.append(np.linspace(segment[0],segment[1],count));sample_codes.append(np.full(count,code,dtype=np.int16))
    sample_points=np.concatenate(sample_points);sample_codes=np.concatenate(sample_codes)
    lo=segments.min(axis=(0,1))-60;hi=segments.max(axis=(0,1))+60;step=8.0
    xs=np.arange(lo[0],hi[0]+step,step);ys=np.arange(lo[1],hi[1]+step,step);xx,yy=np.meshgrid(xs,ys)
    distances,nearest=cKDTree(sample_points).query(np.column_stack([xx.ravel(),yy.ravel()]))
    inferred=np.ma.masked_where(distances>60,sample_codes[nearest]).reshape(xx.shape)
    surface_cmap=ListedColormap([SC[c] for c in categories]);surface_cmap.set_bad("white")
    fig,ax=map_axes("Estimated surface regions with pipe network")
    ax.imshow(inferred,origin="lower",extent=[xs[0]-step/2,xs[-1]+step/2,ys[0]-step/2,ys[-1]+step/2],cmap=surface_cmap,vmin=-.5,vmax=len(categories)-.5,interpolation="nearest",alpha=.42)
    ax.add_collection(LineCollection(segments,colors="#4F5963",linewidths=.42,label="Pipes"));ax.autoscale();ax.legend(loc="upper left")
    save(fig,"23_surface_map","Estimated surface regions with pipe network",qpipe,"space",
         "Areas assigned the same recorded surface type use the same fill color, while every pipe is drawn as the same dark line. The background is a nearest-pipe estimate within 60 coordinate units—not measured land boundaries, elevation, or a geographic basemap.")

    fig,ax=map_axes("Pipes replaced after leaks recorded in train.csv")
    ax.add_collection(LineCollection(segments,colors="#BFC5CA",linewidths=.42,label="No recorded replacement in train.csv"))
    ax.add_collection(LineCollection(segments[d.leaked.to_numpy()],colors=ORANGE,linewidths=.72,label="Replaced with polyurethane after recorded leak"))
    ax.autoscale();ax.legend(loc="upper left")
    save(fig,"24_replaced_pipe_map","Pipes replaced after leaks recorded in train.csv",qpipe,"space",
         "Orange lines are exactly the pipes listed in train.csv and therefore treated as replaced with polyurethane after their recorded leak. Every other pipe is gray; this map does not distinguish their original materials.")

    longest=d.nlargest(15,"length_m")[["Pipe ID","length_m","original_material","current_material","leaked","Cost","x","y"]].copy()
    qlong=evidence("longest_pipes",longest,"The 15 longest pipes by endpoint-to-endpoint distance. Repair cost is present only when the pipe appears in train.csv. Selected for a legible labelled map, not because 15 is a learned threshold.")
    fig,ax=map_axes("The 15 longest pipes in the network")
    ax.add_collection(LineCollection(segments,colors="#D3D7DA",linewidths=.35))
    colors=plt.get_cmap("turbo")(np.linspace(.05,.95,len(longest)))
    for color,(idx,row) in zip(colors,longest.iterrows()):
        ax.add_collection(LineCollection([segments[idx]],colors=[color],linewidths=2.2))
        ax.annotate(f"{row.length_m:.1f} m",(row.x,row.y),xytext=(3,3),textcoords="offset points",fontsize=7,color="#20262B",
                    bbox={"boxstyle":"round,pad=.15","facecolor":"white","edgecolor":color,"alpha":.82})
    ax.autoscale()
    save(fig,"25_longest_pipe_map","Map of the 15 longest pipes",qlong,"space",
         "The 15 longest endpoint-to-endpoint pipe records are individually colored and labelled with length; all other pipes are gray. This tests the visual plausibility of a length explanation for expensive repairs, but the overall length–cost Spearman correlation is only weakly positive and several highlighted pipes have no recorded leak cost.")

    expensive=leaks.nlargest(math.ceil(len(leaks)*.01),"Cost").copy()
    qexp=evidence("top1_cost_pipes",expensive[["Pipe ID","Cost","length_m","original_material","Surface","x","y"]],"Pipes in the highest 1% of recorded repair cost, selected by descending Cost with ceil(1% of leak events). Together they account for the reported top-1% cost share.")
    fig,ax=map_axes("Pipes in the highest 1% of recorded repair costs")
    ax.add_collection(LineCollection(segments,colors="#D3D7DA",linewidths=.35))
    expensive_idx=expensive.index.to_numpy();expensive_cost=expensive.Cost.to_numpy()
    norm=LogNorm(vmin=expensive_cost.min(),vmax=expensive_cost.max())
    highlighted=LineCollection(segments[expensive_idx],cmap="plasma",norm=norm,linewidths=1.8)
    highlighted.set_array(expensive_cost);ax.add_collection(highlighted);ax.autoscale()
    fig.colorbar(highlighted,ax=ax,shrink=.7,label="Recorded repair cost ($, log color scale)")
    save(fig,"26_top1_cost_pipe_map","Map of pipes in the highest 1% of repair costs",qexp,"space",
         f"Only the {len(expensive):,} pipes in the highest 1% of recorded repair costs are colored; all other pipes are gray. Color varies with recorded cost on a logarithmic scale. These highlighted events account for {top1:.1%} of historical repair dollars, but their locations do not by themselves explain why the repairs were expensive.")

    remain=d[d.remaining_iron].groupby("original_material").agg(pipes=("Pipe ID","size"),length_m=("length_m","sum")).reset_index()
    remain["linear_cost"]=200*remain.length_m
    q=evidence("remaining_iron_cost",remain,"No-future-leak benchmark: $200 times remaining original-iron length at 2027. Excludes earthwork, work-unit fixed costs and incidental copper/brass replacement. Not a guaranteed lower bound on realized work cost because future leaks replace pipes.")

    # Save provenance and validation checks.
    checks={"pipe_rows":len(p),"leak_rows":len(t),"duplicate_pipe_ids":int(p["Pipe ID"].duplicated().sum()),
       "duplicate_leak_pipe_ids":int(t["Pipe ID"].duplicated().sum()),"unmatched_leak_ids":int((~t["Pipe ID"].isin(p["Pipe ID"])).sum()),
       "nonpositive_lengths":int((d.length_m<=0).sum()),"leaks_before_installation":int((d.event_date<d.install_date).sum()),
       "material_reconciliation":int(summary.pipes.sum())==len(d),"event_reconciliation":int(summary.leaks.sum())==len(t),
       "cost_reconciliation":bool(np.isclose(annual.total_cost.sum(),total)),"figures":len(CHARTS)}
    metrics={**checks,"historical_cost":total,"median_cost":median,"mean_cost":mean,"max_cost":float(leaks.Cost.max()),
       "top1_cost_share":top1,"top10_cost_share":top10,"remaining_iron":int(d.remaining_iron.sum()),
       "remaining_iron_km":float(d.loc[d.remaining_iron,"length_m"].sum()/1000),"linear_cost_benchmark":float(remain.linear_cost.sum()),
       "polyurethane_2027":int((d.current_material=="polyurethane").sum()),"original_iron":int(d.original_material.isin(IRON).sum()),
       "unknown_material_remaining":int((d.current_material=="Unknown").sum()),"spearman_length_cost":float(rho),
       "spearman_age_cost":float(age_cost_rho)}
    (OUT/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    versions={name:importlib.metadata.version(name) for name in ["numpy","pandas","matplotlib","seaborn","scipy","statsmodels"]}
    provenance={"python":platform.python_version(),"libraries":versions,"files":{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ["data/pipes.csv","data/train.csv"]},"checks":checks}
    (OUT/"validation.json").write_text(json.dumps(provenance,indent=2),encoding="utf-8")
    evidence("key_metrics",pd.DataFrame([metrics]),"Reviewed descriptive metrics; original iron is cast iron, gray iron and wrought iron. The history is treated as the complete supplied 2019–2026 event list. Missing materials remain unknown.")
    snapshot={"surface":"report","title":"Star Kingdom: pipe-network EDA","generatedAt":pd.Timestamp.now(tz="UTC").isoformat(),
              "status":"reviewed","buildStatus":"creating","report":{"asOf":"2026-12-31"},"filters":[],"queries":QUERIES}
    (OUT/"reviewed_snapshot.json").write_text(json.dumps(snapshot,ensure_ascii=False),encoding="utf-8")
    (OUT/"report_content.json").write_text(json.dumps({"charts":CHARTS,"metrics":metrics,"versions":versions},ensure_ascii=False),encoding="utf-8")
    print(json.dumps(metrics,indent=2),flush=True)


if __name__ == "__main__":
    main()
