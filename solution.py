import sys
import itertools
import time
from search import Problem, Node, depth_first_graph_search, astar_search, uniform_cost_search, depth_first_tree_search

class PMDAProblem(Problem):

    def value(self, state):
        pass

    M = {}  # Dictionary of medics (code associated with efficiency)
    L = {}  # Dictionary of Labels (code associated w/ tuple of 2 (max wait time, consult time))
    P = {}  # Dictionary of Patients (code associated w/ tuple of 2 (current wait time, label code))
    t = 5   # the time interval in which the evaluation and new assignments are done
    h = None  # Problem Heuristic
    solution_node = Node(None) # Node corresponding to the solution state

    def set_initial_state(self):
        init_state = (0,) # Start at timestamp zero
        for m in self.M:
            init_state = init_state + ("empty" ,)

        for p in self.P:
            p_label = self.P[p][1];
            p_max_wait_time = self.L[p_label][0]
            p_current_wait_time = self.P[p][0]
            p_availabe_wait_time = p_max_wait_time - p_current_wait_time

            p_consult_time_left = self.L[p_label][1]
            init_state = init_state + ((p_availabe_wait_time, p_consult_time_left,),)
        return init_state

    def get_medic_from_state(self, state, medic_idx):
        if medic_idx <1 :
            raise Exception("Medic index must start at 1")
        if medic_idx > self.M.__len__():
            raise Exception("Medic index must not be greater than the number of medics")
        return state[medic_idx]

    def get_patient_from_state(self,state, patient_idx):
        if patient_idx <1 :
            raise Exception("Patient index must start at 1")
        if patient_idx > self.P.__len__():
            raise Exception("Patient index must not be greater than the number of patients")
        return state[self.M.__len__() + patient_idx]


    def __init__(self, argv):
        if argv.__len__() != 2:
            print("Invalid arguments. Pass only 1 argument")
            exit(2)
        f = open(argv[1], "r")
        self.load(f)
        super().__init__(self.set_initial_state())

    def actions(self, state):
        """ Returns all the possible actions from a given state. Has in account patient
            consult time left ( If a patient has been attended for at least his consult time,
            won't be assigned to new medics) """

        list_p = [] # List of patients tha need medical atention
        list_m = list(self.M.keys()) # List of medics that can give consults (In this case all medics)

        # Checks in the current state wich patients have consult time > 0
        for idx in range(1, self.P.__len__() +1):
            p = self.get_patient_from_state(state, idx)
            if p[1] > 0: # Patient consult time (left)
                list_p.append(list(self.P.keys())[idx-1])

        # If there are more medics than patients waiting, adds empty slot to be assigned to medics with no patients
        if list_m.__len__() > list_p.__len__():
            list_p.extend((list_m.__len__() - list_p.__len__() ) * ["empty"] )

        # Gets action combinations
        num_medics = len(list_m)
        combos_m = [tuple(list_m)]
        combos_p = itertools.permutations(list_p, num_medics)
        combos_p =  [t for t in (set(tuple(i) for i in combos_p))] # Remove duplicates
        actions = itertools.product(combos_m, combos_p)

        actions_list = [tuple(zip(i[0], i[1])) for i in actions] # List of all possible actions without filtering actions that lead to unfeasible states
        actiom_list_copy = actions_list.copy()
        # Removes all states that result in infeasible state
        for action in actiom_list_copy:
            number_critic_patients = 0  # A critic patient is a patient that has to be attended in the next state. ( Remaining waiting time = 5)

            attended_patient = [i[1] for i in action if i[1] != "empty"] # Gets codes of patients being attended
            attended_patient_idx = [list(self.P.keys()).index(code) for code in attended_patient] # Converts code to idx

            all_index = list(range(0, self.P.__len__())) # Generates a list with all indexes
            [all_index.remove(idx) for idx in attended_patient_idx] # Removes attended patient indexes from the list

            for i in all_index: # Iterate all patients that are not being attended by a medic in this action
                patient_state = self.get_patient_from_state(state,i+1)
                if patient_state[0] == 0 and patient_state[1] > 0 : # If current patient has zero minutes and not being attended
                    actions_list.remove(action)
                    break
                if patient_state[0] == self.t: # If patient remaining waiting time = t (5)
                    number_critic_patients +=1 # Increments # of critic patients

            if number_critic_patients > self.M.__len__() and action in actions_list: # If number of critic patients > number of medics -> Next state is unfeasible
                actions_list.remove(action)

        # Filtrar acções que resultam num estado inválido!
        return iter(actions_list)

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""

        for i in range(1, self.P.__len__()+1):
             if self.get_patient_from_state(state, i)[1] > 0: # Checks if atleast one patient has consult time > 0
                 return False

        return True # Goal state -> all patients were attended

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1."""
        sum = 0;
        for i in range(1, self.P.__len__()+1): # Sums the squares of all patients total waiting time
            label_code = list(self.P.values())[i-1][1]
            max_wait_time = self.L[label_code][0]
            sum += pow(max_wait_time - self.get_patient_from_state(state2, i)[0], 2) # Square of patient total waiting time

        return sum # Contemplates the total cost from the initial state until state 2

    def result(self, state, action):
        """A medic can either attend or not attend a patient
                If he attends, Patient Consult time decreases by t*me.
                If he doesn't attend, Patient Waiting time increases by t."""

        new_state = [state[0] + self.t] # timestamp constant

        # Fill the(List) state with default value for the medics
        new_state.extend(self.M.__len__() * " ")

        for i in range(1, self.P.__len__()+1):
            patient_state = self.get_patient_from_state(state, i)
             # patient code
            #if any(list(self.P.keys())[i] in j for j in action):
            try:
                medic_code = next(name for (name, number) in action if number == list(self.P.keys())[i-1])
                new_state[(list(self.M.keys()).index(medic_code) + 1)] = list(self.P.keys())[i-1] # Updates list of state w/ new medic values (patient code of medic(i) )

                new_patient_conslt_time = patient_state[1] - (self.M[medic_code] * self.t) # Consult time of patient decreases by (me * t)
                new_state.append((patient_state[0],  new_patient_conslt_time)) # Updates list of state w/ new patient values;  Patiente waiting time = previous state

            except: # Patient not assigned to a medic by the given action
                if patient_state[1] >0: # If patient consult time is greater than zero, change waiting time
                    new_patient_remaining_time = patient_state[0] - self.t # Time left for the patient to be attended decreases by 't'
                    new_state.append((new_patient_remaining_time, patient_state[1])) # Updates list of state w/ new patient values; Consult time = previous state
                else:
                    new_state.append(patient_state) # If consult time <0, doesn't change state

                continue

        for i in range(1, self.M.__len__()+1):
           if new_state[i] == ' ' : new_state[i] = "empty"


        return tuple(new_state)

    def h(self,node):
        sum = 0;
        for i in range(1, self.P.__len__()+1):
            try:
                sum +=pow((1/self.get_patient_from_state(node.state,i)[1])*50,2)
                sum +=pow((1/self.get_patient_from_state(node.state,i)[0])*50,2)
            except: continue
        return sum

    # Loads a problem from a (opened) file object f (see below for format specification)
    def load(self, file_obj):
        for line in file_obj:
            line_strs = line.split()

            if line == "\n":  # ignores blank line
                continue
            elif line_strs[0] == "MD":
                self.M[line_strs[1]] = float(line_strs[2])
            elif line_strs[0] == "PL":
                self.L[line_strs[1]] = (float(line_strs[2]), float(line_strs[3]))
            elif line_strs[0] == "P":
                self.P[line_strs[1]] = (float(line_strs[2]), line_strs[3])

    def search(self):

        #self.solution_node = uniform_cost_search(self, display=True)
        self.solution_node = astar_search(self, self.h, display=True)
        return False if self.solution_node == None else True

    def save(self, f):
        if self.solution_node == None: #If there is no solution
            f.write("Infeasible")
            return
        node = self.solution_node
        actions = self.solution_node.depth * [None]

        for i in range(self.solution_node.depth):
            actions[self.solution_node.depth - i-1] = node.action
            node = node.parent

        solution_actions = self.M.__len__() * [actions.__len__() * [None]] # List of actione that lead to a solution state

        for j in range(self.M.__len__()):
            solution_actions[j] = [x[j][1] for x in actions]

        for i in range(self.M.__len__()):
            solution_actions[i].insert(0,  list(self.M.keys())[i])
            solution_actions[i].insert(0, "MD")

        for item in solution_actions:
            f.write("%s\n" % str(item).replace("[","").replace("]","").replace("'","").replace(",",""))

if __name__ == '__main__':
    pmda = PMDAProblem(sys.argv) # Initiates the PMDAProblem object

    start = time.time()
    pmda.search() # Searches for a solution
    print("\n---INFO---\nTime of execution:", round(time.time()-start, 2) ,"s" )
    f = open("solution.txt", "w")
    pmda.save(f)    # Saves the actions that lead to the solution obtained
    try: print("Path Cost:", pmda.solution_node.path_cost)
    except: print("Infeasible")


