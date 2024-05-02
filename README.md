# Crop-Rotation-Simulator

This program is designed to simulate Harvests in Path of Exile that use the Crop Rotation Keystone. 

After inputting the data for the current crops in the harvest, you can input a potential order in which they would be harvested, and the simulation will estimate the result. 

Current assumptions:
<break>
1. All Harvest Notables (other than those that affect color chances) and Crop Rotation are allocated
2. Imbued Harvest was selected on the Map Device (additional 50% chance for no-wilt and 50% chance for additional monster from T1-T3 seed)
3. The upgrade probability odds are 25%, 20%, and 5% for T1-T2, T2-T3, and T3-T4 respectively
4. T2 seeds are assigned a value of 1, T3 are assigned a value of 20, and T4 seeds are assigned a value of 100. This is based on my anecdotal observations and several baseline factors:
            a. T3 seeds not only drop larger piles of lifeforce than T2s, but they are also guaranteed to drop some
            b. T4 piles are even larger, but pack size and chance to spawn additional monsters doesn't work on bosses (though duplicate monster seems to for some reason since they do spawn double about 9% of the time).
            c. T4s can also drop sacred blossoms, which have to be accounted for at least a little bit in the estimate.
5. Vivid lifeforce is worth 2x as much as Primal or Wild, which are worth the same.
6. When the simulator is working through a proposed permutation, any crops that are simulated to wilt in a given iteration will simply be skipped over when they would have been harvested, there is no re-evaluation of the optimal route.

Insufficiencies:
1. Cannot currently estimate the true value of the opportunity to make a smart choice. Some permutations will be undervalued in the sense that they potentially offer more opportunities to divert from the planned order if the RNG heavily swings one way or the other. For example, imagine the following scenario:
                   a. There are 3 crops remaining, one Primal crop (crop 1) alone in its plot, and a plot with one Primal crop (crop 2) and one Vivid crop (crop 3).
                   b. The Tiers of Seeds are distributed in such a way that the simulation says that farming 1,2,3 or 2,1,3 will have the best results on average. 
                   c. According to the simulation, choosing to farm 1,2,3 or 2,1,3 will give the same average result, since the order the Primals are farmed in doesn't matter as long as you are committed to taking both of them before the Vivid.
                   d. However, in the real world, farming 1 first is the obvious choice because it guarantees you an opportunity to make an informed decision to potentially divert from the plan. If the first Primal crop harvested rolls very poorly compared to expectation on its upgrading of the Vivid crop, then it may be advtangeous to actually take the Vivid crop first so that it can be used to gamble on upgrading the remaining Primal crop instead. And if the first upgrade rolls very well compared to expectation, it could also be advantageous to take the Vivid crop first because it's now too juicy to risk compared to the value of upgrading it again.
                   e. By contrast, taking 2 first only gives you a meaningful choice if the Vivid crop doesn't wilt, and also makes the choice less meaningful, since instead of evaluating the potential risk/reward, you're only looking at which remaining crop has more potential to upgrade the other one.
                   f. In general, it's always best to save choices for when more information (more harvested crops) has been gathered, but the simulation cannot currently reflect this possibility since trying to get it to choose the optimal path becomes recursive and I don't know how to handle that.
2. GUI is non-intuitive and overall pretty shit.
