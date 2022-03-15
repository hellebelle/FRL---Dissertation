from hashlib import new
from json.tool import main
from msilib.schema import Class
import os
import sys
import optparse
from sumolib import checkBinary
import numpy as np
import traci

class Q_Learning_Model:
    def __init__(self, TL_id, det_id):
        self.TL_id = TL_id
        self.det_id = det_id
        self.environment_rows = 3
        self.environment_columns = 3

        #Create a 2D numpy array to hold the current Q-values for each state and action pair: Q(s, a) 
        #The array contains 3 rows and 3 columns (to match the shape of the environment).
        #The value of each (state, action) pair is initialized to 0.
        self.q_values = np.zeros((self.environment_rows, self.environment_columns)) 

        #define actions
        #numeric action codes: 0 = green, 1 = yellow, 2 = red
        # self.actions =  [0, 1, 2]

        #Create a 2D numpy array to hold the rewards for each state. 
        #The array contains 3 rows and 3 columns (to match the shape of the environment), and each value is initialized to -100.
        # self.rewards = np.full((self.environment_rows, self.environment_columns), -100)
        # self.rewards[0,0] = 100;  self.rewards[2,2] = 100
        # # rewards[0,2] = -100; rewards[2,0] = -100
        # self.rewards[0,1] = 0
        # self.rewards[1,0] = 10; self.rewards[1,1] = 10; self.rewards[1,2] = 10
        # self.rewards[2,1] = 50
        # print(self.rewards)

        
    
    #define an epsilon greedy algorithm that will choose which action to take next (i.e., where to move next)
    def get_next_action(self, current_row_index, current_column_index, epsilon):
        #if a randomly chosen value between 0 and 1 is less than epsilon, 
        #then choose the most promising value from the Q-table for this state.
        if np.random.random() < epsilon:
            #return np.argmax(self.q_values[current_row_index, current_column_index])
            return np.argmax(self.q_values[current_row_index])
        else: #choose a random action
            return np.random.randint(3) 

    #define a function that will get the next location based on the chosen action
    def get_next_location(self):
        column_index = traci.trafficlight.getPhase(self.TL_id)

        if traci.inductionloop.getLastStepOccupancy(self.det_id) >= 80:
            row_index = 2
        elif traci.inductionloop.getLastStepOccupancy(self.det_id) >= 50 and traci.inductionloop.getLastStepOccupancy(det_id) < 80:
            row_index = 1
        else:
            row_index = 0

        return row_index, column_index

    def run(self):
        #define training parameters
        epsilon = 0.9 #the percentage of time when we should take the best action (instead of a random action)
        discount_factor = 0.9 #discount factor for future rewards
        learning_rate = 0.9 #the rate at which the agent should learn
        
        step = 0
        
        row_index, column_index = self.get_next_location()

        # reward = 0
        
        # while step < 2000:
        while traci.simulation.getMinExpectedNumber() > 0:
            num_vehicles_at_det = traci.inductionloop.getLastStepVehicleNumber(self.det_id)
            vehicles_at_det = traci.inductionloop.getLastStepVehicleIDs(self.det_id)
            # num_vehicles = traci.vehicle.getIDCount()
            # vehicles = traci.vehicle.getIDList()
            # avg_waiting_time = 0
            cummulative_waiting_time = 0
            if num_vehicles_at_det > 0:
                for i in vehicles_at_det:
                    # avg_waiting_time += traci.vehicle.getWaitingTime(i)
                    cummulative_waiting_time += traci.vehicle.getWaitingTime(i)
            
                # avg_waiting_time/=num_vehicles #avg_waiting_time of vehicle in N7
                
                occupancy = traci.inductionloop.getLastStepOccupancy(self.det_id)
                #choose which action to take (i.e., where to move next)
                action_index = self.get_next_action(row_index, column_index, epsilon)
                # print('action:', action_index)

                # if occupancy == 0: avg_waiting_time = 0 #if lane is unoccupied, waiting time on lane will be 0 (e.g while occupancy = 0,  avg_waiting_time * occupancy = 0)

                #perform the chosen action, and transition to the next state (i.e., move to the next location)
                old_row_index, old_column_index = row_index, column_index #store the old row and column indexes
                traci.trafficlight.setPhase(TL_id, action_index)
                row_index, column_index = self.get_next_location()

                #receive the reward for moving to the new state, and calculate the temporal difference
                # reward = self.rewards[row_index, column_index]

                # reward = occupancy - avg_waiting_time
                k = 2
                if cummulative_waiting_time > 0 and occupancy > 0 :
                   reward = ((k**2)*occupancy)/cummulative_waiting_time
                elif (cummulative_waiting_time > 0 and occupancy == 0):
                   reward = -k*cummulative_waiting_time
                else:
                   reward = (k**occupancy)
                print('Reward', reward)
                old_q_value = self.q_values[old_row_index, old_column_index]
                # print("Old Q-val: ", old_q_value)
                temporal_difference = reward + (discount_factor * np.max(self.q_values[row_index, column_index])) - old_q_value
                #update the Q-value for the previous state and action pair
                new_q_value = old_q_value + (learning_rate * temporal_difference)
                self.q_values[old_row_index, old_column_index] = new_q_value
                
            traci.simulationStep()
            step +=1

        # print(traci.lane.getIDList())
        # print(self.q_values)
        return self.q_values


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    # print("Success I guess")
else: 
    sys.exit("please declare environment variable 'SUMO_HOME")

