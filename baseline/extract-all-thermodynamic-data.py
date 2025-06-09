#!/usr/bin/env python3

import re
import glob
from pathlib import Path

HARTREE_TO_KCAL = 627.509

def extract_thermo_data(filepath):
    with open(filepath) as f:
        lines = f.readlines()

    data = {
        "File": Path(filepath).name,
        "E(electronic)": None,
        "ZPE": None,
        "Thermal Energy": None,
        "Entropy Corr": None,
        "G(final)": None
    }

    try:
        data["E(electronic)"] = float([line for line in lines if "FINAL SINGLE POINT ENERGY" in line][-1].split()[-1])
    except IndexError:
        pass

    for line in lines:
        if "Zero point energy" in line:
            match = re.search(r'([-+]?\d+\.\d+)\s+Eh', line)
            if match:
                data["ZPE"] = float(match.group(1))
        elif "Total thermal energy" in line and "..." in line:
            try:
                data["Thermal Energy"] = float(line.split()[-2])
            except Exception:
                pass
        elif "Total entropy correction" in line:
            match = re.search(r'([-+]?\d+\.\d+)\s+Eh', line)
            if match:
                data["Entropy Corr"] = float(match.group(1))
        elif "Final Gibbs free energy" in line:
            match = re.search(r'([-+]?\d+\.\d+)', line)
            if match:
                data["G(final)"] = float(match.group(1))
    return data

def print_table(data_list, headers, title=None):
    if title:
        print("\n" + title)
    print("\t".join(headers))
    for entry in data_list:
        row = [str(entry.get(h, "")) for h in headers]
        print("\t".join(row))

def main():
    files = sorted(glob.glob("*.log"))
    if not files:
        print("❌ No .log files found.")
        return

    headers = ["File", "E(electronic)", "ZPE", "Thermal Energy", "Entropy Corr", "G(final)"]
    results = []

    for f in files:
        try:
            results.append(extract_thermo_data(f))
        except Exception as e:
            print(f"⚠️ Failed to parse {f}: {e}")

    print_table(results, headers, title="Thermodynamic Data Table (tab-separated for Google Docs)")

    # Compute relative Gibbs free energy in kcal/mol
    g_values = [d["G(final)"] for d in results if d["G(final)"] is not None]
    if g_values:
        min_g = min(g_values)
        for d in results:
            g = d["G(final)"]
            d["ΔG (kcal/mol)"] = round((g - min_g) * HARTREE_TO_KCAL, 4) if g is not None else None

        rel_headers = ["File", "G(final)", "ΔG (kcal/mol)"]
        print_table(results, rel_headers, title="Relative Gibbs Free Energies (kcal/mol)")

if __name__ == "__main__":
      main()
