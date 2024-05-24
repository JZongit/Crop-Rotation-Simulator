import multiprocessing
import random
import pandas as pd
import time
from copy import deepcopy
from itertools import product

# Remove DEBUG mode for pure efficiency
# DEBUG = False

class Crop:
    def __init__(self, id, harvestable, plot_id, tier_one, tier_two, tier_three, tier_four, weights=None, neighbor=None):
        self.id = id
        self.harvestable = harvestable
        self.plot_id = plot_id
        self.tier_one = tier_one
        self.tier_two = tier_two
        self.tier_three = tier_three
        self.tier_four = tier_four
        self.neighbor = neighbor
        self.upgrade_count = 0  
        self.initial_state = (harvestable, tier_one, tier_two, tier_three, tier_four, 0)
        self.colors = ['Yellow', 'Blue', 'Purple']
        self.weights = weights if weights else [.65, .65, .55]
        self.color = random.choices(self.colors, weights=self.weights, k=1)[0]
        self.priority = None  

    def reset(self):
        self.harvestable, self.tier_one, self.tier_two, self.tier_three, self.tier_four, self.upgrade_count = self.initial_state
        self.color = random.choices(self.colors, weights=self.weights, k=1)[0]

    def __repr__(self):
        neighbor_id = self.neighbor.id if self.neighbor else 'None'
        return (f"Crop(ID={self.id}, Color={self.color}, Harvestable={self.harvestable}, "
                f"PlotID={self.plot_id}, TierOne={self.tier_one}, TierTwo={self.tier_two}, "
                f"TierThree={self.tier_three}, TierFour={self.tier_four}, NeighborID={neighbor_id}, "
                f"UpgradeCount={self.upgrade_count}, Priority={self.priority})")

def prioritization_process(crops_dict):
    priority_map = {
        ('Blue', 'Blue'): 'DB',
        ('Blue', 'Purple'): 'PBH',
        ('Blue', 'Yellow'): 'BYH',
        ('Yellow', 'Yellow'): 'DY',
        ('Yellow', 'Purple'): 'PYH',
        ('Yellow', 'Blue'): 'BYH',
        ('Purple', 'Purple'): 'DP',
        ('Purple', 'Yellow'): 'PYH',
        ('Purple', 'Blue'): 'PBH'
    }
    
    for crop in crops_dict.values():
        if crop.id % 2 == 1:
            pair = (crop.color, crop.neighbor.color)
            priority = priority_map.get(pair)
            if priority:
                crop.priority = priority
                crop.neighbor.priority = priority

def choose_crops_by_weight():
    options = [6, 8, 10]
    weights = [1, 2, 1]
    chosen_count = random.choices(options, weights=weights, k=1)[0]
    return chosen_count

def generate_color_based_permutation(crops_dict):
    num_crops_to_include = choose_crops_by_weight()
    included_crops = [crop for crop in crops_dict.values() if crop.id <= num_crops_to_include]

    blue_crops = []
    purple_crops = []
    yellow_crops = []

    primary_doubles = []
    primary_hybrids = []
    primary_dangers = []
    secondary_doubles = []
    secondary_hybrids = []
    secondary_dangers = []
    yellow_hybrids = []
    yellow_doubles = []

    for crop in included_crops:
        if crop.color == 'Blue':
            blue_crops.append(crop.id)
        elif crop.color == 'Purple':
            purple_crops.append(crop.id)
        elif crop.color == 'Yellow':
            yellow_crops.append(crop.id)

    primary_color, secondary_color = ('Blue', 'Purple') if len(blue_crops) >= len(purple_crops) else ('Purple', 'Blue')

    for crop in included_crops:
        if crop.color == primary_color:
            if crop.priority in ['DP', 'DB']:
                primary_doubles.append(crop.id)
            elif crop.priority == 'PBH':
                primary_hybrids.append(crop.id)
            elif crop.priority in ['PYH', 'BYH']:
                primary_dangers.append(crop.id)
        elif crop.color == secondary_color:
            if crop.priority in ['DP', 'DB']:
                secondary_doubles.append(crop.id)
            elif crop.priority == 'PBH':
                secondary_hybrids.append(crop.id)
            elif crop.priority in ['PYH', 'BYH']:
                secondary_dangers.append(crop.id)
        elif crop.color == 'Yellow':
            if crop.priority in ['PYH', 'BYH']:
                yellow_hybrids.append(crop.id)
            elif crop.priority == 'DY':
                yellow_doubles.append(crop.id)
                

    ordered_ids = (
        primary_doubles + primary_hybrids + primary_dangers +
        secondary_doubles + secondary_hybrids + secondary_dangers +
        yellow_hybrids + yellow_doubles
    )

    return ordered_ids, yellow_crops
