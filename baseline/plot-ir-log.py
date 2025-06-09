#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import argparse
import re
import os

def extract_ir_data_from_log(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Try to isolate the "IR SPECTRUM" block
    ir_block_match = re.search(r"IR SPECTRUM\s+-+\s+Mode\s+freq.+?\n(-+\n)(.*?)(?=\n\n|\Z)", content, re.DOTALL)
    if not ir_block_match:
        print("⚠️  Could not locate IR SPECTRUM block.")
        return [], []

    ir_block = ir_block_match.group(2)

    # Try matching lines like: "  6:    391.33   0.000000    0.00  ..."
    pattern = re.compile(r"\d+:\s+([0-9.]+)\s+[0-9.Ee+-]+\s+([0-9.Ee+-]+)")
    matches = pattern.findall(ir_block)

    if not matches:
        print("⚠️  IR SPECTRUM block found, but no vibrational data matched.")
        print("🔍 Block contents:\n", ir_block[:500])
        return [], []

    frequencies = [float(m[0]) for m in matches]
    intensities = [float(m[1]) for m in matches]

    print("Extracted Frequencies and Intensities:")
    for f, i in zip(frequencies, intensities):
        print(f"{f:.2f} cm⁻¹  ->  {i:.4f} km/mol")

    return frequencies, intensities

def broaden_spectrum(freqs, intensities, fwhm=20.0, resolution=0.5, xrange=(0, 4000)):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    x = np.arange(xrange[0], xrange[1], resolution)
    y = np.zeros_like(x)
    for freq, inten in zip(freqs, intensities):
        y += inten * norm.pdf(x, freq, sigma)
    return x, y

def plot_spectrum(x, y, title, output_pdf):
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, color='black', linewidth=1.5)
    plt.xlabel("Wavenumber (cm⁻¹)")
    plt.ylabel("IR Intensity (km/mol)")
    plt.title(title)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_pdf)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Plot IR spectrum from log file with IR SPECTRUM block")
    parser.add_argument("logfile", help="Log file containing vibrational mode data")
    parser.add_argument("--output", help="Output PDF file name")
    parser.add_argument("--title", help="Custom title for the plot")
    parser.add_argument("--fwhm", type=float, default=20.0, help="FWHM for Gaussian broadening (cm⁻¹)")
    args = parser.parse_args()

    freqs, intensities = extract_ir_data_from_log(args.logfile)
    x, y = broaden_spectrum(freqs, intensities, fwhm=args.fwhm)

    base_name = os.path.splitext(os.path.basename(args.logfile))[0]
    plot_title = args.title if args.title else base_name
    output_pdf = args.output if args.output else base_name + ".jpeg"

    plot_spectrum(x, y, plot_title, output_pdf)
    print(f"Saved IR spectrum to {output_pdf}")

if __name__ == "__main__":
    main()
