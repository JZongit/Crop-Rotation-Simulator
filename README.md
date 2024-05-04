# Crop-Rotation-Simulator

This program is designed to simulate Harvests in Path of Exile that use the Crop Rotation Keystone. 

The user can set values for the relative worth of T3 and T4 seeds compared to T2 seeds (T1 are assumed to be worthless).
            These default to 26 and 100 based on data I've gathered, but you may want to play aroung with them, especially if sacred lifeforce is particularly expensive/cheap. 

The user can also set values for the current prices of lifeforce to determine multipliers that will be applied to crops in the simulation. 

Once those values are set or the defaults are left in place, the user can input the current data of their sacred grove using the dropdown menus and text boxes. 
Selecting only a crop color will default that crop to the starting value of 23 T1 seeds and no higher tier seeds. 
Otherwise, fields left blank will default to 0 if any fields in that same crop are filled in. 
Selecting no color will set that crop to be empty when crops are added. 

Adding crops will create a series of labeled icons, these icons can then be arranged in the proposed order of harvesting, and pressing "simulate permutation" will generate an average seed value (with std. dev) over 10,000 iterations through that permutation. 

For the purposes of this calculation, "average seed value" assumes T2 seeds have a value of 1.

Higher average seed value will always correlate 1:1 with more expected lifeforce, as it is the baseline on which all juiciness multipliers operate, so the actual juiciness of the map/scarabs/etc. won't affect this relationship.  

Other Assumptions:
<break>
1. Crop Rotation and all Harvest Notables (other than those that affect color chances) are allocated
            
2. Imbued Harvest was selected on the Map Device (additional 50% chance for no-wilt and 50% chance for additional monster from T1-T3 seed)
   
3. The upgrade probability odds are 25%, 20%, and 5% for T1-T2, T2-T3, and T3-T4 respectively
   
4. When the simulator is working through a proposed permutation, any crops that are simulated to wilt in a given iteration will simply be skipped over when they would have been harvested, there is no re-evaluation of the optimal route.

Insufficiencies:
1. Cannot currently estimate the true value of the opportunity to make a smart choice. Some permutations will be undervalued in the sense that they potentially offer more opportunities to divert from the planned order if the RNG heavily swings one way or the other. For example, imagine the following scenario:

   a. There are 3 crops remaining, one Primal crop (crop 1) alone in its plot, and a plot with one Primal crop (crop 2) and one Vivid crop (crop 3).
   
   b. The Tiers of Seeds are distributed in such a way that the primal crops are identical, and the Vivid crop is set up so that the simulation says that farming 1,2,3 or 2,1,3 will have the best results on average 
   
   c. According to the simulation, choosing to farm 1,2,3 or 2,1,3 will give the same average result, since the order the Primals are farmed in doesn't matter as long as you are committed to taking both of them before the Vivid.
   
   d. However, in the real world, farming 1 first is the obvious choice because it guarantees you an opportunity to make an informed decision to potentially divert from the plan. If the first Primal crop harvested rolls very poorly compared to expectation on its upgrading of the Vivid crop, then it may be advtangeous to actually take the Vivid crop first so that it can be used to gamble on upgrading the remaining Primal crop instead. And if the first upgrade rolls very well compared to expectation, it could also be advantageous to take the Vivid crop first because it's now too juicy to risk compared to the value of upgrading it again.
   
   e. By contrast, taking 2 first only gives you a meaningful choice if the Vivid crop doesn't wilt, and also makes the choice less meaningful, since instead of evaluating the potential risk/reward, you're only looking at which remaining crop has more potential to upgrade the other one and so the difference in the outcomes will probably be small.

   f. A choice is more valuable if the difference between the right choice and the wrong choice is greater. 
               
   f. In general, it's always best to save valuable choices for when more information (more harvested crops) has been gathered, but the simulation cannot currently reflect this fact, since trying to get it to choose the optimal path becomes recursive and I don't know how to handle that.
   
3. GUI is non-intuitive and overall pretty shit.
