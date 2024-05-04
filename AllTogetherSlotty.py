import tkinter as tk
from tkinter import Canvas, Entry, Label, Button, Frame, OptionMenu, StringVar
from tkinter.font import Font
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
                addition = current_crop.tier_two + 30 * current_crop.tier_three + 100 * current_crop.tier_four
                if current_crop.color == 'Yellow':
                    addition *= 1.6
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

class DraggableIcon:
    def __init__(self, canvas, crop, slot_x):
        self.canvas = canvas
        self.crop = crop
        self.size = 60
        self.slot_x = slot_x
        self.icon = self.canvas.create_oval(slot_x, 10, slot_x + self.size, 70, fill=crop.color.lower(), outline='black')

        # Coordinates for text
        text_x = slot_x + self.size / 2
        text_y = 40

        # Create black "border" text slightly offset in all directions
        offset = 1  # Small offset for the shadow effect
        self.text_shadow_n = self.canvas.create_text(text_x, text_y - offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_ne = self.canvas.create_text(text_x + offset, text_y - offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_e = self.canvas.create_text(text_x + offset, text_y, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_se = self.canvas.create_text(text_x + offset, text_y + offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_s = self.canvas.create_text(text_x, text_y + offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_sw = self.canvas.create_text(text_x - offset, text_y + offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_w = self.canvas.create_text(text_x - offset, text_y, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")
        self.text_shadow_nw = self.canvas.create_text(text_x - offset, text_y - offset, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="black")

        # Create white text on top
        self.text = self.canvas.create_text(text_x, text_y, text=f"{crop.plot_id}{(crop.id - 1) % 2 + 1}", font=custom_font, fill="white")

        # Bind events for drag and drop functionality
        self.canvas.tag_bind(self.icon, "<Button-1>", self.start_move)
        self.canvas.tag_bind(self.text, "<Button-1>", self.start_move)
        self.canvas.tag_bind(self.icon, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.icon, "<ButtonRelease-1>", self.stop_move)
        self.canvas.tag_bind(self.text, "<ButtonRelease-1>", self.stop_move)


    def start_move(self, event):
        self.drag_data = {"x": event.x, "y": event.y}

    def on_drag(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move the main icon
        new_x1 = max(min(self.canvas.coords(self.icon)[0] + delta_x, self.canvas.winfo_width() - self.size), 0)
        new_y1 = max(min(self.canvas.coords(self.icon)[1] + delta_y, self.canvas.winfo_height() - self.size), 10)
        new_x2 = new_x1 + self.size
        new_y2 = new_y1 + self.size
        self.canvas.coords(self.icon, new_x1, new_y1, new_x2, new_y2)

        # Move the main text
        new_text_x = new_x1 + self.size / 2
        new_text_y = new_y1 + self.size / 2
        self.canvas.coords(self.text, new_text_x, new_text_y)

        # Move all shadow texts
        offset = 1  # The offset you used for the shadows
        self.canvas.coords(self.text_shadow_n, new_text_x, new_text_y - offset)
        self.canvas.coords(self.text_shadow_ne, new_text_x + offset, new_text_y - offset)
        self.canvas.coords(self.text_shadow_e, new_text_x + offset, new_text_y)
        self.canvas.coords(self.text_shadow_se, new_text_x + offset, new_text_y + offset)
        self.canvas.coords(self.text_shadow_s, new_text_x, new_text_y + offset)
        self.canvas.coords(self.text_shadow_sw, new_text_x - offset, new_text_y + offset)
        self.canvas.coords(self.text_shadow_w, new_text_x - offset, new_text_y)
        self.canvas.coords(self.text_shadow_nw, new_text_x - offset, new_text_y - offset)

        # Update drag data for next event
        self.drag_data = {"x": event.x, "y": event.y}

    def stop_move(self, event):
        # Example logic for snapping; adjust according to your actual snapping logic
        nearest_slot = min(self.canvas.slots, key=lambda x: abs(x + self.size / 2 - event.x))
        distance = abs(nearest_slot + self.size / 2 - event.x)
        if distance <= 10:  # Snap threshold
            self.canvas.coords(self.icon, nearest_slot, 10, nearest_slot + self.size, 70)
            self.canvas.coords(self.text, nearest_slot + self.size / 2, 40)

            # Update shadow texts positions accordingly
            offset = 1
            self.canvas.coords(self.text_shadow_n, nearest_slot + self.size / 2, 40 - offset)
            self.canvas.coords(self.text_shadow_ne, nearest_slot + self.size / 2 + offset, 40 - offset)
            self.canvas.coords(self.text_shadow_e, nearest_slot + self.size / 2 + offset, 40)
            self.canvas.coords(self.text_shadow_se, nearest_slot + self.size / 2 + offset, 40 + offset)
            self.canvas.coords(self.text_shadow_s, nearest_slot + self.size / 2, 40 + offset)
            self.canvas.coords(self.text_shadow_sw, nearest_slot + self.size / 2 - offset, 40 + offset)
            self.canvas.coords(self.text_shadow_w, nearest_slot + self.size / 2 - offset, 40)
            self.canvas.coords(self.text_shadow_nw, nearest_slot + self.size / 2 - offset, 40 - offset)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.crops = []
        self.next_id = 1
        self.icons = []

    def create_widgets(self):
        # Main frame for input fields arranged in a trapezoid
        input_frame = Frame(self.master, width=750, height=300)
        input_frame.pack(side='top', anchor='nw', padx=10, pady=10, fill='x', expand=True)

        self.entries = []
        colors = ["", "Yellow", "Blue", "Purple"]
        plot_ids = ["A", "B", "C", "D", "E"]

        # Custom placement for trapezoid shape
        row_frames = [Frame(input_frame, height=150) for _ in range(2)]
        row_frames[0].pack(fill='x', padx=105, expand=True)  # Top row (narrower)
        row_frames[1].pack(fill='x', expand=True)  # Bottom row (wider)

        # Assign plots to rows for trapezoidal structure
        for i, plot_id in enumerate(plot_ids):
            frame = Frame(row_frames[0 if i < 2 else 1], relief=tk.RAISED, borderwidth=2)
            frame.pack(side='left', fill='y', expand=False)  # Fixed width, not expanding horizontally
            Label(frame, text=f"Plot {plot_id}").pack()

            for j in range(2):
                index = i * 2 + j
                entry_frame = Frame(frame, relief=tk.GROOVE, borderwidth=1, width=200)
                entry_frame.pack(side='left', fill='both', expand=True)
                color_var = StringVar(entry_frame)
                color_var.set(colors[0])
                Label(entry_frame, text=f"Crop {j + 1} Color").pack()
                # Set width of OptionMenu to prevent resizing
                color_option_menu = OptionMenu(entry_frame, color_var, *colors)
                color_option_menu.config(width=10)  # Adjust width as needed
                color_option_menu.pack(fill='x', expand=True)
                tier_entries = []
                for k, tier_label in enumerate(["T1", "T2", "T3", "T4"], start=1):
                    tier_frame = Frame(entry_frame, width=400)  # Adjust width as needed
                    tier_frame.pack(fill='x', expand=False)
                    Label(tier_frame, text=f"{tier_label}: ", anchor='nw').pack(side='left', fill='x')
                    tier_entry = Entry(tier_frame, width=3)
                    tier_entry.pack(side='right',fill='x')
                    tier_entries.append(tier_entry)
                self.entries.append((index, color_var, tier_entries, plot_id))

        # Setup for buttons and canvas remains the same

        # Buttons below the input section
        button_frame = Frame(self.master)
        button_frame.pack(side='top', anchor='nw', padx=200 , pady=10)
        self.add_button = Button(button_frame, text='Add All Crops', command=self.add_all_crops)
        self.add_button.pack(side='left', anchor='nw', padx=10)
        self.confirm_button = Button(button_frame, text="Confirm Arrangement", command=self.confirm_arrangement)
        self.confirm_button.pack(side='left', anchor='nw', padx=10)

        # Canvas below buttons
        self.canvas = Canvas(self.master, width=800, height=100)
        self.canvas.pack(side='top', padx=10, pady=10, anchor='nw')
        self.canvas.slots = [5 + (i * 70) for i in range(10)]
        for slot in self.canvas.slots:
            self.canvas.create_rectangle(slot, 10, slot + 60, 70, outline='gray')

    def add_all_crops(self):
        # Clear existing crops and icons, including shadow texts
        self.crops.clear()
        for icon in self.icons:
            self.canvas.delete(icon.icon)  # Delete the oval/icon
            self.canvas.delete(icon.text)  # Delete the main text

            # Also delete all shadow texts
            self.canvas.delete(icon.text_shadow_n)
            self.canvas.delete(icon.text_shadow_ne)
            self.canvas.delete(icon.text_shadow_e)
            self.canvas.delete(icon.text_shadow_se)
            self.canvas.delete(icon.text_shadow_s)
            self.canvas.delete(icon.text_shadow_sw)
            self.canvas.delete(icon.text_shadow_w)
            self.canvas.delete(icon.text_shadow_nw)

        self.icons.clear()

        # Add new crops as per the current entries
        for index, color_var, tier_entries, plot_id in self.entries:
            color = color_var.get()
            if color:
                tier_values = [int(tier_entry.get() or 0) for tier_entry in tier_entries]
                crop = Crop(self.next_id, color, 1, plot_id, *tier_values)
                self.crops.append(crop)
                slot_x = self.canvas.slots[(self.next_id - 1) % len(self.canvas.slots)]
                icon = DraggableIcon(self.canvas, crop, slot_x)
                self.icons.append(icon)
                self.next_id += 1

    def confirm_arrangement(self):
        # Sort icons based on their position to determine the user-defined order
        sorted_icons = sorted(self.icons, key=lambda icon: self.canvas.coords(icon.icon)[0])
        permutation = [icon.crop.id for icon in sorted_icons]  # This keeps the permutation logic intact
        icon_order = [self.canvas.itemcget(icon.text, 'text') for icon in sorted_icons]  # Get the icon labels

        average_seed_count = simulate_process(self.crops, permutation)
        self.display_results(average_seed_count, icon_order)  # Pass icon_order instead of permutation

    def display_results(self, results, icon_order):
        # Display the results and the icon order in a new window
        result_window = tk.Toplevel(self.master)
        result_window.title("Simulation Results")
        result_label_text = f"Average Seed Count: {results}\nIcon Order: {', '.join(icon_order)}"
        tk.Label(result_window, text=result_label_text).pack(padx=20, pady=20)

root = tk.Tk()
custom_font = Font(family="Helvetica", size=12, weight="bold")
app = Application(master=root)
app.mainloop()
