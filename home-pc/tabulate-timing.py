#!/usr/bin/env python3
import re
import glob
import pandas as pd

# Define timing keys and readable labels
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

# Regex to extract time
time_re = re.compile(r"\.\.\.\s+([0-9.]+)\s+sec")

# Parse files
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

# Create DataFrame
df = pd.DataFrame(rows)
df = df.sort_values("Cores").reset_index(drop=True)

# Ensure all columns are present
for label in timing_keys.values():
    if label not in df:
        df[label] = 0.0

# Format as Markdown
header = "| " + " | ".join(df.columns) + " |"
separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
rows_md = [header, separator]
for _, row in df.iterrows():
    row_str = "| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in row) + " |"
    rows_md.append(row_str)

# Output Markdown table
md_output = "\n".join(rows_md)
print(md_output)

# Optionally save to .md file
with open("timing_table.md", "w") as f:
    f.write(md_output + "\n")