def simulate_process_single_iteration(crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3):
    for crop in crops_dict.values():
        crop.reset()
    prioritization_process(crops_dict)
    ordered_ids, yellow_crops = generate_color_based_permutation(crops_dict)
    yellow_harvestable_crops = [
        crop_id for crop_id in yellow_crops if crops_dict[crop_id].harvestable == 1
    ]

    seed_count = 0
    index = 0

    while index < len(ordered_ids):
        crop_id = ordered_ids[index]
        current_crop = crops_dict.get(crop_id, None)

        if current_crop and current_crop.harvestable:
            current_crop.harvestable = 0
            if current_crop.color == 'Yellow' and current_crop.id in yellow_harvestable_crops:
                yellow_harvestable_crops.remove(current_crop.id)
               
            if current_crop.neighbor.harvestable == 1 and random.random() < 0.4:
                current_crop.neighbor.harvestable = 0
                if current_crop.neighbor.color == 'Yellow' and current_crop.neighbor.id in yellow_harvestable_crops:
                    yellow_harvestable_crops.remove(current_crop.neighbor.id)
                    
            addition = current_crop.tier_two + t3_mult * current_crop.tier_three + t4_mult * current_crop.tier_four
            if current_crop.color == 'Yellow':
                addition *= vivid_mult
            elif current_crop.color == 'Blue':
                addition *= primal_mult
            elif current_crop.color == 'Purple':
                addition *= wild_mult
            seed_count += addition

            for other_crop in [c for c in crops_dict.values() if c.harvestable == 1 and c.color != current_crop.color]:
                other_crop.upgrade_count += 1

                T3Success = sum(random.random() < p1 for _ in range(other_crop.tier_three))
                other_crop.tier_four += T3Success

                T2Success = sum(random.random() < p2 for _ in range(other_crop.tier_two))
                other_crop.tier_three += T2Success - T3Success

                T1Success = sum(random.random() < p3 for _ in range(other_crop.tier_one))
                other_crop.tier_two += T1Success - T2Success

                other_crop.tier_one -= T1Success

        if len(ordered_ids) - 1 > index:
            next_cropid = ordered_ids[index + 1]
            next_crop = crops_dict.get(next_cropid, None)

            if next_crop.neighbor.harvestable == 1 and next_crop.neighbor.color == 'Yellow' and next_crop.color != 'Yellow':
                
                if next_crop.color == 'Blue':
                    relevant_priority = 'BYH'
                elif next_crop.color == 'Purple':
                    relevant_priority = 'PYH'
                else:
                    relevant_priority = None

                if relevant_priority:
                    matching_harvestable_hybrids = [
                        crop_id for crop_id in yellow_harvestable_crops 
                        if ordered_ids.index(crop_id) > index and 
                        crops_dict[crop_id].priority == relevant_priority and
                        crops_dict[crop_id].neighbor.harvestable == 1
                    ]

                    if matching_harvestable_hybrids:
                        # Calculate the current seed values for these crops
                        hybrid_values = {
                            crop_id: crops_dict[crop_id].tier_two + t3_mult * crops_dict[crop_id].tier_three + t4_mult * crops_dict[crop_id].tier_four
                            for crop_id in matching_harvestable_hybrids
                        }

                        # Find the crop with the least seed value
                        crop_with_least_value = max(hybrid_values, key=hybrid_values.get)
                        neighbor_crop = crops_dict[crop_with_least_value].neighbor

                        # Move its neighbor to be next in the list of ordered_ids
                        ordered_ids.remove(neighbor_crop.id)
                        ordered_ids.insert(index + 1, neighbor_crop.id)

                        # Redefine next_crop after changing the order
                        next_cropid = ordered_ids[index + 1]
                        next_crop = crops_dict.get(next_cropid, None)
                        

                harvestable_yellows = len([
                    crop_id for crop_id in yellow_harvestable_crops if ordered_ids.index(crop_id) > index
                ])

                if harvestable_yellows >= 3:
                    pass
                elif harvestable_yellows == 1:
                    if ((next_crop.neighbor.tier_two * .12) - (next_crop.neighbor.tier_three * .28) - (next_crop.neighbor.tier_four * 1.6)) <= 0:
                        ordered_ids.remove(next_crop.neighbor.id)
                        ordered_ids.insert(index + 1, next_crop.neighbor.id)
                elif harvestable_yellows == 2:   
                    outside_tier_two_count = sum(crops_dict[crop_id].tier_two for crop_id in yellow_harvestable_crops if crop_id != next_crop.neighbor.id)
                    outside_tier_three_count = sum(crops_dict[crop_id].tier_three for crop_id in yellow_harvestable_crops if crop_id != next_crop.neighbor.id)
                    if ((next_crop.neighbor.tier_two * .12) - (next_crop.neighbor.tier_three * .28) - (next_crop.neighbor.tier_four * 1.6) + (outside_tier_two_count * .08) + (outside_tier_three_count * .08)) <= 0:
                        ordered_ids.remove(next_crop.neighbor.id)
                        ordered_ids.insert(index + 1, next_crop.neighbor.id)
            
            if next_crop.neighbor.harvestable == 1 and next_crop.neighbor.color == next_crop.color and next_crop.upgrade_count >= 2:
                if (next_crop.tier_three + (next_crop.tier_four * 4)) < (next_crop.neighbor.tier_three + (next_crop.neighbor.tier_four * 4)):
                    ordered_ids.remove(next_crop.neighbor.id)
                    ordered_ids.insert(index + 1, next_crop.neighbor.id)
                            
        index += 1  

    return seed_count


