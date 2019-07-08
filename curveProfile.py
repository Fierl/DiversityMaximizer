# This script computes the curve profile of a road, which is created through AsFault.

# This seperates the segments from the dictionary into their overall category
def seperateSegments(dic):
    l_turns = []
    r_turns = []
    straights = []
    count = 1
    netW = dic['network']
    nodes = netW['nodes']
    # Get the keys of all the segments
    while count < 1000:
        # try because of the inconsitence of the key values
        try:
            node = nodes[str(count)]
            name = node['key']
            seg_id = int(node['seg_id'])
            infos = name.split('_')
            # seperate the segments and put them into the needed list
            if name.startswith('straight'):
                length = float(infos[1])
                tup = (seg_id, length)
                straights.append(tup)
            elif name.startswith('root'):
                count = count
            else:
                if name.startswith('l'):
                    angle = int(infos[2])
                    pivot = float(infos[3])
                    tup = (seg_id, angle, pivot)
                    l_turns.append(tup)
                else:
                    angle = int(infos[2])
                    pivot = float(infos[3])
                    tup = (seg_id, angle, pivot)
                    r_turns.append(tup)
            count = count + 1
        except KeyError:
            count = count + 1
    return straights, l_turns, r_turns


# put the straight segments from a list into their bins
def putStraightsIntoBins(straights):
    xSStraight = []
    sStraight = []
    lStraight = []
    xLStraight = []
    for straight in straights:
        length = straight[1]
        if length < 75:
            xSStraight.append(straight)
        elif length > 74 and length < 150:
            sStraight.append(straight)
        elif length < 250 and length > 149:
            lStraight.append(straight)
        else:
            xLStraight.append(straight)
        return xSStraight,sStraight,lStraight,xLStraight


# bins for the road segments l_ = left, r_ = right, l = large,
# s = short, S = sharp, N = normal, W = wide
# put the l_turn segments from a list into their six bins
def putL_TurnsIntoBins(l_turns):
    l_sSCurve = [] 
    l_sNCurve = []
    l_sWCurve = []
    l_lSCurve = []
    l_lNCurve = []
    l_lWCurve = []
    for turn in l_turns:
        pivot = turn[2]
        angle = abs(turn[1])
        if pivot < 25:
            if angle < 4:
                l_sSCurve.append(turn)
            elif angle > 44 and angle < 90:
                l_sNCurve.append(turn)
            else:
                l_sWCurve.append(turn)
        else:
            if angle < 45:
                l_lSCurve.append(turn)
            elif angle > 44 and angle < 90:
                l_lNCurve.append(turn)
            else:
                l_lWCurve.append(turn)            
    return l_sSCurve, l_sNCurve, l_sWCurve, l_lSCurve, l_lNCurve, l_lWCurve


# 6 bins for the road segments l_ = left, r_ = right, l = large,
# s = short, S = sharp, N = normal, W = wide
# put the r_turn segments from a list into their six bins
def putR_TurnsIntoBins(r_turns):
    r_sSCurve = [] 
    r_sNCurve = []
    r_sWCurve = []
    r_lSCurve = []
    r_lNCurve = []
    r_lWCurve = []           
    for turn in r_turns:
        pivot = turn[2]
        angle = abs(turn[1])
        if pivot < 25:
            if angle < 45:
                r_sSCurve.append(turn)
            elif angle > 44 and angle < 90:
                r_sNCurve.append(turn)
            else:
                r_sWCurve.append(turn)
        else:
            if angle < 45:
                r_lSCurve.append(turn)
            elif angle > 44 and angle < 90:
                r_lNCurve.append(turn)
            else:
                r_lWCurve.append(turn)
    return r_sSCurve, r_sNCurve, r_sWCurve, r_lSCurve, r_lNCurve, r_lWCurve


# order the bin values from small to large and sharp to wide    
def orderCurveIntoBins(r_turns, l_turns):
    r_turnValues = [len(r_turns[0]), len(r_turns[1]), len(r_turns[2]),len(r_turns[3]), len(r_turns[4]), len(r_turns[5])]
    l_turnValues = [len(l_turns[0]), len(l_turns[1]), len(l_turns[2]),len(l_turns[3]), len(l_turns[4]), len(l_turns[5])]
    binValues = []
    binValues.extend(l_turnValues)
    binValues.extend(r_turnValues)
    return binValues


# gets the curve values from the test
def getCurveBinsValue(dic):
    straights, l_turns, r_turns = seperateSegments(dic)
    l_turnSegments = putL_TurnsIntoBins(l_turns)
    r_turnSegments = putR_TurnsIntoBins(r_turns)
    cProfile = orderCurveIntoBins(l_turnSegments, r_turnSegments)
    return cProfile
