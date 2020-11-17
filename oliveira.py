from search import Problem, uniform_cost_search, depth_first_graph_search, astar_search, recursive_best_first_search
from itertools import permutations, combinations
import time


class PDMAProblem(Problem):
    def __init__(self):
        self.doctors = {}
        self.labels = {}
        self.patients = {}
        self.initial = {}
        self.solution_node = None

    def actions(self, state):
        wait_times, consult_time_remaining = self.get_waiting_times(
            state, consult=True)
        patients_waiting = [pat for pat,
                            time in consult_time_remaining.items() if time > 0]

        # If the number of patients waiting is small than the number of doctors, schedule them all
        if len(patients_waiting) < len(self.doctors):
            patients_waiting.extend(
                ['empty'] * (len(self.doctors) - len(patients_waiting)))
            # return permutations(patients_waiting, len(self.doctors))
            action = [tuple(patients_waiting)]
            return action

        # Patients that have waited the maximum time
        patients_in_deadline = tuple([pat for pat in patients_waiting if
                                      self.labels[self.patients[pat][1]][0] - wait_times[pat] == 0])
        # Patients that can wait
        patients_can_wait = tuple(
            [pat for pat in patients_waiting if pat not in patients_in_deadline])

        # Schedule all patients that have waited their maximum time and any other waiting patient if possible
        if len(patients_in_deadline) == 0:
            action_combs = combinations(patients_waiting, len(self.doctors))
            return self.action_gen(action_combs, consult_time_remaining)

        elif len(patients_in_deadline) < len(self.doctors):

            actions_combs = (patients_in_deadline + pat for pat in
                             combinations(patients_can_wait, len(self.doctors) - len(patients_in_deadline)))

            actions = self.action_gen(actions_combs, consult_time_remaining)
            return actions

        elif len(patients_in_deadline) == len(self.doctors):
            doctors = list(self.doctors.keys())
            next_patients_in_dealine = tuple([pat for pat in patients_waiting if
                                              self.labels[self.patients[pat][1]][0] - wait_times[pat] == 5])

            actions = []
            for action in permutations(patients_in_deadline):
                ctr_deadline = {
                    pat: consult_time_remaining[pat] for pat in patients_in_deadline}
                for pat in action:
                    ctr_deadline[pat] = max(0, ctr_deadline[pat] - self.doctors[
                        doctors[action.index(pat)]] * 5)
                n_pat_dealine = len([pat for pat, time in ctr_deadline.items() if time > 0]) + len(
                    next_patients_in_dealine)
                if n_pat_dealine <= len(doctors):
                    actions.append(action)
            actions = tuple(actions)
            return actions
        # If more patients have reached their maximum waiting time than the number of doctors, the state is a dead end
        else:
            return ()

    def result(self, state, action):
        new_state = tuple(state[d] + tuple([action[d]])
                          for d in range(len(state)))
        return new_state

    def goal_test(self, state):
        wait_times, consult_time_remaining = self.get_waiting_times(
            state, consult=True)
        sum_consult = sum(consult_time_remaining.values())
        if sum_consult > 0:
            return False
        return True

    def path_cost(self, c, state1, action, state2):
        wait_times = self.get_waiting_times(state2)
        return sum([n ** 2 for n in wait_times.values()])

    def load(self, f):
        self.doctors = {}
        self.labels = {}
        self.patients = {}
        for line in f:
            spl = line.split()
            if len(spl) != 0:
                if spl[0] == 'MD':
                    # { <doctor_code> : <efficiency> }
                    self.doctors[spl[1]] = float(spl[2])
                elif spl[0] == 'PL':
                    # { <label_code> : [ <max_waiting_time>, <consult_time> ] }
                    self.labels[spl[1]] = (int(spl[2]), int(spl[3]))
                elif spl[0] == 'P':
                    # { <patient_code> : [ <current_waiting_time>, <label> ] }
                    self.patients[spl[1]] = (int(spl[2]), spl[3])

        self.initial = tuple(() for t in range(len(self.doctors)))

    def save(self, f):
        state = self.solution_node.state
        state = self.state_as_dict(state)
        for pat in state.keys():
            doctor_schedule = 'MD ' + pat + ' ' + ' '.join(state[pat])
            print(doctor_schedule, file=f)

    def search(self):
        self.solution_node = astar_search(self, h=self.heuristic)
        # goal_node = uniform_cost_search(self, display=True)
        # goal_node = depth_first_graph_search(self)
        if self.solution_node:
            print()
            print(self.state_as_dict(self.solution_node.state))
            print()
            print('Depth: ' + str(self.solution_node.depth))
            print('Path Cost: ' + str(self.solution_node.path_cost))
            print()
            wait_times, consult_time_remaining = self.get_waiting_times(
                self.solution_node.state, consult=True)
            print(wait_times, '\n', consult_time_remaining)
            return True
        else:
            return False

    def state_as_dict(self, state):
        doctor_list = list(self.doctors.keys())
        dict_state = {doctor_list[a]: state[a] for a in range(len(state))}
        return dict_state

    def get_waiting_times(self, s, consult=False):
        state = self.state_as_dict(s)
        current_time = len(list(state.values())[0])
        doctor_list = list(self.doctors.keys())

        # Initialize patient waiting times at their initial value
        wait_times = {pat: data[0] for pat, data in self.patients.items()}
        # Initialize the time left in consult for each patient with the time in their label
        consult_time_remaining = {
            pat: self.labels[data[1]][1] for pat, data in self.patients.items()}

        for t in range(current_time):
            patients_in_consult = [patients[t] for patients in state.values()]

            for pat in self.patients.keys():
                if pat in patients_in_consult:
                    consult_time_remaining[pat] = max(0, consult_time_remaining[pat] - self.doctors[
                        doctor_list[patients_in_consult.index(pat)]] * 5)
                elif consult_time_remaining[pat] > 0:
                    wait_times[pat] += 5
        if consult:
            return wait_times, consult_time_remaining
        return wait_times

    def action_gen(self, action_combs, consult_time_remaining):
        doc_efficiency = list(self.doctors.values())
        for comb in action_combs:
            initial_times = {pat: time for pat,
                             time in consult_time_remaining.items() if pat in comb}
            valid_outcomes = set()
            perms = permutations(comb)
            for perm in perms:
                resulting_times = {
                    pat: initial_times[pat] - 5*doc_efficiency[perm.index(pat)] for pat in comb}
                new_outcome = tuple(resulting_times.values())
                if new_outcome not in valid_outcomes:
                    valid_outcomes.add(new_outcome)
                    yield perm

    def heuristic(self, node):
        wait_times, consult_time_remaining = self.get_waiting_times(
            node.state, consult=True)
        doctors = list(self.doctors.keys())
        sorted_doctors = sorted(
            doctors, key=lambda d: self.doctors[d], reverse=True)
        doctor_efficiency = list(self.doctors.values())

        h_state = node.state
        h_consult_times = consult_time_remaining.copy()
        h_wait_times = wait_times.copy()

        sum_consult = sum(consult_time_remaining.values())

        while sum_consult > 0:

            patients_waiting = [pat for pat,
                                time in h_consult_times.items() if time > 0]
            remaining_patients = patients_waiting.copy()
            if len(patients_waiting) < len(doctors):
                h_action = tuple(tuple(patients_waiting) + ('empty',)
                                 * (len(doctors) - len(patients_waiting)))
            else:
                h_action = [''] * len(doctors)
                for doc in sorted_doctors:
                    ratios = {
                        pat: (
                            self.doctors[doc] * (10*wait_times[pat] + 5) / h_consult_times[pat], 1 / h_consult_times[pat])
                        for pat in remaining_patients}

                    best_patient = sorted(
                        remaining_patients, key=lambda p: ratios[p], reverse=True)[0]
                    remaining_patients.remove(best_patient)
                    h_action[doctors.index(doc)] = best_patient
                h_action = tuple(h_action)

            for pat in patients_waiting:
                if pat in h_action:
                    h_consult_times[pat] = max(0, h_consult_times[pat] - self.doctors[
                        doctors[h_action.index(pat)]] * 5)
                elif h_consult_times[pat] > 0:
                    h_wait_times[pat] += 5
            h_state = self.result(h_state, h_action)

            sum_consult = sum(h_consult_times.values())

        h_cost = sum([n ** 2 for n in h_wait_times.values()]) - node.path_cost

        return h_cost

    def heuristic2(self, node):
        wait_times, consult_time_remaining = self.get_waiting_times(
            node.state, consult=True)
        doctors = list(self.doctors.keys())
        sorted_doctors = sorted(
            doctors, key=lambda d: self.doctors[d], reverse=True)
        doctor_efficiency = list(self.doctors.values())

        h_state = node.state
        h_consult_times = consult_time_remaining.copy()
        h_wait_times = wait_times.copy()

        sum_consult = sum(consult_time_remaining.values())

        while sum_consult > 0:

            patients_waiting = [pat for pat,
                                time in h_consult_times.items() if time > 0]
            remaining_patients = patients_waiting.copy()
            if len(patients_waiting) < len(doctors):
                h_action = tuple(tuple(patients_waiting) + ('empty',)
                                 * (len(doctors) - len(patients_waiting)))
            else:
                h_action = [''] * len(doctors)
                for doc in sorted_doctors:
                    ratios = {
                        pat: (
                            self.doctors[doc] * (wait_times[pat]
                                                 ** 2) / h_consult_times[pat],
                            1 / h_consult_times[pat])
                        for pat in remaining_patients}

                    best_patient = sorted(
                        remaining_patients, key=lambda p: ratios[p], reverse=True)[0]
                    remaining_patients.remove(best_patient)
                    h_action[doctors.index(doc)] = best_patient
                h_action = tuple(h_action)

            for pat in patients_waiting:
                if pat in h_action:
                    h_consult_times[pat] = max(0, h_consult_times[pat] - self.doctors[
                        doctors[h_action.index(pat)]] * 5)
                elif h_consult_times[pat] > 0:
                    h_wait_times[pat] += 5
            h_state = self.result(h_state, h_action)

            sum_consult = sum(h_consult_times.values())

        h_cost = sum([n ** 2 for n in h_wait_times.values()]) - node.path_cost

        return h_cost
