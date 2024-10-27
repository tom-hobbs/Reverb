import tkinter as tk
from soundfile import read, write
from reverb import reverb
from pathlib import Path


# Function to run when the button is pressed
def run_action():
    input_path = entry1.get()
    output_path = entry2.get() + "/" + entry3.get()
    if Path(entry2.get()).exists() is False:
        # create output folder if it does not exist
        Path(entry2.get()).mkdir()
    dry_audio, sample_rate = read(input_path)
    wet_audio = reverb(
        dry_audio,
        sample_rate,
        int(entry4.get()),
        float(entry5.get()),
        int(entry6.get()),
        float(entry7.get()),
        float(entry8.get()),
    )
    if wet_audio.shape[0] < 13230000:
        write(output_path, wet_audio, sample_rate)
    else:
        print("!!!! WARNING very large output file !!!!")
        print("file not saved")


root = tk.Tk()
root.title("Diffusion-delay reverb")
labels = [
    "Input file path:",
    "Output folder:",
    "Output file name:",
    "Diffusion channels:",
    "Diffusion delay (ms):",
    "Duffusion feedthroughs:",
    "Feedback delay (ms):",
    "Feedback gain (%):",
]
entries = []
default_values = [
    "inputs/Brut_Force_Break.wav",
    "outputs",
    "test_output.wav",
    "8",
    "100",
    "1",
    "50",
    "0.5",
]

for i in range(8):
    label = tk.Label(root, text=labels[i])
    label.grid(row=i, column=0, padx=(10, 1), pady=1, sticky="e")
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=(1, 10), pady=1)
    entry.insert(0, default_values[i])
    entries.append(entry)

entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8 = entries

run_button = tk.Button(root, text="Run", command=run_action)
run_button.grid(row=8, columnspan=2, pady=10)

root.mainloop()
