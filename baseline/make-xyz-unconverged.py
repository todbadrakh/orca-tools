#!/usr/bin/env python3
import re
import sys
import os

periodic_table = {
    1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I'
}

if len(sys.argv) != 2:
    print("Usage: python extract_last_geometry.py <logfile>")
    sys.exit(1)

logfile = sys.argv[1]
outfile = os.path.splitext(logfile)[0] + ".xyz"

atoms = []
current_atoms = []

with open(logfile) as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Z (Atomic Numbers)" in line:
        current_atoms = []
        for coord_line in lines[i + 1:]:
            parts = coord_line.strip().split()
            if len(parts) >= 5:
                try:
                    z = int(float(parts[0]))
                    mass = float(parts[1])
                    x = float(parts[2]) * 0.529177
                    y = float(parts[3]) * 0.529177
                    z_coord = float(parts[4]) * 0.529177
                    symbol = periodic_table.get(z, f"Z{z}")
                    current_atoms.append((symbol, x, y, z_coord))
                except ValueError:
                    break
            else:
                break
        atoms = current_atoms

with open(outfile, "w") as f:
    f.write(f"{len(atoms)}\n")
    f.write("Last coordinate block from log file\n")
    for symbol, x, y, z in atoms:
        f.write(f"{symbol:<2}  {x:12.6f}  {y:12.6f}  {z:12.6f}\n")

print(f"Geometry written to {outfile}")
