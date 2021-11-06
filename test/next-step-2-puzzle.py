


def next_step_to_puzzle():
    with open("test-data/next-step-1.0-in.txt", "rt") as f:
        with open ("../bat/bat-data/puzzle-1.0-in.txt", "wt") as f1:
            f1.write ("# Puzzle\n")
            oPzls = []
            while 1:
                Line = f.readline()
                if not Line: break
                if Line == "\n" or Line[0] == "#": continue
                i = 0; Pzl = ""
                while Line[i] != "|":  # < len(Pzl-1):
                    if Line[i] == "+": Pzl += "0"; i += 2
                    elif Line[i] == ".": Pzl += "0"; i += 1
                    else: Pzl += (Line[i]); i += 1
                if Pzl in oPzls: continue
                oPzls.append(Pzl)
                f1.write(Pzl+"\n")

if __name__ == "__main__":
    next_step_to_puzzle()