def worker(params):
    initial_crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3, iterations, weights = params
    crops_dict = deepcopy(initial_crops_dict)
    for crop in crops_dict.values():
        crop.weights = weights  # Assign the weights for this worker

    total_seed_count = 0

    for _ in range(iterations):
        seed_count = simulate_process_single_iteration(crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3)
        total_seed_count += seed_count
        
    return total_seed_count, weights

def run_parallel_simulation(initial_crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3, total_iterations, num_parallel_processes, weight_combinations):
    # Set iterations_per_process to a fixed value
    iterations_per_process = total_iterations
    all_params = [(initial_crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3, iterations_per_process, weights) for weights in weight_combinations]

    with multiprocessing.Pool(processes=num_parallel_processes) as pool:
        results = pool.map(worker, all_params)

    # Aggregate results
    aggregated_results = []
    for total_seed_count, weights in results:
        average_seed_count = total_seed_count / iterations_per_process
        aggregated_results.append({
            "Yellow Weight": weights[0],
            "Blue Weight": weights[1],
            "Purple Weight": weights[2],
            "Average Seed Count": round(average_seed_count, 2)
        })

    return aggregated_results

def generate_and_filter_weights():
    weight_values = [.55, .65, .75, .8, .9, 1]
    seen = set()
    filtered_weights = []

    for perm in product(weight_values, repeat=3):
        if .55 in perm:
            swapped = (perm[0], perm[2], perm[1])
            if perm not in seen and swapped not in seen:
                filtered_weights.append(perm)
                seen.add(perm)
    
    return filtered_weights

if __name__ == '__main__':
    start_time = time.time() 
    crops_dict = {
        1: Crop(id=1, harvestable=1, plot_id='A', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        2: Crop(id=2, harvestable=1, plot_id='A', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        3: Crop(id=3, harvestable=1, plot_id='B', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        4: Crop(id=4, harvestable=1, plot_id='B', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        5: Crop(id=5, harvestable=1, plot_id='C', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        6: Crop(id=6, harvestable=1, plot_id='C', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        7: Crop(id=7, harvestable=1, plot_id='D', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        8: Crop(id=8, harvestable=1, plot_id='D', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        9: Crop(id=9, harvestable=1, plot_id='E', tier_one=23, tier_two=0, tier_three=0, tier_four=0),
        10: Crop(id=10, harvestable=1, plot_id='E', tier_one=23, tier_two=0, tier_three=0, tier_four=0)
    }

    crops_dict[1].neighbor = crops_dict[2]
    crops_dict[2].neighbor = crops_dict[1]
    crops_dict[3].neighbor = crops_dict[4]
    crops_dict[4].neighbor = crops_dict[3]
    crops_dict[5].neighbor = crops_dict[6]
    crops_dict[6].neighbor = crops_dict[5]
    crops_dict[7].neighbor = crops_dict[8]
    crops_dict[8].neighbor = crops_dict[7]
    crops_dict[9].neighbor = crops_dict[10]
    crops_dict[10].neighbor = crops_dict[9]

    # Generate weight combinations
    weight_combinations = generate_and_filter_weights()

    # Simulation parameters
    t3_mult = 25
    t4_mult = 100
    vivid_mult = 2.5
    primal_mult = 1
    wild_mult = 1
    p1 = .05
    p2 = .2
    p3 = .25
    total_iterations = 1000000  # Set to the desired number of iterations per weight combination
    num_parallel_processes = 32

    results = run_parallel_simulation(
        crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3, total_iterations, num_parallel_processes, weight_combinations)

    df = pd.DataFrame(results)
    print(df.to_csv(index=False, lineterminator='\n'))

    # Record the end time
    end_time = time.time()

# Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(vivid_mult)

# Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")
