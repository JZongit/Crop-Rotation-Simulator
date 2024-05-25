import multiprocessing
import random
import pandas as pd
import time
from copy import deepcopy
from itertools import product

#Define a Crop and all of its in-game attributes, plus some special ones used for logical sorting/data storage
class Crop:
    def __init__(self, id, harvestable, plot_id, tier_one, tier_two, tier_three, tier_four, weights=None, neighbor=None):
        self.id = id
        self.harvestable = harvestable #Boolean tag indicating that a crop has yet to be harvested. Set to 0 after harvesting or with 40% odds after other crop in same plot is harvested
        self.plot_id = plot_id #Indicates which plot the crop is in, not used that much because of the "neighbor" attribute but worth having as a potential label 
        self.tier_one = tier_one #The count of Tier 1 seeds in the crop, starts at 23
        self.tier_two = tier_two #The count of Tier 2 seeds in the crop, starts at 0
        self.tier_three = tier_three #The count of Tier 3 seeds in the crop, starts at 0
        self.tier_four = tier_four #The count of Tier 4 seeds in the crop, starts at 0
        self.neighbor = neighbor #Hardcoded 1:1 matching assignment for crops in the same plot, makes functions run faster by allowing easy access to neighboring crop's stats. 
        self.upgrade_count = 0  #Tracks how many upgrades a crop has received so far, used in reordering logic to determine if it is even worth deciding between two crops of the same color. Also for data gathering. 
        self.initial_state = (harvestable, tier_one, tier_two, tier_three, tier_four, 0) #Saves the initial state of the crop so that it can be reset for each new grove. 
        self.colors = ['Yellow', 'Blue', 'Purple'] #Duh
        self.weights = weights #Used to set the weight of each color, program iterates through all 52 "unique" (assuming purple and blue are the same value) distributions of Atlas Points so they can be compared. 
        self.color = random.choices(self.colors, weights=self.weights, k=1)[0] #The internal function that randomizes the color of the crop according to the weights, used at the start of each new grove. 
        self.priority = None  #A dynamically assigned label used by the sorting algorithm to determine the inital planned harvesting order for each grove. 

    def reset(self): 
        self.harvestable, self.tier_one, self.tier_two, self.tier_three, self.tier_four, self.upgrade_count = self.initial_state
        self.color = random.choices(self.colors, weights=self.weights, k=1)[0] #Function that is called to reset crops to be harvestable, have 23/0/0/0 tier counts, and randomize their color. 

    def __repr__(self):
        neighbor_id = self.neighbor.id if self.neighbor else 'None'
        return (f"Crop(ID={self.id}, Color={self.color}, Harvestable={self.harvestable}, "
                f"PlotID={self.plot_id}, TierOne={self.tier_one}, TierTwo={self.tier_two}, "
                f"TierThree={self.tier_three}, TierFour={self.tier_four}, NeighborID={neighbor_id}, "
                f"UpgradeCount={self.upgrade_count}, Priority={self.priority})") #Debugging Function

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
    } #Map that categorizes crops, based on their neighbors color, into their strategically relevant groups: Double Blues, Purple/Blue Hybrids, Blue/Yellow Hybrids, Double Yellows, Double Purples, and Purple/Yellow Hybrids. 
    
    for crop in crops_dict.values():
        if crop.id % 2 == 1:
            pair = (crop.color, crop.neighbor.color)
            priority = priority_map.get(pair)
            if priority:
                crop.priority = priority
                crop.neighbor.priority = priority #Function that assigns priority as quickly as possible by labeling each odd numbered crop and it's neighbor at the same time. 

def choose_crops_by_weight(): 
    options = [6, 8, 10]
    weights = [1, 2, 1]
    chosen_count = random.choices(options, weights=weights, k=1)[0]
    return chosen_count #Function that randomizes the number of plots in the harvest. Set to be 25% 3-plot, 50% 4-plot, and 25% 5-plot. Based on 50% chance of 3 or 4 initially, and 50% chance for an additional plot. 

