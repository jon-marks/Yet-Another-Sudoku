from solve import solve_next_step
from solve_utils import *

def tj():

    TestSmpl = []

    TestSmpl.append([(1, 2), (5, 7)])  # opposing diagonal
    TestSmpl.append([(1, 2), (3, 9)])  # out of range col
    TestSmpl.append([(2, 0), (0, 7)])  # first floor, two cells

    TestSmpl.append([(0, 0), (2, 2), (2, 7)]) #first floor 3 cells
    TestSmpl.append([(0, 0), (2, 7), (2, 2)]) #first floor 3 cells
    TestSmpl.append([(2, 2), (2, 7), (0, 0)]) #first floor 3 cells
    TestSmpl.append([(2, 2), (0, 0), (2, 7)]) #first floor 3 cells
    TestSmpl.append([(2, 7), (2, 2), (0, 0)]) #first floor 3 cells
    TestSmpl.append([(2, 7), (0, 0), (2, 2)]) #first floor 3 cells

    TestSmpl.append([(0, 8), (2, 2), (2, 7)]) #first floor 3 cells
    TestSmpl.append([(0, 8), (2, 7), (2, 2)]) #first floor 3 cells
    TestSmpl.append([(2, 2), (2, 7), (0, 8)]) #first floor 3 cells
    TestSmpl.append([(2, 2), (0, 8), (2, 7)]) #first floor 3 cells
    TestSmpl.append([(2, 7), (2, 2), (0, 8)]) #first floor 3 cells
    TestSmpl.append([(2, 7), (0, 8), (2, 2)]) #first floor 3 cells


    for Smpl in TestSmpl:
        res = cells_intersect(Smpl)
        print(f"Cells {Smpl} intersect at {res}.")
    return



if __name__ == "__main__":
    tj()
