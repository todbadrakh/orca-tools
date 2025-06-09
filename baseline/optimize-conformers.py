#!/usr/bin/env python3
import os
import glob
import argparse
import subprocess

def generate_orca_input(xyz_path, method, basis, inp_path, solvent=None, charge=0, multiplicity=1):
  
  """ Generates ORCA opt freq input files.

      Arguments:

        xyz_path       path to xyz file
        method         theoretical method
        basis          basis set
        inp_path       path to generated .inp file
        solvent        cpcm solvent
        charge         molecular electric charge in atomic units
        multiplicity   molecular spin multiplicity
  
  """

  with open(xyz_path) as f:
    lines = f.readlines()

  try:
    natoms = int(lines[0].strip())
  except ValueError:
    print(f"⚠️  Skipping malformed file: {xyz_path}")
    return False

  title = f"Opt Freq {method} {basis}"
  header = f"""\
! {title} cpcm(water)
%maxcore 2000
%pal nprocs 64 end
%scf
   maxiter 300
end
"""

  header += f"\n* xyz {charge} {multiplicity}\n"
  footer = "*\n"

  with open(inp_path, 'w') as out:
    out.write(header)
    out.writelines(lines[2:2 + natoms])
    out.write(footer)

  return True

def generate_submit_script(input, partition, jobname, setup_path, orca_path, scratch):

  """ Generates Slurm submit scripts.

      Arguments:

        input          input file name
        jobname        jobname
        setup_path     path to the SETUP_ENV script
        orca_path      path to the ORCA executable
        scratch        path to the scratch directory
  """

  cwd = os.getcwd()

  script=f"""\
#!/bin/bash
#SBATCH -A stf243
#SBATCH -J {jobname}
#SBATCH -o %x-%j.out
#SBATCH -t 1:00:00
#SBATCH -p {partition}
#SBATCH -N 1

input={input}

# Setup environment to expose ORCA 6.0.1
source {setup_path}

# Setup scratch directory
scratch={scratch}
mkdir -p {scratch}

# Copy input files to scratch directory
cp {input}.inp {scratch}/.
cp h2o.xyz {scratch}/.

# Go to scratch directory and run the calculation
cd {scratch}
{orca_path} {input}.inp --use-hwthread-cpus > {cwd}/{input}.log

# Copy output files back to submit directory
cp -r {scratch}/* cwd/.

# Clean up scratch directory
rm -rf {scratch}
"""
  
  with open(f"{jobname}.slurm", 'w') as out:
    out.write(script)

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
  print(f" Calculation done: {log_path}")

def submit_job(submit_script):

  """ Submits the Slurm job.

      Arguments:

        submit_script     path to the submit script

  """
	
  if not submit_script:
    raise ValueError("submit_script is None or empty")

  if not os.path.isfile(submit_script):
    raise FileNotFoundError(f"Submit script not found: {submit_script}")

  cmd = ["sbatch", submit_script]
  print(f"Running command: {' '.join(cmd)}")

  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  stdout, _ = proc.communicate()
  print("sbatch output:\n", stdout.strip())

def main():
  parser = argparse.ArgumentParser(description="Generate and run ORCA input files from prefix_*.xyz")
  parser.add_argument("--prefix", default="prefix", help="Filename prefix (default: prefix)")
  parser.add_argument("--method", default="wB97X-D3", help="Functional (default: wB97X-D3)")
  parser.add_argument("--basis", default="def2-TZVPP", help="Basis set (default: def2-TZVP)")
  parser.add_argument("--solvent", help="Optional implicit solvent name (e.g., water, acetonitrile)")
  parser.add_argument("--charge", type=int, default=0, help="Molecular charge (default: 0)")
  parser.add_argument("--multiplicity", type=int, default=1, help="Spin multiplicity (default: 1)")
  parser.add_argument("--skip-existing", action="store_true", help="Skip if .log file already exists")
  parser.add_argument("--orca_path", help="Full path to the ORCA 6.0.1 executable")
  parser.add_argument("--setup_path", help="Full path to the SETUP_ENV script")
  parser.add_argument("--jobname", default="conformer-search", help="Input file name")
  parser.add_argument("--scratch", default="/tmp/${USER}/orca", help="Scratch directory")
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

    orca_input = generate_orca_input(
      xyz_file,
      args.method,
      args.basis,
      inp_file,
      solvent=args.solvent,
      charge=args.charge,
      multiplicity=args.multiplicity
    )

    submit_script = generate_submit_script(
      f"{base}",
      'test',
      f"{base}", 
      args.setup_path, 
      args.orca_path,
      args.scratch
    )
    
    if submit_script:
      submit_job(f"{base}.slurm")

if __name__ == "__main__":
  
  main()