def generate_color_based_permutation(crops_dict):
    num_crops_to_include = choose_crops_by_weight()
    included_crops = [crop for crop in crops_dict.values() if crop.id <= num_crops_to_include] #Shaves list of 10 hard coded crops down to whatever is relevant for the current grove based on how many plots it has. 

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
    yellow_doubles = [] #Establishing empty sets for the sorting process 

    for crop in included_crops:
        if crop.color == 'Blue':
            blue_crops.append(crop.id)
        elif crop.color == 'Purple':
            purple_crops.append(crop.id)
        elif crop.color == 'Yellow':
            yellow_crops.append(crop.id) #Populates color groups for counting and data gathering 

    primary_color, secondary_color = ('Blue', 'Purple') if len(blue_crops) >= len(purple_crops) else ('Purple', 'Blue')
    #Determines if Blue or Purple is the more common non-yellow color, because simulations have shown that harvesting the more common color first has better yields. Defaults to Purple in a tie. 

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
                yellow_doubles.append(crop.id) #Populates the priority groupings. There are 8 strategically relevant groupings based on what can happen when a crop is harvested.
                '''
                Categories are divided based on more or less common non-yellow color, having a neighbor of the same color vs. having a non-yellow neighbor vs having a yellow neighbor, and/or being yellow. 
                Harvesting any one of the crops in one of these groups will always be functionally equivalent to harvesting another member of the group. 
                The same colors will be upgraded, and the same color crop is at risk of being destroyed, and the group as a whole has the same potential value to upgrade or be upgraded. 
                Crops of the most common non-yellow color in a plot with a crop of the same color are called primary doubles, crops of the most common non-yellow color sharing a plot with the other non-yellow color are called primary hybrids. 
                Crops of the most common non-yellow color in a plot with a yellow crop are called primary dangers, because they represent a possible decision point where it may be worth it to harvest the yellow crop first if it is juicy enough.
                Ditto for the crops of the least common non-yellow color. 
                For yellow crops, they are separated into those that might be risked at some point because they are in a hybrid plot, and doubles that represent a very easy decision where you just take the best one. 
                '''
                

    ordered_ids = (
        primary_doubles + primary_hybrids + primary_dangers +
        secondary_doubles + secondary_hybrids + secondary_dangers +
        yellow_hybrids + yellow_doubles
    ) #put the categorized crops in the strategically optimal order. 
    '''
    I tested all permutations of this, combined with everything from the most advanced re-ordering logic I could think of to yolo-sending it every time with no regard for EV,
    and with every weight setting, in every remotely feasible economic climate (vivid being worth anywhere from 1.5 to 3.0 times the others)...  
    And through all of that, this initial order always outperformed any other option. Not always by a huge margin, but it's just the right way to do it as far as I can tell. 
    It's so good, that even if you intentionally make the wrong (negative EV) reordering decisions whenever you are deciding to risk a yellow crop or not, it's only about 10% worse than making no-decisions and always risking it, and 20% worse than making the right decisions.
    '''

    return ordered_ids, yellow_crops
    
