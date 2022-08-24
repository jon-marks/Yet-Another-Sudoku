

def tech_als_xz(Grid, Step, Cands, Methods):

    if T_ALS_XZ in Methods:

        # Look in ALSa order 1 and ALSb order 4.
        ALS1List = find_all_als_1st_order(Grid, Cands)
        ALS4List = find_all_als_4th_order(Grid, Cands)

        ALSa = (()); ALSb = ((), (), (), ())
        for ALSaU, ALSa[0] in ALS1List:
            for ALSbU, (ALSb[0], ALSb[1], ALSb[2], ALSb[3]) in ALS4List:
                if len(ALSaU & ALSbU) < 2: continue  # Check for two common cands btwn ALSa and ALSb
                if als_xz_elims(ALSaU, ALSa, ALSbu, ALSb, Cands, Step): return 0



        ALS2List = find_all_als_2nd_order(Grid, Cands)
        ALS3List = find_all_als_3rd_order(Grid, Cands)
    return -1



def find_all_als_1st_order(Grid, Cands):

    ALS1List = []
    for r0 in range(9):
        for c0 in range(9):
            if len(Cands[r0][c0]) == 2:
                ALS1List.append((sorted(Cands[r0][c0]), ((r0, c0, sorted(cands[r0][c0])))))
    return ALS1List

