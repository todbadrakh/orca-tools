#!/usr/bin/env python3
import re
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---- SETTINGS ----
timing_keys = {
    "Sum of individual times": "Total",
    "Startup calculation": "Startup",
    "SCF iterations": "SCF",
    "Property integrals": "Integrals",
    "SCF Response": "SCF_Response",
    "Property calculations": "Properties",
    "SCF Gradient evaluation": "Gradient",
    "Geometry relaxation": "Relax"
}
time_re = re.compile(r"\.\.\.\s+([0-9.]+)\s+sec")

# ---- PARSE LOG FILES ----
rows = []

for file in sorted(glob.glob("pyr-*cores.log")):
    core_match = re.search(r"pyr-(\d+)cores\.log", file)
    if not core_match:
        continue
    cores = int(core_match.group(1))
    times = {"Cores": cores}

    with open(file) as f:
        for line in f:
            for key, label in timing_keys.items():
                if line.strip().startswith(key):
                    match = time_re.search(line)
                    if match:
                        times[label] = float(match.group(1))
                    break

    rows.append(times)

# ---- CREATE DATAFRAME ----
df = pd.DataFrame(rows)
df = df.sort_values("Cores").reset_index(drop=True)
for label in timing_keys.values():
    if label not in df:
        df[label] = float("nan")
df = df[["Cores"] + list(timing_keys.values())]

# ---- PRINT MARKDOWN ----
header = "| " + " | ".join(df.columns) + " |"
separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
rows_md = [header, separator]
for _, row in df.iterrows():
    row_str = "| " + " | ".join(
        f"{v:.3f}" if pd.notna(v) and isinstance(v, float) else "" for v in row
    ) + " |"
    rows_md.append(row_str)

md_output = "\n".join(rows_md)
print(md_output)

with open("timing_table.md", "w") as f:
    f.write(md_output + "\n")

# ---- PLOT ----
components = ["Startup", "SCF", "Integrals", "SCF_Response", "Properties", "Gradient", "Relax"]
colors = plt.cm.tab20.colors

fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(df))

for i, comp in enumerate(components):
    if comp in df:
        ax.bar(df["Cores"], df[comp].fillna(0), bottom=bottom, label=comp, color=colors[i])
        bottom += df[comp].fillna(0)

ax.set_xlabel("Number of Cores")
ax.set_ylabel("Time (seconds)")
ax.set_title("Timing Breakdown vs Number of Cores")
ax.legend(title="Component", loc="upper right")
ax.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("timing_plot.png", dpi=300)