def simulate_process_single_iteration(crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3):
    #This is the meat of the simulation, the process that collects the randomly generated grove, and simulates harvesting each crop according to the initial order and any reordering decisions. 
    for crop in crops_dict.values():
        crop.reset()
    prioritization_process(crops_dict)
    ordered_ids, yellow_crops = generate_color_based_permutation(crops_dict)
    
    yellow_harvestable_crops = [
        crop_id for crop_id in yellow_crops if crops_dict[crop_id].harvestable == 1
    ] #Makes a list of harvestable yellow crops, because this can be used as a trigger for the reordering logic. 
    #There are extremely few and very unlikely scenarios where not risking a yellow plot is the right decision if there are at least 3 total remaining. 
    #The EV calculations are very computationally heavy at that point, and the difference between the right and wrong decision is almost always marginal at best, so it was decided to just send it when there are at least 3 yellows. 

    seed_count = 0 #resets the value extracted from the grove to 0
    index = 0 #sets function to begining of initial harvest order. 

    while index < len(ordered_ids):
        crop_id = ordered_ids[index]
        current_crop = crops_dict.get(crop_id, None) #Singles out the crop being harvested 

        if current_crop and current_crop.harvestable:
            current_crop.harvestable = 0
            if current_crop.color == 'Yellow' and current_crop.id in yellow_harvestable_crops:
                yellow_harvestable_crops.remove(current_crop.id) #When the crop is harvested, it's marked toggled so that it can't be harvested or upgraded any more, and if it was yellow it is removed from the list of yellows remaining. 
               
            if current_crop.neighbor.harvestable == 1 and random.random() < 0.4:
                current_crop.neighbor.harvestable = 0
                if current_crop.neighbor.color == 'Yellow' and current_crop.neighbor.id in yellow_harvestable_crops:
                    yellow_harvestable_crops.remove(current_crop.neighbor.id) #The crop's neighbor is given a 40% chance of also being toggled off, and removed from the yellow list if appropriate. 
                    
            addition = current_crop.tier_two + t3_mult * current_crop.tier_three + t4_mult * current_crop.tier_four
            if current_crop.color == 'Yellow':
                addition *= vivid_mult
            elif current_crop.color == 'Blue':
                addition *= primal_mult
            elif current_crop.color == 'Purple':
                addition *= wild_mult
            seed_count += addition 
            '''
            This is the step that adds the current "seed value" of the crop to the total. 
            This is a semi-arbitrary unit where T2 seeds are given a value of 1, T3 seeds a value of 25, and T4 seeds a value of 100.
            These relative values are based on my best estimates from data I gathered in my own harvesting. 
            I am much more confident in the T2/T3 ratio than the T3/T4 ratio because of the different behaviors of T4 seeds compared to the others. 
            T4 seeds drop piles of lifeforce about 5x the size of T3 seeds, but they don't benefit from pack size, or the 60% chance to spawn an additional monster.
            However, they also drop Sacred Blossoms, whose droprate is estimated at best and whose value can vary. 
            Thankfully, T4 seeds occur infrequently enough that this number doesn't change the outcomes of which strategies are superior until it gets completely crazy (over 1000).  
            T1 seeds are assumed to have no value because they contribute such a small percentage to the grand total that they would just clog up the math. 
            Yellow crops are then given their assigned multiplier (default 2.5) 
            Seed value was chosen as the unit over estimated lifeforce, because map juice will act as a multiplier on it to determine true life force gains. 
            There is no way to get more lifeforce from less seed value with the same amount of juice, so it serves as the best unit for comparison of harvesting strategies.
            '''

            for other_crop in [c for c in crops_dict.values() if c.harvestable == 1 and c.color != current_crop.color]:
                other_crop.upgrade_count += 1

                T3Success = sum(random.random() < p1 for _ in range(other_crop.tier_three))
                other_crop.tier_four += T3Success

                T2Success = sum(random.random() < p2 for _ in range(other_crop.tier_two))
                other_crop.tier_three += T2Success - T3Success

                T1Success = sum(random.random() < p3 for _ in range(other_crop.tier_one))
                other_crop.tier_two += T1Success - T2Success

                other_crop.tier_one -= T1Success
                #Simulated upgrade process that rolls for each seed in each crop independently and adjusts the counts accordingly. 

        if len(ordered_ids) - 1 > index:
            next_cropid = ordered_ids[index + 1]
            next_crop = crops_dict.get(next_cropid, None) #This is the beginning of the "decision block" that possibly alters the harvesting order, it is only triggered when there is at least one crop left.

            if next_crop.neighbor.harvestable == 1 and next_crop.neighbor.color == 'Yellow' and next_crop.color != 'Yellow':
                #Checks if a yellow crop is potentially in danger if the current order is followed and a non-yellow crop is harvested next. 
                if next_crop.color == 'Blue':
                    relevant_priority = 'BYH'
                elif next_crop.color == 'Purple':
                    relevant_priority = 'PYH'
                else:
                    relevant_priority = None #Prepares variables for checking other options that may put a less valuable yellow crop at risk. 

                if relevant_priority:
                    matching_harvestable_hybrids = [
                        crop_id for crop_id in yellow_harvestable_crops 
                        if ordered_ids.index(crop_id) > index and 
                        crops_dict[crop_id].priority == relevant_priority and
                        crops_dict[crop_id].neighbor.harvestable == 1
                    ] # Finds other crops of the same color that are also next to yellow crops

                    if matching_harvestable_hybrids:
                        hybrid_values = {
                            crop_id: crops_dict[crop_id].tier_two + t3_mult * crops_dict[crop_id].tier_three + t4_mult * crops_dict[crop_id].tier_four
                            for crop_id in matching_harvestable_hybrids
                        } # If there is another option, calculates the current juiciness of each neighboring yellow. 

                
                        crop_with_least_value = min(hybrid_values, key=hybrid_values.get)
                        neighbor_crop = crops_dict[crop_with_least_value].neighbor
                        # Singles out the less juicy one and identifies its non-yellow neighbor
                        

                        
                        ordered_ids.remove(neighbor_crop.id)
                        ordered_ids.insert(index + 1, neighbor_crop.id)
                        # Changes the order so the non-yellow next to the less juicy yellow is taken first. This is done because upgrades have an accelerative quality
                        #Therefore, deferring the decision about risking the juicier crop until more randomness has resolved is beneficial. 

                       
                        next_cropid = ordered_ids[index + 1]
                        next_crop = crops_dict.get(next_cropid, None) 
                         # Redefine next_crop after changing the order because more reordering is still possible if the less juicy yellow crop is still too juicy to risk. 
                        

                harvestable_yellows = len([
                    crop_id for crop_id in yellow_harvestable_crops if ordered_ids.index(crop_id) > index
                ]) #Counts harvestable yellow crops remaining in the harvest order

                if harvestable_yellows >= 3:
                    pass #As explained above, if there are more than 3 yellows that could be upgraded, it's almost always worth the risk. 
                elif harvestable_yellows == 1:
                    if ((next_crop.neighbor.tier_two * .12) - (next_crop.neighbor.tier_three * .28) - (next_crop.neighbor.tier_four * 1.6)) <= 0:
                        ordered_ids.remove(next_crop.neighbor.id)
                        ordered_ids.insert(index + 1, next_crop.neighbor.id) #EV calculation for situation with only one yellow crop remaining and the decision is to harvest it or its neighbor. 
                elif harvestable_yellows == 2:   
                    outside_tier_two_count = sum(crops_dict[crop_id].tier_two for crop_id in yellow_harvestable_crops if crop_id != next_crop.neighbor.id)
                    outside_tier_three_count = sum(crops_dict[crop_id].tier_three for crop_id in yellow_harvestable_crops if crop_id != next_crop.neighbor.id)
                    if ((next_crop.neighbor.tier_two * .12) - (next_crop.neighbor.tier_three * .28) - (next_crop.neighbor.tier_four * 1.6) + (outside_tier_two_count * .08) + (outside_tier_three_count * .08)) <= 0:
                        ordered_ids.remove(next_crop.neighbor.id)
                        ordered_ids.insert(index + 1, next_crop.neighbor.id) #EV calculation for situation with only two yellow crops remaining and one might be put at risk.  
            
            if next_crop.neighbor.harvestable == 1 and next_crop.neighbor.color == next_crop.color and next_crop.upgrade_count >= 2:
                if (next_crop.tier_three + (next_crop.tier_four * 4)) < (next_crop.neighbor.tier_three + (next_crop.neighbor.tier_four * 4)):
                    ordered_ids.remove(next_crop.neighbor.id)
                    ordered_ids.insert(index + 1, next_crop.neighbor.id) # If the next crop in the order and its neighbor are the same color, moves the juicier one to the front. 
                            
        index += 1  #increments index to proceed with next harvesting

    return seed_count


