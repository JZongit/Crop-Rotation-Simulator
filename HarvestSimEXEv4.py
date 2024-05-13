import tkinter as tk
from tkinter import Canvas, Entry, Label, Button, Frame, OptionMenu, StringVar, Checkbutton
from tkinter.font import Font
import random
import math

class Crop:
    """Represents a crop with various attributes and methods to manage its state."""
    def __init__(self, id, color, harvestable, plot_id, tier_one, tier_two, tier_three, tier_four):
        """Initialize a new crop with specific attributes."""
        self.id = id  # Unique identifier for the crop
        self.color = color  # Visual representation color for the crop
        self.harvestable = harvestable  # Status indicating if the crop can be harvested
        self.plot_id = plot_id  # Identifier for the plot this crop belongs to
        self.tier_one = tier_one  # First tier value influencing the crop's output
        self.tier_two = tier_two  # Second tier value
        self.tier_three = tier_three  # Third tier value
        self.tier_four = tier_four  # Fourth tier value
        self.initial_state = (harvestable, tier_one, tier_two, tier_three, tier_four)  # Save initial state for reset

    def reset(self):
        """Reset the crop to its initial state."""
        self.harvestable, self.tier_one, self.tier_two, self.tier_three, self.tier_four = self.initial_state

    def __repr__(self):
        """Provide a string representation of the crop for debugging and logging purposes."""
        return (f"Crop(ID={self.id}, Color={self.color}, Harvestable={self.harvestable}, "
                f"PlotID={self.plot_id}, TierOne={self.tier_one}, TierTwo={self.tier_two}, "
                f"TierThree={self.tier_three}, TierFour={self.tier_four})")

