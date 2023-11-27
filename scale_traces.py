import os
import shutil
import subprocess

# Base directory where traces are stored
base_dir = 'network/traces'

# Directory to save the scaled traces
scaled_dir = 'network/scaled_traces'

if os.path.exists(scaled_dir):
    shutil.rmtree(scaled_dir)

# Recursively go through the directory structure
for dirpath, dirnames, filenames in os.walk(base_dir):
    for file in filenames:
        # Check if the file is a trace (adjust this as needed)
        if file.endswith(('.dat', '.trace', '.log')): # You can add more extensions if required
            # Create the same folder structure in scaled_traces
            relative_path = os.path.relpath(dirpath, base_dir)
            for mbps in [1, 2, 3]:
                new_dir = os.path.join(scaled_dir, f"{mbps}mbps", relative_path)
                os.makedirs(new_dir, exist_ok=True)
                # Construct the input and output file paths
                trace_in = os.path.join(dirpath, file)
                trace_out = os.path.join(new_dir, file.replace('.dat', f'_scaled_{mbps}mbps.dat'))
                # Call the scale_trace.py script for each speed
                cmd = [
                    'python3', 'network/scale_trace.py',
                    '--trace-in', trace_in,
                    '--trace-out', trace_out,
                    f'--target-mbps={mbps}'
                ]
                subprocess.run(cmd)
print("Scaling complete!")