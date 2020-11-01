import sys

from search import Problem
from utils import is_in
import itertools

class PMDAProblem(Problem):

    def value(self, state):
        pass

    M = {}  # Dictionary of medics (code associated with efficiency)
    L = {}  # Dictionary of Labels (code associated w/ tuple of 2 (max wait time, consult time))
    P = {}  # Dictionary of Patients (code associated w/ tuple of 2 (current wait time, label code))
    t = 5  # the time interval in which the evaluation and new assignments are done

    def set_initial_state(self):
        init_state = (0,) # Start at timestamp zero
        for m in self.M:
            init_state = init_state + (("empty" , self.M[m],),)

        for p in self.P:
            p_label = self.P[p][1];
            p_max_wait_time = self.L[p_label][0]
            p_current_wait_time = self.P[p][0]
            p_availabe_wait_time = int(p_max_wait_time) - int(p_current_wait_time)

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
        #NOTE! TRY TO RETURN ITERATOR INSTEAD OF LIST #
        """ Returns all the possible actions from a given state. Has in account patient
            consult time left ( If a patient has been attended for atleat his consult time,
            won't be assigned to new medics) """

        list_p = [] # List of patients tha need medical atention
        list_m = list(self.M.keys()) # List of medics that can give consults (In this case all medics)

        # Checks in the current state wich patients have consult time > 0
        for idx in range(1, self.P.__len__() +1):
            p = self.get_patient_from_state(state, idx)
            if int(p[1]) > 0: # Patient consult time (left)
                list_p.append(list(self.P.keys())[idx-1])

        # If there are more medics than patients waiting, adds empty slot to be assigned to medics with no patients
        if list_m.__len__() > list_p.__len__():
            list_p.extend((list_m.__len__() - list_p.__len__() ) * ["empty"] )

        # Gets action combinations
        num_medics = len(list_m)
        combos_m = [tuple(list_m)]
        combos_p = itertools.permutations(list_p, num_medics)
        combos_p =  [t for t in (set(tuple(i) for i in combos_p))] # Remove duplicates
        prod = itertools.product(combos_m, combos_p)

        return [tuple(zip(i[0], i[1])) for i in prod]


    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def result(self, state, action):
        """A medic can either attend or not attend a patient
                If he attends, Patient Consult time decreases by t*me.
                If he doesn't attend, Patient Waiting time increases by t."""

        new_state = (state[0] + self.t,) # timestamp constant

        # [TO DO !] ADD MEDIC NEW STATES TO CURRENT STATE -------------

        for i in range(1, self.P.__len__()+1):
            patient_state = self.get_patient_from_state(state, i)
             # patient code
            #if any(list(self.P.keys())[i] in j for j in action):
            try:
                medic_code = next(name for (name, number) in action if number == list(self.P.keys())[i-1])
                new_patient_conslt_time = float(self.get_patient_from_state(state, i)[1]) - (float(self.M[medic_code]) * self.t) # Consult time of patient decreases by (me * t)
            except: # Patient not assigned to a medic by the given action
                new_patient_remaining_time = float(self.get_patient_from_state(state, i)[0]) - self.t # Time left for the patient to be attended decreases by 't'
                continue

            # [TO DO !] ADD SAVE IN STATE [IN HERE!] -------------


        """RETURNS state"""
        pass

    # Loads a problem from a (opened) file object f (see below for format specification)
    def load(self, file_obj):
        for line in file_obj:
            line_strs = line.split()

            if line == "\n":  # ignores blank line
                continue
            elif line_strs[0] == "MD":
                self.M[line_strs[1]] = line_strs[2]
            elif line_strs[0] == "PL":
                self.L[line_strs[1]] = (line_strs[2], line_strs[3])
            elif line_strs[0] == "P":
                self.P[line_strs[1]] = (line_strs[2], line_strs[3])


if __name__ == '__main__':
    pmda = PMDAProblem(sys.argv)

    action = pmda.actions(pmda.initial)
    pmda.result(pmda.initial, action[0])
    breaksa = 1;


