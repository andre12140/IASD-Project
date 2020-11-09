
import NewSolution
import sys
import time

if __name__ == '__main__':
    pmda = NewSolution.PDMAProblem() # Initiates the PMDAProblem object
    pmda.load(open("demo.txt", "r"))
    start = time.time()
    pmda.search() # Searches for a solution
    print("\n---INFO---\nTime of execution:", round(time.time()-start, 2) ,"s" )
    f = open("solution.txt", "w")
    pmda.save(f)    # Saves the actions that lead to the solution obtained
    try: print("Path Cost:", pmda.solution_node.path_cost)
    except: print("Infeasible")