#!/usr/bin/env python3
import argparse
import re
import numpy as np
import matplotlib.pyplot as plt

def parse_psi4_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    freqs, intensities = [], []
    for line in lines:
        if "Freq" in line and "[cm^-1]" in line:
            parts = line.split()
            freq_values = [float(x) for x in parts if re.match(r'^-?\d+\.?\d*$', x)]
            freqs.extend(freq_values)
        elif "IR activ" in line:
            parts = line.split()
            intensity_values = [float(x) for x in parts if re.match(r'^-?\d+\.?\d*$', x)]
            intensities.extend(intensity_values)

    return np.array(freqs), np.array(intensities)

def lorentzian(x, x0, gamma):
    return (gamma / np.pi) / ((x - x0)**2 + gamma**2)

def broaden_spectrum(freqs, intensities, x_range, gamma):
    y = np.zeros_like(x_range)
    for f, inten in zip(freqs, intensities):
        y += inten * lorentzian(x_range, f, gamma)
    return y

def main():
    parser = argparse.ArgumentParser(description="Plot IR spectrum from Psi4 log file")
    parser.add_argument("logfile", help="Path to Psi4 log file")
    parser.add_argument("outfile", help="Output image file (e.g., spectrum.pdf or spectrum.png)")
    parser.add_argument("-g", "--gamma", type=float, default=10.0, help="Lorentzian broadening in cm⁻¹")
    args = parser.parse_args()

    freqs, intensities = parse_psi4_log(args.logfile)

    x = np.linspace(min(freqs) - 100, max(freqs) + 100, 5000)
    y = broaden_spectrum(freqs, intensities, x, args.gamma)

    plt.figure(figsize=(4, 3))
    plt.plot(x, y)
    plt.xlabel("Wavenumber (cm⁻¹)")
    plt.ylabel("Intensity (arb. units)")
    plt.title(str(args.logfile))
    plt.tight_layout()
    plt.savefig(args.outfile)
    print(f"Spectrum saved to {args.outfile}")

if __name__ == "__main__":
    main()
