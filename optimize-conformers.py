import os
import glob
import argparse
import subprocess

def generate_orca_input(xyz_path, method, basis, inp_path, solvent=None, charge=0, multiplicity=1):
    with open(xyz_path) as f:
        lines = f.readlines()

    try:
        natoms = int(lines[0].strip())
    except ValueError:
        print(f"⚠️  Skipping malformed file: {xyz_path}")
        return False

    title = f"Opt Freq {method} {basis} TightSCF RIJCOSX D3BJ"
    header = f"""\
! {title}
%maxcore 4000
%pal nprocs 4 end
%scf
   maxiter 300
end
"""

    if solvent:
        header += f"""\
%cpcm
   smd true
   smdsolvent "{solvent}"
end
"""

    header += f"\n* xyz {charge} {multiplicity}\n"
    footer = "*\n"

    with open(inp_path, 'w') as out:
        out.write(header)
        out.writelines(lines[2:2 + natoms])
        out.write(footer)

    return True

def run_orca(inp_path, orca_path):
    base = os.path.splitext(inp_path)[0]
    log_path = f"{base}.log"
    cmd = [orca_path, inp_path, "--oversubscribe"]
    print(f"🚀 Running: {' '.join(cmd)}")

    with open(log_path, 'w') as log_file:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(line, end='')
            log_file.write(line)
    proc.wait()
    print(f"✅ Done: {log_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate and run ORCA input files from prefix_*.xyz")
    parser.add_argument("--prefix", default="prefix", help="Filename prefix (default: prefix)")
    parser.add_argument("--method", default="xB97-XD3", help="Functional (default: xB97-XD3)")
    parser.add_argument("--basis", default="def2-TZVPP", help="Basis set (default: def2-TZVPP)")
    parser.add_argument("--orca", default="/opt/orca/6.0.1/orca", help="Path to ORCA executable")
    parser.add_argument("--solvent", help="Optional implicit solvent name (e.g., water, acetonitrile)")
    parser.add_argument("--charge", type=int, default=0, help="Molecular charge (default: 0)")
    parser.add_argument("--multiplicity", type=int, default=1, help="Spin multiplicity (default: 1)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if .log file already exists")
    args = parser.parse_args()

    xyz_files = sorted(glob.glob(f"{args.prefix}_*.xyz"))
    if not xyz_files:
        print("❌ No matching XYZ files found.")
        return

    for xyz_file in xyz_files:
        base = os.path.splitext(xyz_file)[0]
        inp_file = f"{base}.inp"
        log_file = f"{base}.log"

        if args.skip_existing and os.path.exists(log_file):
            print(f"⏩ Skipping existing log: {log_file}")
            continue

        success = generate_orca_input(
            xyz_file,
            args.method,
            args.basis,
            inp_file,
            solvent=args.solvent,
            charge=args.charge,
            multiplicity=args.multiplicity
        )

        if success:
            run_orca(inp_file, args.orca)

if __name__ == "__main__":
    main()
