#!/usr/bin/env python3
import argparse
import os

def split_xyz(input_file, output_prefix="frame", output_dir="."):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    i = 0
    frame = 0
    while i < len(lines):
        try:
            natoms = int(lines[i].strip())
        except ValueError:
            print(f"⚠️  Could not read atom count on line {i+1}")
            break

        end = i + 2 + natoms
        if end > len(lines):
            print(f"⚠️  Incomplete frame at line {i+1}")
            break

        block = lines[i:end]
        frame += 1
        fname = os.path.join(output_dir, f"{output_prefix}_{frame:04d}.xyz")
        with open(fname, 'w') as out:
            out.writelines(block)

        i = end

    print(f"✅ Extracted {frame} frames to '{output_dir}'")

def main():
    parser = argparse.ArgumentParser(description="Split a trajectory XYZ file into separate per-frame XYZ files.")
    parser.add_argument("xyz_file", help="Trajectory .xyz file with multiple geometries")
    parser.add_argument("--prefix", default="frame", help="Filename prefix (default: frame)")
    parser.add_argument("--outdir", default=".", help="Output directory (default: current)")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    split_xyz(args.xyz_file, args.prefix, args.outdir)

if __name__ == "__main__":
    main()
