import probability

class PDMAProblem():

    def __init__(self, fh):
        self.D = []
        self.S = {}
        self.E = {}
        self.M = {}
        self.P = 0.0
        self.load(fh)
        # Place here your code to load problem from opened file object fh
        # and use probability . BayesNet () to create the Bayesian network .

    def solve(self):
        # Place here your code to determine the maximum likelihood
        # solution returning the solution disease name and likelihood .
        # Use probability . elimination_ask () to perform probabilistic
        # inference .
        return 1
        #return (disease, likelihood)

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
                self.E[line_strs[1]] = (line_strs[2], float(line_strs[3]), float(line_strs[4]))
            elif line_strs[0] == "M":
                for i in range(1, line_strs.__len__()):
                    self.M.append(line_strs[i])

            elif line_strs[0] == "P":
                self.P = float(line_strs[1])
