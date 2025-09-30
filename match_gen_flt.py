from tqdm import tqdm
import json

class MatchGen(object):

    def __init__(self):
        self.have_cnt = 0
        self.qa_save = []

    # Convert per-position encoded digits to a full equation representation
    def solotowhole(self, ori_num):
        num = ori_num[:]
        num[0] = 0 if num[0] == -1 else num[0]
        num[3] = 0 if num[3] == -1 else num[3]
        num[6] = 0 if num[6] == -1 else num[6]
        formula = []
        formula.append(num[2] - 10)
        formula.append(num[0] * 10 + num[1])
        formula.append(num[3] * 10 + num[4])
        formula.append(num[6] * 10 + num[7])
        return formula
    
    # Search solutions by moving one matchstick       
    def deal(self, numarr:list):
        position1, position0, positionm1 = [], [], [] # positions of matchsticks
        nump1, nump0, numpm1 = 0, 0, 0
        difficulty1 = []
        difficulty2 = []
        information = [[9,9,9,9,9,9,0,9,1,0,9,9],
                       [9,9,9,9,9,9,9,1,9,9,9,9],
                       [9,9,9,0,9,9,9,9,9,9,9,9],
                       [9,9,0,9,9,0,9,9,9,1,9,9],
                       [9,9,9,9,9,9,9,9,9,9,9,9],
                       [9,9,9,0,9,9,1,9,9,1,9,9],
                       [0,9,9,9,9,-1,9,9,1,0,9,9],
                       [9,-1,9,9,9,9,9,9,9,9,9,9],
                       [-1,9,9,9,9,9,-1,9,9,-1,9,9],
                       [0,9,9,-1,9,-1,0,9,1,9,9,9],
                       [9,9,9,9,9,9,9,9,9,9,9,-1],
                       [9,9,9,9,9,9,9,9,9,9,1,9]]

        numarrcopy = numarr[:]
        tempequal = self.solotowhole(numarrcopy)
        correctsign = 0
        # Equation validation
        if tempequal[0] == 0:
            if tempequal[1] + tempequal[2] == tempequal[3]:
                self.problem = f"{tempequal[1]} + {tempequal[2]} = {tempequal[3]}"
                correctsign = 1
        elif tempequal[0] == 1:
            if tempequal[1] - tempequal[2] == tempequal[3]:
                self.problem = f"{tempequal[1]} + {tempequal[2]} = {tempequal[3]}"
                correctsign = 1
        
        if correctsign > 0:
            finalanswer = tempequal[:]
            self.mode_1_solution = []
            self.mode_1_solution_raw = []
            return

        # Assign positions and counts
        for j in range(8):
            if numarr[j] != -1:
                for k in range(12):
                    if information[numarr[j]][k] == 1:
                        position1.append([j,k])
                        nump1 = nump1 + 1
                    if information[numarr[j]][k] == 0:
                        position0.append([j,k])
                        nump0 = nump0 + 1
                    if information[numarr[j]][k] == -1:
                        positionm1.append([j,k])
                        numpm1 = numpm1 + 1                 

        correctsign = 0 # solution found flag
        solutionnum = 0 # number of solutions
        solution, solution_raw = [], [] # all solutions
        if nump0 != 0 : # move within a single digit
            for i in range(nump0):
                numarrcopy = numarr[:]
                numarrcopy[position0[i][0]] = position0[i][1]
                if numarrcopy[5] != -1 or numarrcopy[2] == -1:
                    continue
                tempequal = self.solotowhole(numarrcopy)
                correctsign = 0
                # Equation validation
                if tempequal[0] == 0:
                    if tempequal[1] + tempequal[2] == tempequal[3]:
                        correctsign = 1
                elif tempequal[0] == 1:
                    if tempequal[1] - tempequal[2] == tempequal[3]:
                        correctsign = 1

                if correctsign == 1:
                    finalanswer = tempequal[:]
                    solution.append(finalanswer)
                    solution_raw.append(numarrcopy[:])
                    solutionnum = solutionnum + 1

                    difficulty1.append(1)
                    if numarrcopy[2] != numarr[2]:
                        difficulty2.append(2)
                    else:
                        difficulty2.append(1)

        if nump1 != 0 and numpm1 != 0: # move between different digits
            for i in range(nump1):
                for j in range(numpm1):
                    if position1[i][0] == positionm1[j][0]: # skip if same digit
                        continue
                    numarrcopy = numarr[:]
                    numarrcopy[position1[i][0]] = position1[i][1]
                    numarrcopy[positionm1[j][0]] = positionm1[j][1]
                    correctsign = 0
                    
                    tempequal = self.solotowhole(numarrcopy)
                    # Equation validation
                    if tempequal[0] == 0:
                        if tempequal[1] + tempequal[2] == tempequal[3]:
                            correctsign = 1
                    elif tempequal[0] == 1:
                        if tempequal[1] - tempequal[2] == tempequal[3]:
                            correctsign = 1
                    elif tempequal[0] == 2:
                        if tempequal[1] * tempequal[2] == tempequal[3]:
                            correctsign = 1

                    if correctsign == 1:
                        finalanswer = tempequal[:]
                        solution.append(finalanswer)
                        solution_raw.append(numarrcopy[:])
                        solutionnum = solutionnum + 1
                        difficulty1.append(2)
                        if numarrcopy[2] != numarr[2]:
                            difficulty2.append(2)
                        else:
                            difficulty2.append(1)
        finaldifficulty = []
        # Check if solutions exist
        if solutionnum == 0:
            # print("No solution")
            self.mode_1_solution = []
            self.mode_1_solution_raw = []

        else:
            self.searesult = solution[:]
            self.searesultnum = solutionnum
            self.currentnum = solutionnum - 1
            sumdifficulty = 0
            for i in range(solutionnum):
                finaldifficulty.append(difficulty1[i]*0.4*2.5 + difficulty2[i]*0.6*5/3) # difficulty metric
                sumdifficulty = sumdifficulty + difficulty1[i]*0.4*2.5 + difficulty2[i]*0.6*5/3 # sum
            averagefifficulty = sumdifficulty/solutionnum # average
            self.evaluedifficulty = finaldifficulty[:]

            # print("Number of solutions:", solutionnum)
            # print(f"Solutions: \n{solution}")
            # print(f"difficulty1: {difficulty1}")
            # print(f"difficulty2: {difficulty2}")
            # print(f"Average difficulty: {averagefifficulty:.2f}")

            self.mode_1_solution = solution
            self.mode_1_solution_raw = solution_raw

    
    # Search solutions by moving two matchsticks
    def deal2(self, numarr:list):
        difficulty1 = []
        difficulty2 = []
        information = [[9,9,9,9,9,9,0,9,1,0,9,9],
                       [9,9,9,9,9,9,9,1,9,9,9,9],
                       [9,9,9,0,9,9,9,9,9,9,9,9],
                       [9,9,0,9,9,0,9,9,9,1,9,9],
                       [9,9,9,9,9,9,9,9,9,9,9,9],
                       [9,9,9,0,9,9,1,9,9,1,9,9],
                       [0,9,9,9,9,-1,9,9,1,0,9,9],
                       [9,-1,9,9,9,9,9,9,9,9,9,9],
                       [-1,9,9,9,9,9,-1,9,9,-1,9,9],
                       [0,9,9,-1,9,-1,0,9,1,9,9,9],
                       [9,9,9,9,9,9,9,9,9,9,9,-1],
                       [9,9,9,9,9,9,9,9,9,9,1,9]]

        information2 = [[9,9,-1,-1,9,-1,0,9,1,0,9,9],
                        [9,9,9,9,2,9,9,9,9,9,9,9],
                        [1,9,9,0,9,0,1,9,2,1,9,9],
                        [1,9,0,9,-1,0,1,-2,2,1,9,9],
                        [9,-2,9,1,9,1,9,-1,9,2,9,9],
                        [1,9,0,0,-1,9,1,9,2,1,9,9],
                        [0,9,-1,-1,9,-1,9,9,1,0,9,9],
                        [9,-1,9,2,1,9,9,9,9,9,9,9],
                        [-1,9,-2,-2,9,-2,-1,9,9,-1,9,9],
                        [0,9,-1,-1,-2,-1,0,9,1,9,9,9],
                        [9,9,9,9,9,9,9,9,9,9,9,-1],
                        [9,9,9,9,9,9,9,9,9,9,1,9]]

        numarrcopy = numarr[:]
        tempequal = self.solotowhole(numarrcopy)
        correctsign = 0
        # Equation validation
        if tempequal[0] == 0:
            if tempequal[1] + tempequal[2] == tempequal[3]:
                self.problem = f"{tempequal[1]} + {tempequal[2]} = {tempequal[3]}"
                correctsign = 1
        elif tempequal[0] == 1:
            if tempequal[1] - tempequal[2] == tempequal[3]:
                self.problem = f"{tempequal[1]} + {tempequal[2]} = {tempequal[3]}"
                correctsign = 1
        
        if correctsign > 0:
            finalanswer = tempequal[:]
            self.mode_2_solution = []
            self.mode_2_solution_raw = []
            return
        
        solution, solution_raw = [], [] # all solutions
        solutionnum = 0 # number of solutions

        # Variation of moving within/between digits
        position0, position1, positionm1 = [], [], [] # positions
        nump0, nump1, numpm1 = 0, 0, 0 # counts
        position02, position1move, positionm1move = [], [], [] # positions
        nump02, nump1move, numpm1move = 0, 0, 0 # counts
        position2, positionm2 = [], [] # positions
        nump2, numpm2 = 0, 0 # counts

        # Assign positions and counts
        for j in range(8):
            if numarr[j] != -1:
                for k in range(12):
                    if information[numarr[j]][k] == 1:
                        position1.append([j,k])
                        nump1 = nump1 + 1
                    if information[numarr[j]][k] == 0:
                        position0.append([j,k])
                        nump0 = nump0 + 1
                    if information[numarr[j]][k] == -1:
                        positionm1.append([j,k])
                        numpm1 = numpm1 + 1
                    if information2[numarr[j]][k] == 0:
                        position02.append([j,k])
                        nump02 = nump02 + 1
                    if information2[numarr[j]][k] == 1:
                        position1move.append([j,k])
                        nump1move = nump1move + 1
                    if information2[numarr[j]][k] == -1:
                        positionm1move.append([j,k])
                        numpm1move = numpm1move + 1
                    if information2[numarr[j]][k] == 2:
                        position2.append([j,k])
                        nump2 = nump2 + 1
                    if information2[numarr[j]][k] == -2:
                        positionm2.append([j,k])
                        numpm2 = numpm2 + 1
         
        correctsign = 0 # solution found flag

        if nump02 != 0: # two moves within one digit
            for i in range(nump02):
                numarrcopy = numarr[:]
                numarrcopy[position02[i][0]] = position02[i][1]
                correctsign = 0

                tempequal = self.solotowhole(numarrcopy)
                # Equation validation
                if tempequal[0] == 0:
                    if tempequal[1] + tempequal[2] == tempequal[3]:
                        correctsign = 1
                elif tempequal[0] == 1:
                    if tempequal[1] - tempequal[2] == tempequal[3]:
                        correctsign = 1

                if correctsign == 1:
                    finalanswer = tempequal[:]
                    solution.append(finalanswer)
                    solution_raw.append(numarrcopy[:])
                    solutionnum = solutionnum + 1
                    difficulty1.append(1)
                    if numarrcopy[2] != numarr[2]:
                        difficulty2.append(2)
                    else:
                        difficulty2.append(1)

        if nump2 != 0 and numpm2 != 0: # move two from one digit to another
            for i in range(nump2):
                for j in range(numpm2):
                    if position2[i][0] != positionm2[j][0]:
                        numarrcopy = numarr[:]
                        numarrcopy[position2[i][0]] = position2[i][1]
                        numarrcopy[positionm2[j][0]] = positionm2[j][1]
                        correctsign = 0

                        tempequal = self.solotowhole(numarrcopy)
                        # Equation validation
                        if tempequal[0] == 0:
                            if tempequal[1] + tempequal[2] == tempequal[3]:
                                correctsign = 1
                        elif tempequal[0] == 1:
                            if tempequal[1] - tempequal[2] == tempequal[3]:
                                correctsign = 1

                        if correctsign == 1:
                            finalanswer = tempequal[:]
                            solution.append(finalanswer)
                            solution_raw.append(numarrcopy[:])

                            solutionnum = solutionnum + 1
                            difficulty1.append(2)
                            if numarrcopy[2] != numarr[2]:
                                difficulty2.append(2)
                            else:
                                difficulty2.append(1)

        if nump2 != 0 and numpm1 >= 2: # one digit gains two, two digits lose one each
            for i in range(nump2):
                for j in range(numpm1 - 1):
                    for k in range(numpm1 - j - 1):
                        if position2[i][0] != positionm1[j][0] and position2[i][0] != positionm1[j+k+1][0] and positionm1[j][0] != positionm1[j+k+1][0]:
                            numarrcopy = numarr[:]
                            numarrcopy[position2[i][0]] = position2[i][1]
                            numarrcopy[positionm1[j][0]] = positionm1[j][1]
                            numarrcopy[positionm1[j+k+1][0]] = positionm1[j+k+1][1]
                            correctsign = 0

                            tempequal = self.solotowhole(numarrcopy)
                            # Equation validation
                            if tempequal[0] == 0:
                                if tempequal[1] + tempequal[2] == tempequal[3]:
                                    correctsign = 1
                            elif tempequal[0] == 1:
                                if tempequal[1] - tempequal[2] == tempequal[3]:
                                    correctsign = 1

                            if correctsign == 1:
                                finalanswer = tempequal[:]
                                solution.append(finalanswer)
                                solution_raw.append(numarrcopy[:])

                                solutionnum = solutionnum + 1
                                difficulty1.append(3)
                                if numarrcopy[2] != numarr[2]:
                                    difficulty2.append(2)
                                else:
                                    difficulty2.append(1)

        if numpm2 != 0 and nump1 >= 2: # one digit loses two, two digits gain one each
            for i in range(numpm2):
                for j in range(nump1 - 1):
                    for k in range(nump1 - j - 1):
                        if positionm2[i][0] != position1[j][0] and positionm2[i][0] != position1[j+k+1][0] and position1[j][0] != position1[j+k+1][0]:
                            numarrcopy = numarr[:]
                            numarrcopy[positionm2[i][0]] = positionm2[i][1]
                            numarrcopy[position1[j][0]] = position1[j][1]
                            numarrcopy[position1[j+k+1][0]] = position1[j+k+1][1]
                            correctsign = 0

                            tempequal = self.solotowhole(numarrcopy)
                            # Equation validation
                            if tempequal[0] == 0:
                                if tempequal[1] + tempequal[2] == tempequal[3]:
                                    correctsign = 1
                            elif tempequal[0] == 1:
                                if tempequal[1] - tempequal[2] == tempequal[3]:
                                    correctsign = 1
                            elif tempequal[0] == 2:
                                if tempequal[1] * tempequal[2] == tempequal[3]:
                                    correctsign = 1

                            if correctsign == 1:
                                finalanswer = tempequal[:]
                                solution.append(finalanswer)
                                solution_raw.append(numarrcopy[:])

                                solutionnum = solutionnum + 1
                                difficulty1.append(3)
                                if numarrcopy[2] != numarr[2]:
                                    difficulty2.append(2)
                                else:
                                    difficulty2.append(1)

        if nump0 >=2: # two digits move one each
            for i in range(nump0 - 1):
                for j in range(nump0 - i - 1):
                    if position0[i][0] != position0[i+j+1][0]:
                        numarrcopy = numarr[:]
                        numarrcopy[position0[i][0]] = position0[i][1]
                        numarrcopy[position0[i+j+1][0]] = position0[i+j+1][1]
                        correctsign = 0
                        
                        tempequal = self.solotowhole(numarrcopy)
                        # Equation validation
                        if tempequal[0] == 0:
                            if tempequal[1] + tempequal[2] == tempequal[3]:
                                correctsign = 1
                        elif tempequal[0] == 1:
                            if tempequal[1] - tempequal[2] == tempequal[3]:
                                correctsign = 1

                        if correctsign == 1:
                            finalanswer = tempequal[:]
                            solution.append(finalanswer)
                            solution_raw.append(numarrcopy[:])

                            solutionnum = solutionnum + 1
                            difficulty1.append(2)
                            if numarrcopy[2] != numarr[2]:
                                difficulty2.append(2)
                            else:
                                difficulty2.append(1)

        if nump1 >= 2 and numpm1 >= 2: # two digits gain one, two digits lose one
            for i in range(nump1 - 1):
                for j in range(nump1 - i - 1):
                    for m in range(numpm1 - 1):
                        for n in range(numpm1 - m - 1):
                            if position1[i][0] != position1[i+j+1][0] and position1[i][0] != positionm1[m][0] and position1[i][0] != positionm1[m+n+1][0] and position1[i+j+1][0] != positionm1[m][0] and position1[i+j+1][0] != positionm1[m+n+1][0] and positionm1[m][0] != positionm1[m+n+1][0]:
                                numarrcopy = numarr[:]
                                numarrcopy[position1[i][0]] = position1[i][1]
                                numarrcopy[position1[i+j+1][0]] = position1[i+j+1][1]
                                numarrcopy[positionm1[m][0]] = positionm1[m][1]
                                numarrcopy[positionm1[m+n+1][0]] = positionm1[m+n+1][1]
                                correctsign = 0
                                
                                tempequal = self.solotowhole(numarrcopy)
                                # Equation validation
                                if tempequal[0] == 0:
                                    if tempequal[1] + tempequal[2] == tempequal[3]:
                                        correctsign = 1
                                elif tempequal[0] == 1:
                                    if tempequal[1] - tempequal[2] == tempequal[3]:
                                        correctsign = 1

                                if correctsign == 1:
                                    finalanswer = tempequal[:]
                                    solution.append(finalanswer)
                                    solution_raw.append(numarrcopy[:])
                                    solutionnum = solutionnum + 1
                                    difficulty1.append(4)
                                    if numarrcopy[2] != numarr[2]:
                                        difficulty2.append(2)
                                    else:
                                        difficulty2.append(1)

        if (nump0 != 0 and nump1 != 0 and numpm1 != 1 ) or (nump1move != 0 and numpm1 != 0 ) or (numpm1move != 0 and nump1 != 0): # mixed moves
            if nump0 != 0 and nump1 != 0 and numpm1 != 1:
                for i in range(nump0):
                    for j in range(nump1):
                        for k in range(numpm1):
                            if position0[i][0] != position1[j][0] and position0[i][0] != positionm1[k][0] and position1[j][0] != positionm1[k][0]:
                                numarrcopy = numarr[:]
                                numarrcopy[position0[i][0]] = position0[i][1]
                                numarrcopy[position1[j][0]] = position1[j][1]
                                numarrcopy[positionm1[k][0]] = positionm1[k][1]
                                correctsign = 0
                                
                                tempequal = self.solotowhole(numarrcopy)
                                # Equation validation
                                if tempequal[0] == 0:
                                    if tempequal[1] + tempequal[2] == tempequal[3]:
                                        correctsign = 1
                                elif tempequal[0] == 1:
                                    if tempequal[1] - tempequal[2] == tempequal[3]:
                                        correctsign = 1

                                if correctsign == 1:
                                    finalanswer = tempequal[:]
                                    solution.append(finalanswer)
                                    solution_raw.append(numarrcopy[:])

                                    solutionnum = solutionnum + 1
                                    difficulty1.append(3)
                                    if numarrcopy[2] != numarr[2]:
                                        difficulty2.append(2)
                                    else:
                                        difficulty2.append(1)
            
            if nump1move != 0 and numpm1 != 0:
                for i in range(nump1move):
                    for j in range(numpm1):
                        if position1move[i][0] != positionm1[j][0]:
                            numarrcopy = numarr[:]
                            numarrcopy[position1move[i][0]] = position1move[i][1]
                            numarrcopy[positionm1[j][0]] = positionm1[j][1]
                            correctsign = 0
                            
                            tempequal = self.solotowhole(numarrcopy)
                            # Equation validation
                            if tempequal[0] == 0:
                                if tempequal[1] + tempequal[2] == tempequal[3]:
                                    correctsign = 1
                            elif tempequal[0] == 1:
                                if tempequal[1] - tempequal[2] == tempequal[3]:
                                    correctsign = 1

                            if correctsign == 1:
                                finalanswer = tempequal[:]
                                solution.append(finalanswer)
                                solution_raw.append(numarrcopy[:])
                                solutionnum = solutionnum + 1
                                difficulty1.append(5)
                                if numarrcopy[2] != numarr[2]:
                                    difficulty2.append(2)
                                else:
                                    difficulty2.append(1)
        
            if numpm1move != 0 and nump1 != 0:
                for i in range(numpm1move):
                    for j in range(nump1):
                        if positionm1move[i][0] != position1[j][0]:
                            numarrcopy = numarr[:]
                            numarrcopy[positionm1move[i][0]] = positionm1move[i][1]
                            numarrcopy[position1[j][0]] = position1[j][1]
                            correctsign = 0
                            
                            tempequal = self.solotowhole(numarrcopy)
                            # Equation validation
                            if tempequal[0] == 0:
                                if tempequal[1] + tempequal[2] == tempequal[3]:
                                    correctsign = 1
                            elif tempequal[0] == 1:
                                if tempequal[1] - tempequal[2] == tempequal[3]:
                                    correctsign = 1

                            if correctsign == 1:
                                finalanswer = tempequal[:]
                                solution.append(finalanswer)
                                solution_raw.append(numarrcopy[:])
                                solutionnum = solutionnum + 1
                                difficulty1.append(5)
                                if numarrcopy[2] != numarr[2]:
                                    difficulty2.append(2)
                                else:
                                    difficulty2.append(1)
                
        # Check if solutions exist
        finaldifficulty = []
        if solutionnum == 0:
            # print('No solution')
            self.mode_2_solution = []
            self.mode_2_solution_raw = []
        else:
            self.searesult = solution[:]
            self.searesultnum = solutionnum
            self.currentnum = solutionnum - 1
            sumdifficulty = 0
            for i in range(solutionnum):
                finaldifficulty.append(difficulty1[i]*0.4 + difficulty2[i]*0.6*5/3)# difficulty metric
                sumdifficulty = sumdifficulty + difficulty1[i]*0.4 + difficulty2[i]*0.6*5/3# sum
            averagefifficulty = sumdifficulty/solutionnum# average
            self.evaluedifficulty = finaldifficulty[:]

            # print("Number of solutions:", solutionnum)
            # print(f"Solutions: \n{solution}")
            # print(f"difficulty1: {difficulty1}")
            # print(f"difficulty2: {difficulty2}")
            # print(f"Average difficulty: {averagefifficulty:.2f}")

            self.mode_2_solution = solution
            self.mode_2_solution_raw = solution_raw
    
    # Build the equation string for a given raw array
    def showresultstr(self,numarr):
        tempnum = numarr[:]
        str0 = str(tempnum[0]) if tempnum[0] != -1 else ''
        str1 = str(tempnum[1]) if tempnum[1] != -1 else ''
        str3 = str(tempnum[3]) if tempnum[3] != -1 else ''
        str4 = str(tempnum[4]) if tempnum[4] != -1 else ''
        str6 = str(tempnum[6]) if tempnum[6] != -1 else ''
        str7 = str(tempnum[7]) if tempnum[7] != -1 else ''

        if tempnum[2] == 10:
            str2 = ' + '
        elif tempnum[2] == 11:
            str2 = ' - '
        else:
            raise AssertionError(f"Invalid operation code in numarr[2]: {tempnum[2]}")

        str5 = ' = '
        tempstr = f"{str0}{str1}{str2}{str3}{str4}{str5}{str6}{str7}"
        return tempstr

    # Run both modes and consolidate
    def search(self, numarr:list):
        # print("============= MODE = 1 =============")
        self.deal(numarr)
        # print("============= MODE = 2 =============")
        self.deal2(numarr)

        # print("============= MERGE =============")
        self.mode_1_solution = set(tuple(x) if isinstance(x, list) else x for x in self.mode_1_solution)
        self.mode_2_solution = set(tuple(x) if isinstance(x, list) else x for x in self.mode_2_solution) - self.mode_1_solution

        self.mode_1_solution_raw = set(tuple(x) if isinstance(x, list) else x for x in self.mode_1_solution_raw)
        self.mode_2_solution_raw = set(tuple(x) if isinstance(x, list) else x for x in self.mode_2_solution_raw) - self.mode_1_solution_raw
        
        self.result_str_mode_1_list = []
        for sample in self.mode_1_solution_raw:
            self.result_str_mode_1_list.append(self.showresultstr(sample))

        self.result_str_mode_2_list = []
        for sample in self.mode_2_solution_raw:
            self.result_str_mode_2_list.append(self.showresultstr(sample))

        if len(self.mode_1_solution) + len(self.mode_2_solution) > 0:
            self.have_cnt = self.have_cnt + 1
            self.qa_save.append({
                "sample_id": f"{self.have_cnt:08d}",
                "problem": self.showresultstr(numarr),
                "solution_num": [len(self.mode_1_solution), len(self.mode_2_solution)],
                "mode_1_solution": self.result_str_mode_1_list,
                "mode_2_solution": self.result_str_mode_2_list,
                "problem_raw": numarr,
                "mode_1_solution_raw": list(self.mode_1_solution_raw),
                "mode_2_solution_raw": list(self.mode_2_solution_raw),
            })
        # print(f"Mode 1 solutions: \n{self.mode_1_solution}")
        # print(f"Mode 2 solutions: \n{self.mode_2_solution}")

