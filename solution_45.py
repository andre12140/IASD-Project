### Template ###
import sys
import itertools

from search import Problem, Node, depth_first_graph_search, astar_search, uniform_cost_search, depth_first_tree_search, best_first_graph_search
from operator import itemgetter

import datetime


class PDMAProblem(Problem):

    def __init__(self):
        super().__init__(None)
        self.M = {}  # Dictionary of medics (code associated with efficiency)
        # Dictionary of Labels (code associated w/ tuple of 2 (max wait time, consult time))
        self.L = {}
        # Dictionary of Patients (code associated w/ tuple of 2 (current wait time, label code))
        self.P = {}
        self.t = 5  # the time interval in which the evaluation and new assignments are done
        # List of lists of medics that have the same efficiency (Mc)
        self.equivalent_M = []

        # Node corresponding to the solution state
        self.solution_node = Node(None)

    def set_initial_state(self):
        init_state = (0,)  # Start at timestamp zero

        init_state = init_state + (("empty",) * self.M.__len__())

        for p in self.P:
            p_label = self.P[p][1]
            p_max_wait_time = self.L[p_label][0]
            p_current_wait_time = self.P[p][0]
            p_availabe_wait_time = p_max_wait_time - p_current_wait_time

            p_consult_time_left = self.L[p_label][1]
            init_state = init_state + \
                ((p_availabe_wait_time, p_consult_time_left,),)
        return init_state

    def get_medic_from_state(self, state, medic_idx):
        if medic_idx < 1:
            raise Exception("Medic index must start at 1")
        if medic_idx > self.M.__len__():
            raise Exception(
                "Medic index must not be greater than the number of medics")
        return state[medic_idx]

    def get_patient_from_state(self, state, patient_idx):
        if patient_idx < 1:
            raise Exception("Patient index must start at 1")
        if patient_idx > self.P.__len__():
            raise Exception(
                "Patient index must not be greater than the number of patients")
        return state[self.M.__len__() + patient_idx]

    def get_patient_result(self, action, state):

        new_state = []

        for i in range(1, self.P.__len__() + 1):
            patient_state = self.get_patient_from_state(state, i)
            # patient code
            # if any(list(self.P.keys())[i] in j for j in action):
            try:
                medic_code = next(
                    name for (name, number) in action if number == list(self.P.keys())[i - 1])

                new_patient_conslt_time = patient_state[1] - (
                    self.M[medic_code] * self.t)  # Consult time of patient decreases by (me * t)
                new_state.append((patient_state[0],
                                  new_patient_conslt_time))  # Updates list of state w/ new patient values;  Patiente waiting time = previous state

            except:  # Patient not assigned to a medic by the given action
                # If patient consult time is greater than zero, change waiting time
                if patient_state[1] > 0:
                    new_patient_remaining_time = patient_state[
                        0] - self.t  # Time left for the patient to be attended decreases by 't'
                    new_state.append((new_patient_remaining_time, patient_state[
                        1]))  # Updates list of state w/ new patient values; Consult time = previous state
                else:
                    # If consult time <0, doesn't change state
                    new_state.append(patient_state)
                continue

        return list(new_state)

    def actions(self, state):
        """ Returns all the possible actions from a given state. Has in account patient
            consult time left ( If a patient has been attended for at least his consult time,
            won't be assigned to new medics) """

        """a = datetime.datetime.now()"""

        list_p = []  # List of patients tha need medical atention
        # List of medics that can give consults (In this case all medics)
        list_m = list(self.M.keys())

        # Checks in the current state wich patients have consult time > 0
        for idx in range(1, self.P.__len__() + 1):
            p = self.get_patient_from_state(state, idx)
            if p[1] > 0:  # Patient consult time (left)
                list_p.append(list(self.P.keys())[idx - 1])

        # If there are more medics than patients waiting, adds empty slot to be assigned to medics with no patients
        if list_m.__len__() > list_p.__len__():
            list_p.extend((list_m.__len__() - list_p.__len__()) * ["empty"])
            # return itertools.product(tuple(self.M.keys()), tuple(list_p))

        # Gets action combinations
        num_medics = len(list_m)
        combos_m = [tuple(list_m)]
        combos_p = itertools.permutations(list_p, num_medics)
        # Remove duplicates
        # Patients with respective index of the medic that is attending
        combos_p = [t for t in (set(tuple(i) for i in combos_p))]

        actions = itertools.product(combos_m, combos_p)

        actions_list = [list(zip(i[0], i[1])) for i in
                        actions]  # List of all possible actions without filtering actions that lead to unfeasible states

        action_list_copy = actions_list.copy()

        patient_result_list = []

        # Removes all states that result in infeasible state
        for action in action_list_copy:

            # Filter Medics with the same efficiency (Remove actions that result in the same state)
            if self.equivalent_M.__len__() > 0:
                patient_result = self.get_patient_result(action, state)

                if patient_result in patient_result_list:
                    actions_list.remove(action)
                    continue
                else:
                    patient_result_list.append(patient_result)

            # A critic patient is a patient that has to be attended in the next state. ( Remaining waiting time = 5)
            number_critic_patients = 0

            # Gets codes of patients being attended
            attended_patient = [i[1] for i in action if i[1] != "empty"]
            attended_patient_idx = [list(self.P.keys()).index(code) for code in
                                    attended_patient]  # Converts code to idx

            # Generates a list with all indexes
            all_index = list(range(0, self.P.__len__()))
            # Removes attended patient indexes from the list
            [all_index.remove(idx) for idx in attended_patient_idx]

            for i in all_index:  # Iterate all patients that are not being attended by a medic in this action
                patient_state = self.get_patient_from_state(state, i + 1)
                if patient_state[0] == 0 and patient_state[
                        1] > 0:  # If current patient has zero minutes and not being attended
                    actions_list.remove(action)
                    break
                # If patient remaining waiting time = t (5)
                if patient_state[0] == self.t:
                    number_critic_patients += 1  # Increments # of critic patients

            # If number of critic patients > number of medics -> Next state is unfeasible
            if number_critic_patients > self.M.__len__() and action in actions_list:
                actions_list.remove(action)

        """b = datetime.datetime.now()
        c = b - a
        print(c.microseconds)
        exit(0)"""

        # Filtrar acções que resultam num estado inválido!
        return iter(actions_list)

    def result(self, state, action):
        """A medic can either attend or not attend a patient
                If he attends, Patient Consult time decreases by t*me.
                If he doesn't attend, Patient Waiting time increases by t."""

        new_state = [state[0] + self.t]  # timestamp constant

        # Fill the(List) state with default value for the medics
        new_state.extend(self.M.__len__() * " ")

        for i in range(1, self.P.__len__() + 1):
            patient_state = self.get_patient_from_state(state, i)
            # patient code
            # if any(list(self.P.keys())[i] in j for j in action):
            try:
                medic_code = next(
                    mCode for (mCode, patientCode) in action if patientCode == list(self.P.keys())[i - 1])
                new_state[(list(self.M.keys()).index(medic_code) + 1)] = list(self.P.keys())[
                    i - 1]  # Updates list of state w/ new medic values (patient code of medic(i) )

                new_patient_conslt_time = patient_state[1] - (
                    self.M[medic_code] * self.t)  # Consult time of patient decreases by (me * t)
                new_state.append((patient_state[0],
                                  new_patient_conslt_time))  # Updates list of state w/ new patient values;  Patiente waiting time = previous state

            except:  # Patient not assigned to a medic by the given action
                # If patient consult time is greater than zero, change waiting time
                if patient_state[1] > 0:
                    new_patient_remaining_time = patient_state[
                        0] - self.t  # Time left for the patient to be attended decreases by 't'
                    new_state.append((new_patient_remaining_time, patient_state[
                        1]))  # Updates list of state w/ new patient values; Consult time = previous state
                else:
                    # If consult time <0, doesn't change state
                    new_state.append(patient_state)

                continue

        for i in range(1, self.M.__len__() + 1):
            if new_state[i] == ' ':
                new_state[i] = "empty"

        return tuple(new_state)

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        for i in range(1, self.P.__len__() + 1):
            if(self.get_patient_from_state(state, i)[1] > 0):
                return False
        return True  # Goal state -> all patients were attended

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1."""
        sum = 0
        # Sums the squares of all patients total waiting time
        for i in range(1, self.P.__len__() + 1):
            label_code = list(self.P.values())[i - 1][1]
            max_wait_time = self.L[label_code][0]
            sum += pow(max_wait_time - self.get_patient_from_state(state2, i)[0],
                       2)  # Square of patient total waiting time

        return sum  # Contemplates the total cost from the initial state until state 2

    def heuristic(self, node):
        # Ignoring Patient Waiting time limit

        volatilState = node.state

        while(1):

            if(self.goal_test(volatilState)):
                break

            # ratio to pick patient = (((Pacient waiting time + t)^2)/(patient consult time left^2)) * 1/Depth
            # Depth = (Patient consult time left)/ t  #Minimum depth possible => being always attended by a Medic with max efficiency (100%)
            ratios = []

            # Patients with consult time remaining lower than 5 and higher than 0
            pWithLowConsultTime = []

            for i in range(1, self.P.__len__() + 1):
                label_code = list(self.P.values())[i - 1][1]
                max_wait_time = self.L[label_code][0]
                pState = self.get_patient_from_state(volatilState, i)
                """if(pState[0] < 0):
                    return pow(self.path_cost(None, None, None, volatilState), 2)"""
                pWaitingTime = max_wait_time - pState[0]
                pConsultTime = pState[1]
                if(pConsultTime < 5 and pConsultTime > 0):
                    pWithLowConsultTime.append([i-1, pConsultTime])
                if(pConsultTime <= 0):
                    ratios.append(-1)
                    continue
                depth = pConsultTime / self.t
                r = ((pow(pWaitingTime + self.t, 2) /
                      pow(pConsultTime, 2)) * 1/depth)
                """r = ((10*pWaitingTime + self.t) /
                     pConsultTime) * 1/depth"""
                """r = ((pWaitingTime)/(pConsultTime))"""
                ratios.append(r)

            # If there's more Medics than patients that need attention
            # if this happens the the all patients will be attended and no patient will incrise wating time => Path cost doesn't change
            ratiosAux = [ratios[i]
                         for i in range(ratios.__len__()) if ratios[i] != -1]

            if(ratiosAux.__len__() <= self.M.__len__()):
                break

            medic_index_effSorted = list(reversed([i[0] for i in sorted(
                enumerate(self.M.values()), key=lambda x:x[1])]))

            ratios_indexSorted = list(reversed([i[0] for i in sorted(
                enumerate(ratios), key=lambda x:x[1])]))

            combos_p = ["empty"] * self.M.__len__()

            # Verify if there's a patient with less consult time that 5
            if(pWithLowConsultTime.__len__() > 0):
                indexAux1 = -1
                for pIndex, pConsultTime in pWithLowConsultTime:
                    combos_p[medic_index_effSorted[indexAux1]] = list(self.P.keys())[
                        pIndex]
                    indexAux1 -= 1
                    if(indexAux1 < -medic_index_effSorted.__len__()):
                        break

            # Assign medic to patient
            for medicIdx in medic_index_effSorted:
                if(combos_p[medicIdx] == "empty"):
                    for aux in ratios_indexSorted:
                        if((list(self.P.keys())[aux] not in combos_p)):
                            combos_p[medicIdx] = list(self.P.keys())[aux]
                            break

            h_action = list(itertools.product(
                list(self.M.keys()), combos_p))

            volatilState = self.result(volatilState, h_action)

        h_cost = self.path_cost(
            None, None, None, volatilState) - self.path_cost(None, None, None, node.state)

        return h_cost

    def heuristic2(self, node):
        sum = 0
        for i in range(1, self.P.__len__() + 1):
            try:
                sum += pow((1 / self.get_patient_from_state(node.state, i)
                            [1]) * 30, 2)
                sum += pow((1 / self.get_patient_from_state(node.state, i)
                            [0]) * 30, 2)
            except:
                continue
        return sum

    def load(self, file_obj):
        for line in file_obj:
            line_strs = line.split()

            if line == "\n":  # ignores blank line
                continue
            elif line_strs[0] == "MD":
                self.M[line_strs[1]] = float(line_strs[2])
            elif line_strs[0] == "PL":
                self.L[line_strs[1]] = (
                    float(line_strs[2]), float(line_strs[3]))
            elif line_strs[0] == "P":
                self.P[line_strs[1]] = (float(line_strs[2]), line_strs[3])
        rev_dict = {}
        for key, value in self.M.items():
            rev_dict.setdefault(value, set()).add(
                list(self.M.keys()).index(key))

        for key, value in rev_dict.items():
            if value.__len__() > 1:
                # List of medics with same efficiency
                self.equivalent_M.append(list(value))

        # Set inital state after loading input file
        self.initial = self.set_initial_state()

    def save(self, f):
        if self.solution_node == None:  # If there is no solution
            f.write("Infeasible")
            return
        node = self.solution_node
        actions = self.solution_node.depth * [None]

        for i in range(self.solution_node.depth):
            actions[self.solution_node.depth - i - 1] = node.action
            node = node.parent

        solution_actions = self.M.__len__() * [
            actions.__len__() * [None]]  # List of actions that lead to a solution state

        for j in range(self.M.__len__()):
            solution_actions[j] = [x[j][1] for x in actions]

        for i in range(self.M.__len__()):
            solution_actions[i].insert(0, list(self.M.keys())[i])
            solution_actions[i].insert(0, "MD")

        for item in solution_actions:
            f.write("%s\n" % str(item).replace("[", "").replace(
                "]", "").replace("'", "").replace(",", ""))

    def search(self):
        # self.solution_node = uniform_cost_search(self, display=True)
        self.solution_node = astar_search(self, self.heuristic)

        return False if self.solution_node == None else True
