#!/usr/bin/env python3
import sys
import numpy as np
import os

def read_xyz(filename):
    with open(filename) as f:
        lines = f.readlines()
    natoms = int(lines[0])
    symbols = []
    coords = []
    for line in lines[2:2+natoms]:
        parts = line.strip().split()
        symbols.append(parts[0])
        coords.append([float(x) for x in parts[1:4]])
    return np.array(symbols), np.array(coords)

def write_xyz(filename, symbols, coords):
    with open(filename, 'w') as f:
        f.write(f"{len(symbols)}\nAligned to XY plane, NH along Y axis\n")
        for s, (x, y, z) in zip(symbols, coords):
            f.write(f"{s} {x:.6f} {y:.6f} {z:.6f}\n")

def rotate(coords, axis, angle):
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return coords @ R.T

def align_molecule(symbols, coords):
    # === customize if needed ===
    ring_indices = [0, 1, 2, 3, 4, 5]  # pyridine ring atoms
    nh_indices = [0, 6]               # N and H atoms of N–H bond

    # Step 1: align ring to XY plane
    ring_coords = coords[ring_indices]
    ring_centered = ring_coords - ring_coords.mean(axis=0)
    _, _, vh = np.linalg.svd(ring_centered)
    normal = vh[2]

    z_axis = np.array([0, 0, 1])
    cross1 = np.cross(normal, z_axis)
    if np.linalg.norm(cross1) > 1e-6:
        angle1 = np.arccos(np.clip(np.dot(normal, z_axis), -1, 1))
        coords = rotate(coords, cross1, angle1)

    # Step 2: align NH vector to Y-axis
    n = coords[nh_indices[0]]
    h = coords[nh_indices[1]]
    nh = h - n
    nh[2] = 0  # project to XY
    nh /= np.linalg.norm(nh)

    y_axis = np.array([0, 1, 0])
    cross2 = np.cross(nh, y_axis)
    angle2 = np.arccos(np.clip(np.dot(nh, y_axis), -1, 1))
    sign2 = np.sign(cross2[2]) if abs(cross2[2]) > 1e-8 else 1.0
    coords = rotate(coords, [0, 0, 1], sign2 * angle2)

    return coords

def main():
    if len(sys.argv) != 2:
        print("Usage: ./align_pyridine_xyz.py input.xyz")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = f"aligned_{os.path.basename(input_file)}"

    symbols, coords = read_xyz(input_file)
    aligned_coords = align_molecule(symbols, coords)
    write_xyz(output_file, symbols, aligned_coords)
    print(f"Aligned XYZ written to: {output_file}")

if __name__ == "__main__":
    main()
