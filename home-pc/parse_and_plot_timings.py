#!/usr/bin/env python3
import re
import glob
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ---- ARGUMENT PARSING ----
parser = argparse.ArgumentParser(description="Analyze ORCA timing from log files.")
parser.add_argument("--prefix", required=True, help="Prefix for log files, e.g. pyr")
args = parser.parse_args()

prefix = args.prefix
pattern = f"{prefix}*.log"
file_re = re.compile(rf"^{re.escape(prefix)}(\d+).log$")

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

# ---- PARSE FILES ----
rows = []

for file in sorted(glob.glob(pattern)):
  match = file_re.match(os.path.basename(file))
  if not match:
    continue
  cores = int(match.group(1))
  times = {"nproc": cores}

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
df = pd.DataFrame(rows).sort_values("nproc").reset_index(drop=True)
for label in timing_keys.values():
  if label not in df:
    df[label] = float("nan")
df = df[["nproc"] + list(timing_keys.values())]

# ---- MARKDOWN TABLE ----
md_file = f"{prefix}_timing_table.md"
with open(md_file, "w") as f:
  header = "| " + " | ".join(df.columns) + " |"
  sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
  f.write(header + "\n" + sep + "\n")
  for _, row in df.iterrows():
    line = "| " + " | ".join(
      f"{v:.3f}" if pd.notna(v) and isinstance(v, float) else "" for v in row
    ) + " |"
    f.write(line + "\n")
print(f"Wrote: {md_file}")

# ---- PLOT ----
components = ["Startup", "SCF", "Integrals", "SCF_Response", "Properties", "Gradient", "Relax"]
colors = plt.cm.tab20.colors

fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(df))

for i, comp in enumerate(components):
  if comp in df:
    ax.bar(df["nproc"], df[comp].fillna(0), bottom=bottom, label=comp, color=colors[i])
    bottom += df[comp].fillna(0)

ax.set_xlabel("Number of nproc")
ax.set_ylabel("Time (seconds)")
ax.set_title(f"Timing Breakdown vs Number of nproc ({prefix})")
ax.legend(title="Component", loc="upper right")
ax.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
fig.savefig(f"{prefix}_timing_plot.png", dpi=300)
print(f"Wrote: {prefix}_timing_plot.png")
