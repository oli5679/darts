# simulation not 100% accurate relative to closed form solns. because of fudge for going bust
def simulate_strategy(score, strategy, accuracy, current_dart):
    dart = random.random()
    target = strategy[1]
    if(strategy[0] == 'bull'):
        if(dart < accuracy['pbb']):
            new_score= int(score - 50)
        elif(dart < (accuracy['pbb']+accuracy['pbob'])):
            new_score= int(score - 25)
        else:
            random_single_score = ceil(random.random()*20)
            new_score= int(score - random_single_score)

    elif(strategy[0] == 'outer_bull'):
        if(dart < accuracy['pobb']):
            new_score= int(score - 50)
        elif(dart < (accuracy['pobb']+accuracy['pobob'])):
            new_score= int(score - 25)
        else:
            random_single_score = ceil(random.random()*20)
            new_score= int(score - random_single_score)

    elif(strategy[0]=='single'):
        new_score= int(score - target)
    
    elif(strategy[0]=='triple'):
        if(dart < accuracy['ptt']):
            new_score= int(score - (3 * target))
        else:
            new_score= int(score - target)

    elif(strategy[0]=='double'):
        if(dart < accuracy['pdd']):
            new_score = score - (2 * target)
        elif(dart < (accuracy['pdd']+accuracy['pds'])):
            new_score = score - target
        else:
            new_score = score
        if(new_score == 1):
            new_score= bust_value
            current_dart= 2
        else:
            new_score= int(new_score)

    return [new_score,current_dart+1]

def simulate_single_player_from_score(player_accuracy,player_strategy,score,current_dart):
    throws = 1
    while(score != 0):
        if(current_dart == 3):
            throws += 1
        current_dart = current_dart % 3
        strategy = player_strategy[current_dart][score]
        [score,current_dart] = simulate_strategy(score,strategy,player_accuracy, current_dart)
    return throws



def simulate_val_from_score(player_accuracy, player_strategy, score, current_throw, n):
    count, total = 0 
    for i in range(n):
        throws = simulate_single_player_from_score(player_accuracy=player_accuracy,
                                                    player_strategy=player_strategy,
                                                    score=score,
                                                    current_dart=current_dart)
        count += 1
        total += throws
    return total / count

def sim_strategy_values(accuracy,strategy,n):
    #Pandas

    for score in tqdm(range(2,502)):
        for current_throw in [0,2,1]:
            val = calculate_val_from_score(accuracy,strategy,score,current_throw,n)
            sim_strategy_values[current_throw][score]=val
    return sim_strategy_values