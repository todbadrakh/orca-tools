#!/usr/bin/env python3
import argparse
import re
import math

# Constants
HARTREE_TO_KCAL_MOL = 627.509
R = 0.001987  # kcal/mol·K
T = 298.15  # Kelvin
RTln10 = 2.303 * R * T  # kcal/mol

# Use experimental solvated Gibbs free energy of proton
G_PROTON = -270.49 # kcal/mol

def extract_gibbs_energy(filename):
    """
    Extract the final Gibbs free energy from an ORCA output file.
    """
    with open(filename, 'r') as f:
        for line in f:
            if "Final Gibbs free energy" in line:
                match = re.search(r"([-]?\d+\.\d+)\s+Eh", line)
                if match:
                    return float(match.group(1))
    raise ValueError(f"Gibbs free energy not found in {filename}")

def compute_pka(ha, a):
    """
    Computes pKa from HA <-> A- + H+ in solution.
    """
    delta_g =  a * HARTREE_TO_KCAL_MOL - ha * HARTREE_TO_KCAL_MOL + G_PROTON 
    pka = delta_g / (2.303 * R * T)
    return pka, delta_g

def main():
    parser = argparse.ArgumentParser(description="Calculate solution-phase pKa from ORCA log files.")
    parser.add_argument('--ha', required=True, help="ORCA log file for HA (protonated acid)")
    parser.add_argument('--a', required=True, help="ORCA log file for A- (deprotonated base)")

    args = parser.parse_args()

    ha = extract_gibbs_energy(args.ha)
    a = extract_gibbs_energy(args.a)
    print(f"G(ha) = {ha} Ha")
    print(f"G(a)  = {a} Ha")

    pka, delta_g_kcal = compute_pka(ha, a)

    print(f"ΔG = {delta_g_kcal:.3f} kcal/mol")
    print(f"pKa = {pka:.2f}")

if __name__ == "__main__":
    main()