# #define the shape of the environment (i.e., its states and actions)
# environment_rows = 3
# environment_columns = 3

# #Create a 2D numpy array to hold the current Q-values for each state and action pair: Q(s, a) 
# #The array contains 3 rows and 3 columns (to match the shape of the environment), as well as a third "action" dimension.
# #The "action" dimension consists of 4 layers that will allow us to keep track of the Q-values for each possible action in
# #each state (see next cell for a description of possible actions). 
# #The value of each (state, action) pair is initialized to 0.
# q_values = np.zeros((environment_rows, environment_columns))

# #define actions
# #numeric action codes: 0 = green, 1 = yellow, 2 = red
# actions = [0, 1, 2]

# #define states
# #numeric state codes: 0 = 0-49% occupancy, 1 = 50-79% occupancy, 2 = 80-100% occupancy
# states = [0, 1, 2]

#Create a 2D numpy array to hold the rewards for each state. 
#The array contains 3 rows and 3 columns (to match the shape of the environment), and each value is initialized to -100.
# rewards = np.full((environment_rows, environment_columns), -100)
# rewards[0,0] = 100;  rewards[2,2] = 100
# rewards[0,2] = -100; rewards[2,0] = -100
# rewards[0,1] = 0
# rewards[1,0] = 10; rewards[1,1] = 10; rewards[1,2] = 10
# rewards[2,1] = 50

# for row in rewards:
#     print(row)

# traffic_light_ID_list = traci.trafficlight.getIDList()
# det_list = traci.inductionloop.getIDList()

#Dictionary of Traffic Lights and corresponding detectors
TL_det_lookup = {}
TL_det_lookup['275503308#1-AddedOnRampNode'] = "myLoop_3"
TL_det_lookup['2801474636'] = "myLoop_4"
TL_det_lookup['322708970'] = "myLoop_1"
TL_det_lookup['322709881'] = "myLoop_5"
TL_det_lookup['33583130'] = "myLoop7"
TL_det_lookup['4881370732'] = "myLoop_2"
TL_det_lookup['726898959'] = "myLoop8"
TL_det_lookup['727820891'] = "myLoop9"

