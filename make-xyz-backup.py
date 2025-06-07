import argparse
import re
import os

def extract_last_geometry(filename):
    atoms = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "Final structure (Angstroms):" in line:
            # Geometry starts 3 lines after this one:
            # Line 1 = "Fragment 1 (Ang)"
            # Line 2 = (blank)
            # Line 3+ = coordinates
            for coord_line in lines[i + 3:]:
                match = re.match(r'^\s*([A-Z][a-z]?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)', coord_line)
                if match:
                    symbol, x, y, z = match.groups()
                    atoms.append((symbol, float(x), float(y), float(z)))
                else:
                    break
            break  # once found, no need to keep scanning

    if not atoms:
        raise RuntimeError("❌ Final structure not found in the file.")

    return atoms

def write_xyz(atoms, outfile):
    with open(outfile, 'w') as f:
        f.write(f"{len(atoms)}\n")
        f.write("Final geometry from Psi4 optimization\n")
        for symbol, x, y, z in atoms:
            f.write(f"{symbol:<2}  {x: >12.6f}  {y: >12.6f}  {z: >12.6f}\n")

def main():
    parser = argparse.ArgumentParser(description="Extract final geometry from Psi4 output and save as .xyz")
    parser.add_argument("logfile", help="Psi4 output file")
    args = parser.parse_args()

    xyzfile = os.path.splitext(args.logfile)[0] + ".xyz"
    atoms = extract_last_geometry(args.logfile)
    write_xyz(atoms, xyzfile)
    print(f"✅ Final structure written to {xyzfile}")

if __name__ == "__main__":
    main()