def write_dict_list_to_jsonl(data: list[dict[str, any]], file_path: str) -> None:
    """
    Write a list of dictionaries to a JSONL file.

    Args:
        data: list of dictionaries
        file_path: output JSONL path
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Wrote {len(data)} records to {file_path}")
    except Exception as e:
        print(f"Error writing file: {e}")
       
if __name__ == "__main__":
    generator = MatchGen()
    # generator.search([-1,9,11,-1,9,-1,-1,5])

    with open("match_gen.jsonl", "w", encoding="utf-8") as f:
        generator.qa_save = []
        generator.have_cnt = 0

        # Calculate total iterations
        a_range = range(-1, 10)  # 11 values
        b_range = range(0, 10)   # 10 values
        c_range = range(10, 12)  # 2 values
        d_range = range(-1, 10)  # 11 values
        e_range = range(0, 10)   # 10 values
        g_range = range(-1, 10)  # 11 values
        h_range = range(0, 10)   # 10 values

        # a_range = range(-1, 0)  # 11 values
        # b_range = range(0, 2)   # 10 values
        # c_range = range(10, 12)  # 2 values
        # d_range = range(-1, 10)  # 11 values
        # e_range = range(0, 10)   # 10 values
        # g_range = range(-1, 10)  # 11 values
        # h_range = range(0, 10)   # 10 values

        # a_range = range(-1, 0)  # 11 values
        # b_range = range(0, 10)   # 10 values
        # c_range = range(10, 12)  # 2 values
        # d_range = range(-1, 0)  # 11 values
        # e_range = range(0, 10)   # 10 values
        # g_range = range(-1, 0)  # 11 values
        # h_range = range(0, 10)   # 10 values

        total_iterations = (len(a_range) * len(b_range) * len(c_range) * 
            len(d_range) * len(e_range) * len(g_range) * len(h_range))

        # Create a progress bar
        with tqdm(total=total_iterations, desc="Overall progress") as pbar:
            for a in a_range:
                for b in b_range:
                    for c in c_range:
                        for d in d_range:
                            for e in e_range:
                                for g in g_range:
                                    for h in h_range:
                                        generator.search([a, b, c, d, e, -1, g, h])
                                        pbar.update(1)

        write_dict_list_to_jsonl(generator.qa_save, "match_gen.jsonl")