TL_id = '2801474636'
det_id = TL_det_lookup[TL_id]

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

    
if __name__ == "__main__":
   
    sumoBinary_gui = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
    
    traci.start([sumoBinary_gui, "-c", "N7_simulation.sumo.cfg", 
                            "--tripinfo-output", "tripinfo.xml"])

    # models = []
    # for key, value in TL_det_lookup.items():
    #     model = Q_Learning_Model(key,value)
    #     q_table = model.run()
    #     models.append(model)

#      Sample output of Q-table
#     [[ 494.72513367 -155.89262641  -39.0102926 ]
#      [ 141.45633866   35.95508736  111.38845223]
#      [ 216.91456987  176.88815662 -109.36996045]]

#after adding new rewards equation
#reward equation: reward = occupancy - avg_waiting_time 
# [[119.57628195 111.7960126   79.5049924 ]
#  [134.63198407 130.01438056 174.36390165]
#  [ 87.34932786 149.06793475 171.0526266 ]]

#  reward equation: reward = occupancy - avg_waiting_time
# [[ 5.00784271e-02  5.25138464e-02  4.97379785e-02]
#  [ 1.21460614e+02  1.28456999e+01  1.53019153e+01]
#  [-1.34759940e+01  2.12943863e+02  2.16636786e+01]]

# k = 5
# if avg_waiting_time > 0 and occupancy > 0 :
#    reward = ((k**2)*occupancy)/avg_waiting_time
# elif (occupancy < 0):
#    reward = -avg_waiting_time
# else:
#    reward = ((k**2)*occupancy)

# [[2.59509245e-02 2.46363618e-02 2.47472301e-02]
#  [6.43747523e+04 9.50520194e+02 1.00507304e+04]
#  [1.39726221e+04 1.24829310e+03 3.29424270e+04]]

# k = 2
# if avg_waiting_time > 0 and occupancy > 0 :
#     reward = ((k**2)*occupancy)/avg_waiting_time
# elif (avg_waiting_time > 0 and occupancy == 0):
#     reward = -(k * avg_waiting_time)
# else:
#     reward = (k*occupancy)

# [[-7.64730429e+00 -6.08921057e-02 -3.26192343e+00]
#  [ 2.46033331e+02  1.13448398e+02  1.16889957e+04]
#  [ 1.39984045e+03  3.46826019e+02  4.80364964e+05]]

# k = 2
# if avg_waiting_time > 0 and occupancy > 0 :
#     reward = ((k**2)*occupancy)/avg_waiting_time
# elif (avg_waiting_time > 0 and occupancy == 0):
#     reward = -(avg_waiting_time)
# else:
#     reward = (k*occupancy)

# [[1.35074488e+00 1.38317658e+00 1.34113797e+00]
#  [4.63424480e+01 8.49249446e+03 2.06800057e+03]
#  [1.50350562e+03 2.43884258e+04 6.25764064e+01]]

# if avg_waiting_time > 1 :
#     reward = occupancy/avg_waiting_time
# else:
#     reward = occupancy

# [[4.31011980e-04 4.62893250e-04 4.30326839e-04]
#  [1.69323938e+01 5.75560752e+01 3.46351569e+01]
#  [2.17714785e+02 1.91445248e+01 1.93877670e+01]]

# k = 5
# if avg_waiting_time > 0 and occupancy > 0 :
#     reward = ((k**2)*occupancy)/avg_waiting_time
# elif (avg_waiting_time > 0 and occupancy == 0):
#     reward = -avg_waiting_time
# else:
#     reward = ((k**2)*occupancy)

# [[1.84044701e-01 1.90123903e-01 2.03659049e-01]
#  [6.71046897e+01 8.47560800e+03 4.87558679e+03]
#  [6.01085943e+05 1.50306211e+04 1.64330011e+06]]
    TL_1 = Q_Learning_Model('2801474636', TL_det_lookup[TL_id])
    TL_1_Q_table = TL_1.run()
    print(TL_1.q_values)

    # run()
    # for i in models:
    #     print(i)
    traci.close()
    sys.exit()