def simulate_process(crops, permutation, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1=5, p2=20, p3=25, iterations=10000):
    """Simulate the crop processing to calculate average and variance of seed counts."""
    seed_counts = []
    p1 /= 100.0  # Convert percentage probability to decimal for calculation
    p2 /= 100.0
    p3 /= 100.0
    for _ in range(iterations):  # Loop through each simulation iteration
        for crop in crops:
            crop.reset()  # Reset crops to initial state before each simulation run
        seed_count = 0       # Sets the seed count to 0 for the start of the iteration
        for crop_id in permutation:  # Process each crop based on the permutation of IDs
            current_crop = next((crop for crop in crops if crop.id == crop_id), None)
            if current_crop and current_crop.harvestable:
                current_crop.harvestable = 0  # Mark crop as non-harvestable after processing
                # Check for adjacency effects within the same plot
                for other_crop in [c for c in crops if c.plot_id == current_crop.plot_id and c.id != current_crop.id]:
                    if random.random() < 0.4:
                        other_crop.harvestable = 0
                # Calculate seed addition based on crop tier values and multipliers
                addition = current_crop.tier_two + t3_mult * current_crop.tier_three + t4_mult * current_crop.tier_four
                # Apply color-specific multipliers
                if current_crop.color == 'Yellow':
                    addition *= vivid_mult
                if current_crop.color == 'Blue':
                    addition *= primal_mult
                if current_crop.color == 'Purple':
                    addition *= wild_mult
                seed_count += addition

                # Additional effects on other crops based on tier probabilities
                for other_crop in [c for c in crops if c.harvestable == 1 and c.color != current_crop.color]:
                    T3Success = sum(random.random() < p1 for _ in range(other_crop.tier_three))
                    other_crop.tier_four += T3Success

                    T2Success = sum(random.random() < p2 for _ in range(other_crop.tier_two))
                    other_crop.tier_three += T2Success - T3Success

                    T1Success = sum(random.random() < p3 for _ in range(other_crop.tier_one))
                    other_crop.tier_two += T1Success - T2Success

                    other_crop.tier_one -= T1Success

        seed_counts.append(seed_count)  # Record seed count separately for this iteration so the value can be reset

    average_seed_count = sum(seed_counts) / len(seed_counts)  # Calculate average seed count
    variance = sum((x - average_seed_count) ** 2 for x in seed_counts) / len(seed_counts)  # Calculate variance
    return average_seed_count, variance

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

    nonoslots = []
    def start_move(self, event):
        self.drag_data = {"x": event.x, "y": event.y}
        icon_x1, icon_y1, icon_x2, icon_y2 = self.canvas.coords(self.icon)
        icon_center_x = (icon_x1 + icon_x2) / 2
        icon_center_y = (icon_y1 + icon_y2) / 2

        # Find the nearest slot based on the icon's center position
        nearest_slotx = min(self.canvas.slots, key=lambda x: abs(x + self.size / 2 - icon_center_x))
        yanchor = (110, 110, 110, 110, 110, 110, 110, 110, 110, 110)  # Example y-positions
        nearest_sloty = min(yanchor, key=lambda y: abs(y + self.size / 2 - icon_center_y))

        # Calculate distances
        distancex = abs(nearest_slotx + self.size / 2 - icon_center_x)
        distancey = abs(nearest_sloty + self.size / 2 - icon_center_y)

        # Check if the icon is within the snapping threshold
        if distancex <= 1 and distancey <= 1 and nearest_slotx in DraggableIcon.nonoslots:
            DraggableIcon.nonoslots.remove(nearest_slotx)
        print(DraggableIcon.nonoslots)



    def on_drag(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move the main icon
        new_x1 = max(min(self.canvas.coords(self.icon)[0] + delta_x, self.canvas.winfo_width() - self.size), 0)
        new_y1 = max(min(self.canvas.coords(self.icon)[1] + delta_y, self.canvas.winfo_height() - self.size), -10)
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
        # Get the current position of the icon
        icon_x1, icon_y1, icon_x2, icon_y2 = self.canvas.coords(self.icon)
        icon_center_x = (icon_x1 + icon_x2) / 2
        icon_center_y = (icon_y1 + icon_y2) / 2

        # Find the nearest slot based on the icon's center position
        nearest_slotx = min(self.canvas.slots, key=lambda x: abs(x + self.size / 2 - icon_center_x))
        yanchor = (110, 110, 110, 110, 110, 110, 110, 110, 110, 110)  # Example y-positions
        nearest_sloty = min(yanchor, key=lambda y: abs(y + self.size / 2 - icon_center_y))

        # Calculate distances
        distancex = abs(nearest_slotx + self.size / 2 - icon_center_x)
        distancey = abs(nearest_sloty + self.size / 2 - icon_center_y)

        # Check if the icon is within the snapping threshold
        if distancex <= 40 and distancey <= 50 and nearest_slotx not in DraggableIcon.nonoslots:
            # Update the coordinates of the icon to snap it into place
            self.canvas.coords(self.icon, nearest_slotx, nearest_sloty, nearest_slotx + self.size,
                               nearest_sloty + self.size)
            # Update the main text to be centered over the icon
            self.canvas.coords(self.text, nearest_slotx + self.size / 2, nearest_sloty + self.size / 2)

            # Update shadow texts positions accordingly
            offset = 1
            self.update_shadow_texts(nearest_slotx + self.size / 2, nearest_sloty + self.size / 2, offset)

            # Append to nonoslots if the slot is occupied now
            DraggableIcon.nonoslots.append(nearest_slotx)


    def update_shadow_texts(self, text_x, text_y, offset):
        self.canvas.coords(self.text_shadow_n, text_x, text_y - offset)
        self.canvas.coords(self.text_shadow_ne, text_x + offset, text_y - offset)
        self.canvas.coords(self.text_shadow_e, text_x + offset, text_y)
        self.canvas.coords(self.text_shadow_se, text_x + offset, text_y + offset)
        self.canvas.coords(self.text_shadow_s, text_x, text_y + offset)
        self.canvas.coords(self.text_shadow_sw, text_x - offset, text_y + offset)
        self.canvas.coords(self.text_shadow_w, text_x - offset, text_y)
        self.canvas.coords(self.text_shadow_nw, text_x - offset, text_y - offset)


class CustomCheckbox:
    all_checkboxes = []  # Class-level list to hold all checkbox instances
    def __init__(self, master, text, color, variable, checkboxes):
        self.variable = variable
        self.color = color
        self.checkboxes = checkboxes

        self.label = tk.Label(master, text="  ", bg=color.lower(), fg='#57B640', font=('Helvetica', '16', 'bold', 'normal'), width=2)
        self.label.bind("<Button-1>", self.toggle)
        self.label.pack()

        self.update_display()
        CustomCheckbox.all_checkboxes.append(self)

    def toggle(self, event=None):
        if self.variable.get() == self.color:
            self.variable.set('')  # Deselect if this checkbox is currently selected
        else:
            self.variable.set(self.color)  # Select this checkbox
            for checkbox in self.checkboxes:
                checkbox.update_display()

        self.update_display()

    def update_display(self):
        if self.variable.get() == self.color:
            self.label.config(text="X")
        else:
            self.label.config(text=" ")

    def pack(self, *args, **kwargs):
        self.label.pack(*args, **kwargs)

    def get(self):
        return self.variable.get()

    @classmethod
    def clearexes(cls):
        for chkbx in cls.all_checkboxes:
            chkbx.variable.set('')  # Clear the variable
            chkbx.update_display()  # Update display to reflect the change

def setup_checkboxes(master):
    var = tk.StringVar(value='')  # Unique StringVar for each group of checkboxes
    checkboxes = []
    colors = ["Yellow", "Blue", "Purple"]  # Ensure color names here match those used in the GUI
    for color in colors:
        cb = CustomCheckbox(master, color, color, var, checkboxes)
        checkboxes.append(cb)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(side='left', padx=(40,0))
        self.create_widgets()
        self.crops = []
        self.next_id = 1
        self.icons = []

    def create_widgets(self):
        # Main frame for input fields arranged in a trapezoid
        input_frame = Frame(self.master, width=750, height=300)
        input_frame.pack(side='top', padx=25, anchor='nw', fill='x', expand=True)

        # Frame for settings directly next to the top row (Plot A)
        settings_frame = Frame(input_frame, relief=tk.RAISED, borderwidth=2)
        settings_frame.place(x=0, y=0, width=105, height=160)  # Position this frame at specific coordinates

        settings_title = Label(settings_frame, text="Settings:", font=('Helvetica', '12', 'bold'))
        settings_title.pack(side='top')  # Add some padding to give space around the title

        # Adding labeled text fields for multipliers and factors
        labels = ["   T3 Mult:", "   T4 Mult:", "Yellow/D:", "Purple/D:", "    Blue/D:"]
        defaults = ["26", "100", "4000", "9000", "9000"]
        self.settings_entries = []
        for idx, label in enumerate(labels):
            frame = Frame(settings_frame)
            frame.pack(fill='x', pady=3)
            Label(frame, text=label).pack(side='left')
            entry = Entry(frame, width=5)
            entry.pack(side='right', padx=2)
            entry.insert(0, defaults[idx])  # Access default value using the loop index
            self.settings_entries.append(entry)

        tips_frame = Frame(self.master, relief=tk.RAISED, borderwidth=2)
        tips_frame.place(x=620, y=0, width=120, height=160)

        tips_title = Label(tips_frame, text="Tips:", font=('Helvetica', '12', 'bold'))
        tips_title.pack(side='top')
        tips_text = Label(tips_frame, text="Selecting no color will prevent crop from "
                                            "being added.\n\n Inputting no tier counts "
                                            "will default to T1 = 23 (unupgraded crop)", wraplength=110)
        tips_text.pack(side='top')

        # Entry and checkbox setup in Application's create_widgets method
        self.entries = []
        colors = ["Yellow", "Blue", "Purple"]
        plot_ids = ["A", "B", "C", "D", "E"]

        # Custom placement for trapezoid shape
        row_frames = [Frame(input_frame, height=150) for _ in range(2)]
        row_frames[0].pack(fill='x', padx=109, expand=True)  # Top row (narrower)
        row_frames[1].pack(fill='x', expand=True)  # Bottom row (wider)

        # Assign plots to rows for trapezoidal structure
        for i, plot_id in enumerate(plot_ids):
            frame = Frame(row_frames[0 if i < 2 else 1], relief=tk.RAISED, borderwidth=2)
            frame.pack(side='left', fill='y', expand=False)

            Label(frame, text=f"Plot {plot_id}", font=('Helvetica', '10', 'bold')).pack()  # Label for each plot

            for j in range(2):
                index = i * 2 + j
                entry_frame = Frame(frame, relief=tk.GROOVE, borderwidth=1, width=200)
                entry_frame.pack(side='left', fill='both', expand=True)

                # Label for each crop color within the plot
                Label(entry_frame, text=f"Crop {j + 1} Color:").pack()  # Ensure this label is correctly included

                checkbox_frame = Frame(entry_frame)
                checkbox_frame.pack()

                var = tk.StringVar(value='')  # This controls the active state of the checkboxes
                checkboxes = []  # Initialize the list to store checkbox instances for this group

                for color in colors:
                    # Create each checkbox and add it to the list
                    cb = CustomCheckbox(checkbox_frame, color, color, var, checkboxes)
                    cb.pack(side='left')
                    checkboxes.append(cb)  # Add the newly created checkbox to the list



                tier_entries = []
                for k, tier_label in enumerate(["T1", "T2", "T3", "T4"], start=1):
                    tier_frame = Frame(entry_frame, width=400)  # Adjust width as needed
                    tier_frame.pack(fill='x', expand=False)
                    Label(tier_frame, text=f"{tier_label}: ", anchor='nw').pack(side='left', fill='x', padx=(30, 0))
                    tier_entry = Entry(tier_frame, width=3)
                    tier_entry.pack(side='right', fill='x', padx=(0, 30))
                    tier_entries.append(tier_entry)
                self.entries.append((index, var, tier_entries, plot_id))

        # Setup for buttons and canvas remains the same

        # Buttons below the input section
        button_frame = Frame(self.master)
        button_frame.place(x=58, y=330)  # Use fixed coordinates. Adjust x and y to match your layout needs.
        self.add_button = Button(button_frame, text='Add/Update Crops', command=self.add_all_crops)
        self.add_button.pack(side='left', anchor='nw', padx=(10, 0))
        self.confirm_button = Button(button_frame, text="Simulate Harvest Order", command=self.confirm_arrangement)
        self.confirm_button.pack(side='left', anchor='nw', padx=(30, 0))
        self.resetperm_button = Button(button_frame, text="Clear Current Order", command=self.add_all_crops)
        self.resetperm_button.pack(side='left', padx=(5, 0))  # Adjust location as needed
        self.clear_button = Button(button_frame, text="Clear Tier Counts", command=self.clear_tier_entries)
        self.clear_button.pack(side='left', padx=(30, 0))  # Adjust location as needed
        self.resetcolors_button = Button(button_frame, text='Reset Crop Colors', command=CustomCheckbox.clearexes)
        self.resetcolors_button.pack(side='left', padx=5)

        # Canvas below buttons
        self.canvas = Canvas(self.master, width=800, height=200)
        self.canvas.pack(side='bottom', padx=10, pady=10, anchor='nw',  fill='y')
        self.canvas.slots = [5 + (i * 70) for i in range(10)]
        for slot in self.canvas.slots:
            self.canvas.create_rectangle(slot, 110, slot + 60, 170, outline='gray')



    def clear_tier_entries(self):
        for index, var, tier_entries, plot_id in self.entries:
            for tier_entry in tier_entries:
                tier_entry.delete(0, tk.END)  # Clear the entry

    def validate_integer(self, P):
        # Validation function to ensure only integers are entered
        if P.isdigit() or P == "":
            return True
        return False

    def add_all_crops(self):
        # Clear existing crops and icons, including shadow texts
        self.crops.clear()
        DraggableIcon.nonoslots.clear()
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
        self.next_id = 1

        total_slots = len(self.canvas.slots)
        num_crops = len([entry for entry in self.entries if entry[1].get()])  # Count non-empty colors
        offset = (total_slots - num_crops) // 2  # Calculate the offset to center the icons

        # Add new crops as per the current entries
        for index, var, tier_entries, plot_id in self.entries:
            color = var.get()
            if color:
                # Check if all tier entries are blank
                all_blank = all(not tier_entry.get().strip() for tier_entry in tier_entries)

                # Set default values depending on the all_blank flag
                tier_values = []
                for i, tier_entry in enumerate(tier_entries):
                    if i == 0:  # This is T1
                        tier_value = int(tier_entry.get() or (
                            23 if all_blank else 0))  # Default to 23 only if all are blank, otherwise 0
                    else:
                        tier_value = int(tier_entry.get() or 0)  # Default to 0 for T2, T3, T4
                    tier_values.append(tier_value)

                crop = Crop(self.next_id, color, 1, plot_id, *tier_values)
                self.crops.append(crop)
                slot_x = self.canvas.slots[offset + (self.next_id - 1) % num_crops]
                icon = DraggableIcon(self.canvas, crop, slot_x)
                self.icons.append(icon)
                self.next_id += 1

    def confirm_arrangement(self):
        # Sort icons based on their position to determine the user-defined order
        sorted_icons = sorted(self.icons, key=lambda icon: self.canvas.coords(icon.icon)[0])
        permutation = [icon.crop.id for icon in sorted_icons]  # This keeps the permutation logic intact
        icon_order = [self.canvas.itemcget(icon.text, 'text') for icon in sorted_icons]  # Get the icon labels

        t3_mult = int(self.settings_entries[0].get())  # Assuming index 0 is for T2 Mult
        t4_mult = int(self.settings_entries[1].get())  # Assuming index 1 is for T4 Mult
        vd_value = int(self.settings_entries[2].get())
        wd_value = int(self.settings_entries[3].get())
        pd_value= int(self.settings_entries[4].get())

        # Calculate the new multipliers
        max_value = max(vd_value, pd_value, wd_value)
        vivid_mult = max_value / vd_value if vd_value != 0 else 0
        primal_mult = max_value / pd_value if pd_value != 0 else 0
        wild_mult = max_value / wd_value if wd_value != 0 else 0

        average_seed_count = simulate_process(self.crops, permutation, t3_mult=t3_mult, t4_mult=t4_mult,
                                              wild_mult=wild_mult, vivid_mult=vivid_mult, primal_mult=primal_mult)
        self.display_results(average_seed_count, icon_order)  # Pass icon_order instead of permutation

    def display_results(self, results, icon_order):
        average_seed_count, variance = results
        standard_deviation = math.sqrt(variance)
        # Display the results and the icon order in a new window
        result_window = tk.Toplevel(self.master)
        result_window.title("Simulation Results")
        formatted_average = f"{average_seed_count:.1f}"
        formatted_sd = f"{standard_deviation:.1f}"
        result_label_text = f"Average Seed Count: {formatted_average} ± {formatted_sd}\nHarvest Order: {', '.join(icon_order)}"
        tk.Label(result_window, text=result_label_text).pack(padx=20, pady=20)
        result_window.geometry('+600+670')

root = tk.Tk()
custom_font = Font(family="Helvetica", size=12, weight="bold")
root.geometry('780x600+800+200')
root.title("Crop Rotation Simulator")
app = Application(master=root)
app.mainloop()