def worker(params):
    #Parallel threading process, I barely understand what's going on here, I just know that the results are the same with or without it, but without it they take 30 times longer to get. 
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

    return aggregated_results #Puts it all together at the end

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
    
    return filtered_weights #Function that generates the resulting weights from all possible unique permutations of atlas points
    #At least one color has to be 45% reduced, and then it only kept half of the trees where if purple and blue were swapped they'd be the same. 

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
    } #Hardcoded dictionary of 10 crops that can be copied, passed to each multithreaded process, and then randomized as necessary.  

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
    #Hardcoded neighbor relationships for easy processing in the decision making and ordering functions

    # Generate weight combinations
    weight_combinations = generate_and_filter_weights()

    # Simulation parameters
    t3_mult = 25 #Point value of T3 Seeds (T2 = 1)
    t4_mult = 100 #Point value of T4 Seeds
    vivid_mult = 2.5 #Point multiplier for yellow crops
    primal_mult = 1 #Potential point multiplier for blue crops
    wild_mult = 1 #Potential point multiplier for blue crops
    p1 = .05 # Probability that a T3 plant will upgrade to a T4 plant when the crop is upgraded, taken from Prohibited Library Discord 
    p2 = .2 # Probability that a T2 plant will upgrade to a T3 plant when the crop is upgraded, ditto
    p3 = .25 # Probability that a T1 plant will upgrade to a T2 plant when the crop is upgraded, ditto
    total_iterations = 1000000  # Set to the desired number of iterations per weight combination
    num_parallel_processes = 32

    results = run_parallel_simulation(
        crops_dict, t3_mult, t4_mult, vivid_mult, primal_mult, wild_mult, p1, p2, p3, total_iterations, num_parallel_processes, weight_combinations)

    df = pd.DataFrame(results)
    print(df.to_csv(index=False, lineterminator='\n')) #Prints results as a CSV for easy copy/paste into google sheets. 

    # Record the end time
    end_time = time.time()

# Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(vivid_mult)

# Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")
