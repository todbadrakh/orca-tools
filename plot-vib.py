import numpy as np
import matplotlib.pyplot as plt
import re
import argparse

def parse_log_file(filename):
    frequencies = []
    intensities = []
    with open(filename, 'r') as file:
        lines = file.readlines()

    start_idx = None
    for i, line in enumerate(lines):
        if re.search(r'mode\s+ω/cm⁻¹', line):
            start_idx = i + 2
            break
    
    if start_idx is None:
        raise ValueError("Could not find vibrational frequencies table header in the file.")
    
    for line in lines[start_idx:]:
        line = line.strip()
        if re.match(r'-{5,}', line) or line == '':
            break
        
        parts = line.split()
        if len(parts) < 5:
            continue
        
        try:
            freq = float(parts[1])
            ts_vib = float(parts[-1])
        except ValueError:
            continue
        
        frequencies.append(freq)
        intensities.append(abs(ts_vib))

    return frequencies, intensities

def main():
    parser = argparse.ArgumentParser(description='Plot vibrational spectrum from a log file.')
    parser.add_argument('logfile', type=str, help='Path to the log file containing vibrational data')
    parser.add_argument('-o', '--output', type=str, default='vibrational_spectrum_from_log.pdf',
                        help='Output filename for the plot (default: vibrational_spectrum_from_log.pdf)')
    parser.add_argument('-w', '--width', type=float, default=5.0,
                        help='Gaussian broadening width in cm⁻¹ (default: 5.0)')
    args = parser.parse_args()

    frequencies, intensities = parse_log_file(args.logfile)

    x_vals = np.linspace(0, 300, 2000)
    spectrum = np.zeros_like(x_vals)

    for freq, inten in zip(frequencies, intensities):
        spectrum += inten * np.exp(-((x_vals - freq) ** 2) / (2 * args.width ** 2))

    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, spectrum, color='green')
    plt.title(f'Vibrational Spectrum from {args.logfile}')
    plt.xlabel('Frequency (cm⁻¹)')
    plt.ylabel('Intensity (arb. units)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(args.output, dpi=300)
    plt.show()

if __name__ == "__main__":
    main()
