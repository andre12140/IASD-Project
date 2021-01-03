import solution

if __name__ == '__main__':
    # Initiates the PMDAProblem object
    pmda = solution.MDProblem(open("PUB1.txt", "r"))
    (disease, likelihood) = pmda.solve()
    A = 1
