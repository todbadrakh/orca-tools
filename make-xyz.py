import argparse
import re
import os

periodic_table = {
    1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I'
}

def extract_last_geometry(filename):
    atoms = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # for converged log files
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
    if not atoms:
        raise RuntimeError("❌ Final structure not found in the file.")
    return atoms

def atomic_symbol(z):
    periodic_table = {
        1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I'
    }
    return periodic_table.get(z, f"Z{z}")

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