def find_all_als_2nd_order(Grid, Cands):

    ALS2List = []
    # look in rows
    for r0 in range(9):
        for c0 in range(8):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 3: continue
            for c1 in range(c0+1, 9):
                U1 = Cands[r0][c0] | Cands[r0][c1]
                if Grid[r0][c1] or len(U1) > 3: continue
                ALS2List.append((sorted(U1), ((r0, c0, sorted(Cands[r0][c0])), (r0, c1, sorted(Cands[r0][c1])))))
    # look in cols
    for c0 in range(9):
        for r0 in range(8):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 3: continue
            for r1 in range(r0+1, 9):
                U1 = Cands[r0][c0] | Cands[r1][c0]
                if Grid[r1][c0] or len(U1) > 3: continue
                ALS2List.append((sorted(U1), ((r0, c0, sorted(Cands[r0][c0])), (r1, c0, sorted(Cands[r1][c0])))))
    # look in boxes
    for rb, cb in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
        for h0 in range(8):
            r0, c0 = (rb+h0//3, cb+h0%3)
            if Grid[r0][c0] or len(Cands[r0][c0]) > 3: continue
            for h1 in range(h0+1, 9):
                r1, c1 = (rb+h1//3, cb+h1%3); U1 = Cands[ro][c0] | Cands[r1][c1]
                if Grid[r1][c1] or len(U1) > 3: continue
                ALS2List.append((sorted(U1), ((r0, c0, sorted(Cands[r0][c0])), (r1, c1, sorted(Cands[r1][c1])))))
    return ALS2List

def find_all_als_3rd_order(Grid, Cands):
    ALS3List = []
    # look in rows
    for r0 in range(9):
        for c0 in range(7):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 4: continue
            for c1 in range(c0+1, 8):
                U1 = Cands[r0][c0] | Cands[r0][c1]
                if Grid[r0][c1] or len(U1) > 4: continue
                for c2 in range(c1+1, 9):
                    U2 = U1 | Cands[r0][c2]
                    if Grid[r0][c2] or len(U2) > 4: continue
                    ALS3List.append((sorted(U2), ((r0, c0, sorted(Cands[r0][c0])), (r0, c1, sorted(Cands[r0][c1])), (r0, c2, sorted(Cands[r0][c2])))))
    # look in cols
    for c0 in range(9):
        for r0 in range(7):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 4: continue
            for r1 in range(r0+1, 8):
                U1 = Cands[r0][c0] | Cands[r1][c0]
                if Grid[r1][c0] or len(U1) > 4: continue
                for r2 in range(r1+1, 9):
                    U2 = U1 | Cands[r2][c0]
                    if Grid[r2][c0] or len(U2) > 4: continue
                    ALS3List.append((sorted(U2), ((r0, c0, sorted(Cands[r0][c0])), (r1, c0, sorted(Cands[r1][c0])), (r2, c0, sorted(Cands[r2][c0])))))
    # look in boxes
    for rb, cb in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
        for h0 in range(7):
            r0, c0 = (rb+h0//3, cb+h0%3)
            if Grid[r0][c0] or len(Cands[r0][c0]) > 4: continue
            for h1 in range(h0+1, 8):
                r1, c1 = (rb+h1//3, cb+h1%3); U1 = Cands[ro][c0] | Cands[r1][c1]
                if Grid[r1][c1] or len(U1) > 4: continue
                for h2 in range(h1+1, 9):
                    r2, c2 = (rb+h2//3, cb+h2%3); U2 = U1 | Cands[r2][c2]
                    if Grid[r2][c2] or len(U2) > 4: continue
                    ALS3List.append((sorted(U2), ((r0, c0, sorted(Cands[r0][c0])), (r1, c1, sorted(Cands[r1][c1])), (r2, c2, sorted(Cands[r2][c2])))))
    return ALS3List

def find_all_als_4rd_order(Grid, Cands):
    ALS4List = []
    # look in rows
    for r0 in range(9):
        for c0 in range(6):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 5: continue
            for c1 in range(c0+1, 7):
                U1 = Cands[r0][c0] | Cands[r0][c1]
                if Grid[r0][c1] or len(U1) > 5: continue
                for c2 in range(c1+1, 8):
                    U2 = U1 | Cands[r0][c2]
                    if Grid[r0][c2] or len(U2) > 5: continue
                    for c3 in range(c2+1, 9):
                        U3 = U2 | Cands[r0][c3]
                        if Grid[r0][c3] or len(U3) > 5: continue
                        ALS4List.append((sorted(U3), ((r0, c0, sorted(Cands[r0][c0])), (r0, c1, sorted(Cands[r0][c1])), (r0, c2, sorted(Cands[r0][c2])), (r0, c3, sorted(Cands[r0][c3])))))
    # look in cols
    for c0 in range(9):
        for r0 in range(6):
            if Grid[r0][c0] or len(Cands[r0][c0]) > 5: continue
            for r1 in range(r0+1, 7):
                U1 = Cands[r0][c0] | Cands[r1][c0]
                if Grid[r1][c0] or len(U1) > 5: continue
                for r2 in range(r1+1, 8):
                    U2 = U1 | Cands[r2][c0]
                    if Grid[r2][c0] or len(U2) > 5: continue
                    for r3 in range(r2+1, 9):
                        U3 = U2 | Cands[r3][c0]
                        if Grid[r3][c0] or len(U3) > 5: continue
                        ALS4List.append((sorted(U3), ((r0, c0, sorted(Cands[r0][c0])), (r1, c0, sorted(Cands[r1][c0])), (r2, c0, sorted(Cands[r2][c0])), (r3, c0, sorted(Cands[r3][c0])))))
    # look in boxes
    for rb, cb in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
        for h0 in range(6):
            r0, c0 = (rb+h0//3, cb+h0%3)
            if Grid[r0][c0] or len(Cands[r0][c0]) > 5: continue
            for h1 in range(h0+1, 7):
                r1, c1 = (rb+h1//3, cb+h1%3); U1 = Cands[ro][c0] | Cands[r1][c1]
                if Grid[r1][c1] or len(U1) > 5: continue
                for h2 in range(h1+1, 8):
                    r2, c2 = (rb+h2//3, cb+h2%3); U2 = U1 | Cands[r2][c2]
                    if Grid[r2][c2] or len(U2) > 5: continue
                    for h3 in range(h2+1, 9):
                        r3, c3 = (rb+h3//3, cb+h3%3); U3 = U2 | Cands[r3][c3]
                        if Grid[r3][c3] or len(U3) > 5: continue
                        ALS4List.append((sorted(U3), ((r0, c0, sorted(Cands[r0][c0])), (r1, c1, sorted(Cands[r1][c1])), (r2, c2, sorted(Cands[r2][c2])), (r3, c3, sorted(Cands[r3][c3])))))
    return ALS4List

def als_xz_elims(ALSa, ALSb, Ua, Ub, Step, Cands):

    SharedCands = {}; RCC = []
    for Cand in ALSaU & ALSbU:
        for ra0, ca0, Candsa0 in ALSa:
            if Cand in Candsa0:
                for rb0, cb0, Candsb0 in ALSb:
                    if Cand in Candsb0:
                        Lk = how_ccells_linked(ra0, ca0, Cand, rb0, cb0, Cand, Cands)
                        if Cand in SharedCands.keys:
                            if not Lk: SharedCands[Cand][0] = False
                            SharedCands[Cand][1].append((ra0, ca0, rb0, cb0))
                        else:
                            SharedCands[Cand] = [True if Lk else False, [(ra0, ca0, rb0, cb0)]]
        if SharedCands[Cand][0]: RCC.append(Cand)

    if len(RCC) == 1:  # singly linked ALS-XZ found. What can be eliminated?
    RCCs = 0
    for SCProps in SharedCands.values():
        if SCProps[0]: RCCs += 1
    if not RCCS: return False
    #  Valid ALS-XZ found  are their elims.  Also indicate


    return False
