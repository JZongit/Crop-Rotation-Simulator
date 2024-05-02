import tkinter as tk
import random

class Crop:
    def __init__(self, id, color, harvestable, plot_id, tier_one, tier_two, tier_three, tier_four):
        self.id = id
        self.color = color
        self.harvestable = harvestable
        self.plot_id = plot_id
        self.tier_one = tier_one
        self.tier_two = tier_two
        self.tier_three = tier_three
        self.tier_four = tier_four
        self.initial_state = (harvestable, tier_one, tier_two, tier_three, tier_four)

    def reset(self):
        self.harvestable, self.tier_one, self.tier_two, self.tier_three, self.tier_four = self.initial_state

    def __repr__(self):
        return (f"Crop(ID={self.id}, Color={self.color}, Harvestable={self.harvestable}, "
                f"PlotID={self.plot_id}, TierOne={self.tier_one}, TierTwo={self.tier_two}, "
                f"TierThree={self.tier_three}, TierFour={self.tier_four})")

def simulate_process(crops, permutation, p1=5, p2=20, p3=25, iterations=10000):
    seed_counts = []
    p1 /= 100.0  # Convert percentage to decimal
    p2 /= 100.0
    p3 /= 100.0
    for _ in range(iterations):
        for crop in crops:
            crop.reset()
        seed_count = 0
        for crop_id in permutation:
            current_crop = next((crop for crop in crops if crop.id == crop_id), None)
            if current_crop and current_crop.harvestable:
                current_crop.harvestable = 0
                for other_crop in [c for c in crops if c.plot_id == current_crop.plot_id and c.id != current_crop.id]:
                    if random.random() < 0.4:
                        other_crop.harvestable = 0
                addition = current_crop.tier_two + 20 * current_crop.tier_three + 100 * current_crop.tier_four
                if current_crop.color == 'V':
                    addition *= 2
                seed_count += addition

                for other_crop in [c for c in crops if c.harvestable == 1 and c.color != current_crop.color]:
                    T3Success = sum(random.random() < p1 for _ in range(other_crop.tier_three))
                    other_crop.tier_four += T3Success

                    T2Success = sum(random.random() < p2 for _ in range(other_crop.tier_two))
                    other_crop.tier_three += T2Success - T3Success

                    T1Success = sum(random.random() < p3 for _ in range(other_crop.tier_one))
                    other_crop.tier_two += T1Success - T2Success

                    other_crop.tier_one -= T1Success

        seed_counts.append(seed_count)

    return sum(seed_counts) / len(seed_counts)

class CropInputApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Crop Simulation GUI')
        self.geometry('800x1000')
        self.crops = []
        self.setup_ui()

    def setup_ui(self):
        self.title('Crop Simulation GUI')
        self.geometry('800x1000')  # Adjusted window size

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.output_frame = tk.Frame(self)
        self.output_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entries = []
        plot_labels = ['Plot A', 'Plot B', 'Plot C', 'Plot D', 'Plot E']
        color_options = ['Wild', 'Primal', 'Vivid']

        for plot_label in plot_labels:
            frame = tk.LabelFrame(self.input_frame, text=plot_label, padx=5, pady=5)
            frame.pack(padx=5, pady=5, fill="both", expand=True)

            crop_container = tk.Frame(frame)
            crop_container.pack(fill="both", expand=True)

            for i in range(2):  # Two crops per plot
                crop_frame = tk.Frame(crop_container, relief=tk.RAISED, borderwidth=1)
                crop_frame.pack(side=tk.LEFT, padx=5, pady=5, fill="both", expand=True)

                entry = {'plot_id': plot_label[-1]}  # Capture the plot ID

                # Configure color dropdown with labels inline
                color_label_frame = tk.Frame(crop_frame)
                color_label_frame.pack(side=tk.TOP, fill="x", pady=2)
                tk.Label(color_label_frame, text=f"Crop {i + 1} Color:").pack(side=tk.LEFT, padx=10)
                entry['color'] = tk.StringVar(crop_frame)
                entry['color'].set('')  # Start with an empty string to allow blank selection
                color_dropdown = tk.OptionMenu(color_label_frame, entry['color'], '', *color_options)
                color_dropdown.pack(side=tk.LEFT)
                color_dropdown.config(width=10)

                for j, field in enumerate(['T1', 'T2', 'T3', 'T4']):
                    field_frame = tk.Frame(crop_frame)
                    field_frame.pack(fill="x", pady=2)
                    tk.Label(field_frame, text=field).pack(side=tk.LEFT, padx=10)
                    entry[field.lower()] = tk.Entry(field_frame, width=5)
                    entry[field.lower()].pack(side=tk.LEFT)

                self.entries.append(entry)

        self.process_button = tk.Button(self.input_frame, text="Process Crops", command=self.process_crops)
        self.process_button.pack(pady=5)

        self.result_text = tk.Text(self.output_frame, height=10, width=50)
        self.result_text.pack(padx=5, pady=5)

        # Permutation input with label
        permutation_frame = tk.Frame(self.output_frame)
        permutation_frame.pack(pady=5)
        tk.Label(permutation_frame, text="Input permutation #,#,#...").pack(side=tk.LEFT)
        self.permutation_entry = tk.Entry(permutation_frame, width=50)
        self.permutation_entry.pack(side=tk.LEFT)

        self.simulate_button = tk.Button(self.output_frame, text="Simulate", command=self.run_simulation)
        self.simulate_button.pack(pady=5)

        self.result_label = tk.Label(self.output_frame, text="")
        self.result_label.pack()

    def process_crops(self):
        self.crops = []
        crop_id = 1
        self.result_text.delete('1.0', tk.END)  # Clear existing text before adding new data
        for entry in self.entries:
            color = entry['color'].get()
            if color:  # Ensure a color is selected
                color_map = {'Wild': 'W', 'Primal': 'P', 'Vivid': 'V'}
                crop = Crop(
                    id=crop_id,
                    color=color_map[color],
                    harvestable=1,
                    plot_id=entry['plot_id'],
                    tier_one=int(entry['t1'].get() or 0),
                    tier_two=int(entry['t2'].get() or 0),
                    tier_three=int(entry['t3'].get() or 0),
                    tier_four=int(entry['t4'].get() or 0)
                )
                self.crops.append(crop)
                self.result_text.insert(tk.END, f"CropID {crop_id}, Color {crop.color}, PlotID {crop.plot_id}\n")
                crop_id += 1

    def run_simulation(self):
        if not self.crops:
            self.result_label.config(text="No crops processed.")
            return
        permutation = list(map(int, self.permutation_entry.get().split(',')))
        result = simulate_process(self.crops, permutation)
        self.result_label.config(text=f"Average Seed Count: {result}")

if __name__ == "__main__":
    app = CropInputApp()
    app.mainloop()
