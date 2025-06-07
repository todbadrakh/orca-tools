import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import argparse
import os

def read_spectrum(filename):
    data = np.loadtxt(filename)
    freqs = data[:, 0]
    intensities = data[:, 1]
    return freqs, intensities

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
    plt.ylabel("IR Intensity (a.u.)")
    plt.title(title)
    plt.grid(True, linestyle=':', alpha=0.5)  # Dotted grid
    plt.tight_layout()
    plt.savefig(output_pdf)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Plot and save IR spectrum as PDF")
    parser.add_argument("filename", help="Input file with frequency and intensity columns")
    parser.add_argument("--output", help="Output PDF file name")
    parser.add_argument("--title", help="Custom title for the plot")
    parser.add_argument("--fwhm", type=float, default=20.0, help="FWHM for Gaussian broadening (cm⁻¹)")
    args = parser.parse_args()

    freqs, intensities = read_spectrum(args.filename)
    x, y = broaden_spectrum(freqs, intensities, fwhm=args.fwhm)

    base_name = os.path.splitext(os.path.basename(args.filename))[0]
    plot_title = args.title if args.title else base_name
    output_pdf = args.output if args.output else base_name + ".jpeg"

    plot_spectrum(x, y, plot_title, output_pdf)
    print(f"Saved PDF: {output_pdf}")

if __name__ == "__main__":
    main()
