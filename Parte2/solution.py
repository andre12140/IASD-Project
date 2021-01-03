import probability
import itertools


class MDProblem():

    def __init__(self, fh):
        self.D = []
        self.S = {}
        self.E = {}
        self.M = []
        self.P = 0.0
        self.load(fh)
        self.totalTime = self.M.__len__()
        self.bayes = self.createBayesNet()

    def solve(self):

        # Build Evidence of measurements for elimination_ask = ev_dict
        ev_dict = {}  # for the elimination ask
        p_dict = {}
        time = 0
        for examesListTimeT in self.M:
            for i in range(0, examesListTimeT.__len__(), 2):
                ev_dict[str(time) + '-' + examesListTimeT[i]
                        ] = bool(examesListTimeT[i+1] == 'T')
            time += 1

        # Get likelihood for each room and store value in dictionary
        for disease in self.D:
            # get likelihood of room being on fire = True
            likelihood_aux = probability.elimination_ask(
                str(self.totalTime-1) + '-' + disease, ev_dict, self.bayes)[True]
            # Save values
            p_dict[disease] = likelihood_aux
        # Get max value
        diseaseName = max(p_dict, key=p_dict.get)
        likelihood = p_dict[diseaseName]

        return (diseaseName, likelihood)

    def getExam(self, diseaseName):
        listExams = []
        for Key_exam in self.E:
            if (diseaseName in self.E[Key_exam]):
                listExams.append(Key_exam)
        return listExams

    def getCommonSimptom(self, diseaseName):
        listDiseases = []
        for i in self.S:
            if(diseaseName in self.S[i]):
                for disease in self.S[i]:
                    if(disease not in listDiseases):
                        listDiseases.append(disease)
        if(diseaseName in listDiseases):
            listDiseases.remove(diseaseName)
        return listDiseases

    def getProb(self, diseaseName, CommonSimptomsLen):
        dic = {}
        # length of neighbours is always +1 because we need to count with itself as well
        num = CommonSimptomsLen + 1
        # generate binary list
        condProbTable = list(itertools.product([False, True], repeat=num))
        if(num == 1):
            dic[True] = 1
            dic[False] = 0
            return dic

        for row in condProbTable:

            # Check if they are all 'False'
            if all(item == False for item in row):
                dic[row] = 0

            # if first element is 'False', it's now assured that there's at least a 'True' after
            elif row[0] == False:
                dic[row] = 0

            # if first element is 'True', it's now assured that there's at least a 'False' after
            elif row[0] == True:
                dic[row] = 1

            TrueCount = 0
            if(row[0] == True):
                for item in row:
                    if(item == True):
                        TrueCount += 1
                        if(TrueCount >= 2):
                            dic[row] = self.P
                            continue
        return dic

    def createBayesNet(self):
        baye = []
        # Step in this case goes only until T-1
        for t in range(self.totalTime):
            for disease in self.D:
                # Create parents at t=0
                if t == 0:
                    # Add initial probability
                    # X = BayesNode('X', '', 0.2)
                    baye.append((str(t) + '-' + disease, '', 0.5))
                    # Add respective sensors if any
                    for exameName in self.getExam(disease):
                        baye.append((str(t) + '-' + exameName, str(t) + '-' + disease,
                                     {True: self.E[exameName][1], False: self.E[exameName][2]}))  # Y = BayesNode('Y', 'P', {T: 0.2, F: 0.7})
                else:
                    # Start building the child nodes
                    ax = 1
                    # Add parents of current node
                    parent = str(t-1) + '-' + disease

                    listCommonSimptom = self.getCommonSimptom(disease)

                    # buscar sintomas que estao presentes nesta doenca
                    for sameSimptomDisease in listCommonSimptom:
                        parent = parent + ' ' + \
                            str(t-1) + '-' + sameSimptomDisease
                        ax += 1

                    # Z = BayesNode('Z', 'P Q',{(T, T): 0.2, (T, F): 0.3, (F, T): 0.5, (F, F): 0.7})
                    baye.append((str(t) + '-' + disease, parent,
                                 self.getProb(disease, listCommonSimptom.__len__())))

                    # Add respective sensors of the room if any
                    for exameName in self.getExam(disease):
                        baye.append((str(t) + '-' + exameName, str(t) + '-' + disease,
                                     {True: self.E[exameName][1], False: self.E[exameName][2]}))  # Y = BayesNode('Y', 'P', {T: 0.2, F: 0.7})
        # Uncomment to see bayes net
        # print(baye)
        return probability.BayesNet(baye)

    def load(self, file_obj):
        for line in file_obj:
            line_strs = line.split()

            if line == "\n":  # ignores blank line
                continue

            elif line_strs[0] == "D":
                for i in range(1, line_strs.__len__()):
                    self.D.append(line_strs[i])

            elif line_strs[0] == "S":
                self.S[line_strs[1]] = []
                for i in range(2, line_strs.__len__()):
                    self.S[line_strs[1]].append(line_strs[i])

            elif line_strs[0] == "E":
                self.E[line_strs[1]] = (line_strs[2], float(
                    line_strs[3]), float(line_strs[4]))

            elif line_strs[0] == "M":
                lista = []
                for i in range(1, line_strs.__len__()):
                    lista.append(line_strs[i])
                self.M.append(lista)

            elif line_strs[0] == "P":
                self.P = float(line_strs[1])
