from IPython import embed
from math import log, ceil, floor
import random
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt

board = [
    5,
    20,
    1,
    18,
    4,
    13,
    6,
    10,
    15,
    2,
    17,
    3,
    19,
    7,
    16,
    8,
    11,
    14,
    9,
    12,
    5,
    20
]

NEIGHBOURS = {}
for i in range(1,21):
    NEIGHBOURS[board[i]]=[board[i-1],board[i+1]]

OUTCOME_MAP = {
    'triple' : [
        ['pts', 1,'target']
        ['ptsn', 1, 'upper'],
        ['ptsn', 1, 'lower'],
        ['pttn', 3,'upper'],
        ['pttn', 3, 'lower'],
        ['ptt', 3, 'target']
    ],
    'single' : [
        ['pss', 1, 'target']
        ['pssn',1 , 'upper'],
        ['pssn', 1, 'lower'],
    ],
    'bull': [
        ['pbb',25, 'constant'],
        ['pbob', 50, 'constant']
    ], 
    'outer_bull':[
        ['pobb',25, 'constant'],
        ['pobob', 50, 'constant']
    ]
}

ACCURACY = {
'pss': 0.95,
'pssn':0.025,
'pdd': 0.45,
'pds' : 0.27,
'pddn':0,
'pdsn':0,
'pdm':0.28,
'ptt' : 0.45,
'pts':0.55,
'pttn':0,
'ptsn':0,
'pbb' : 0.35,
'pbob' : 0.45,
'pobb':0.34,
'pobob':0.46
}

BUST_VALUE = 2
M = 4000

for number in range(1,21):
    STRATEGY_MAP['bull'].append(['pbs', number,'constant'])
    STRATEGY_MAP['outer_bull'].append(['pobs',number,'constant'])

def find_optimal_strategy(score, current_throw, strategy_values):
    #returns array with strategy and expectation for all feasible strategies
    all_strategies = evaluate_all_non_doubles(score=score, current_throw = current_throw, strategy_values = strategy_values) + \
    evaluate_double(score=score, current_throw=current_throw, strategy_values=strategy_values)
    # return strategy and expectation for highest strategy
    optimal_strat = min(all_strategies, key = lambda x: x[1])
    return optimal_strat

def get_targets(strategy_number):
    targets = {'target':strategy_number}
    targets['lower']=NEIGHBOURS[strategy_number][0]
    targets['upper']=NEIGHBOURS[strategy_number][1]
    targets['constant'] = 1
    return targets

def evaluate_non_double_strategy(score, strategy, strategy_values, accuracy, throw_number):
    strategy_group, strategy_number = strategy
    outcomes = STRATEGY_MAP[strategy_group]
    next_throw = (current_throw + 1) % 3
    targets = get_targets(strategy_number)
    bust_prob = 0
    if current_throw == 2:
        expectation = 1
    else:
        expectation = 0
    for outcome in outcomes:
        probability, score_1, score_2 = outcome
        outcome_score = current_score - (score_1 * score2)
        if outcome_score <= 0:
            bust_prob += probability
        else:
            expectation += accuracy[probability] * strategy_values[[next_throw, outcome_score]]
    
    return (expectation + bust_prob)/(1-bust_prob)

def evaluate_all_non_doubles(score,current_throw,strategy_values):
    non_double_strategies = []
    for target in range(1,21):
        single_eval = evaluate_non_double_strategy(score = score, 
                                    strategy = ['single',target], 
                                    strategy_values = strategy_values, 
                                    accuracy = accuracy,
                                    throw_number = throw_number)

        non_double_strategies.append([['single',target],single_eval])

        triple_eval = evaluate_non_double_strategy(score = score, 
                                    strategy = ['triple',target], 
                                    strategy_values = strategy_values, 
                                    accuracy = accuracy,
                                    throw_number = throw_number)

        non_double_strategies.append([['triple',target],triple_eval])

    bull_eval = evaluate_non_double_strategy(score = score, 
                                    strategy = ['bull',1], 
                                    strategy_values = strategy_values, 
                                    accuracy = accuracy,
                                    throw_number = throw_number)

    outer_bull_eval = evaluate_non_double_strategy(score = score, 
                                    strategy = ['outer_bull',1], 
                                    strategy_values = strategy_values, 
                                    accuracy = accuracy,
                                    throw_number = throw_number)

    non_double_strategies.append([['bull',1],bull_eval])

    non_double_strategies.append([['outer_bull',1],outer_bull_eval])
    
    return non_double_strategies

def evaluate_double(score,current_throw, strategy_values, accuracy):
    miss = accuracy['pdm']
    s1, s2, s0, bust = 0
    target = score // 2
    targets = get_targets(target)
    for target_type in ['upper','lower','target']:
        if target_type = 'target':
            pdd = accuracy['pdd']
            pds = accuracy['ds']
        else:
            pdd = accuracy['pddn']
            pds = accuracy['pdsn']
        target = targets[target_type]
        if(score-target<2):
            bust += accuracy['pds']
        else:
            s1 += pds*strategy_values[1][score-target]
            s2 += pds*strategy_values[2][score-target]
            s0 += pds*strategy_values[0][score-target]
        if(score-(2*target)<2 and score - (2*target) != 0):
            bust+= pdd
        elif(score - (2*target) >- 2:
            s1 += pdd*strategy_values[1][score-2*target]
            s2 += pdd*strategy_values[2][score-2*target]
            s0 += pdd*strategy_values[0][score-2*target]
        
    #keep the notes. This algebra is fiddly and you could easily have screwed it up.
    A = bust + s2 + miss*(1+s0) 
    B = miss*(miss+bust) + bust
    x1 = (bust + s1 + miss * A)/(1-bust- (miss*B))
    x3 = 1 + (bust + miss)*x1+s0
    x2 = bust + s2 + miss*x3 + bust*x1
    vals = [x1, x2, x3]
    return vals[current_throw]

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

def derive_val_from_score(accuracy, strategy, strategy_values,score, current_throw):
    strategy = player_strategy[current_dart][score]
    if strategy[0] == 'double':
        return evaluate_double(score=score, 
                            current_throw=current_throw,
                            current_dart=current_dart,
                            strategy_values)
    else:
        return evaluate_non_double_strategy()

def simulate_single_player_from_score(player_accuracy,player_strategy,score,current_dart):
    throws = 1
    while(score != 0):
        if(current_dart == 3):
            throws += 1
        current_dart = current_dart % 3
        strategy = player_strategy[current_dart][score]
        [score,current_dart] = simulate_strategy(score,strategy,player_accuracy, current_dart)
    return throws

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

def gen_strategy_skeleton():
    # Pandas

def gen_baseline_strategies_and_expectations(accuracy):
    baseline_strategies, baseline_strategy_values = gen_strategy_skeleton()

    #filling in baseline strategies
    for score in range(2,51):
        for throw in range(3):
            if score % 2 == 0 and score < 41:
                baseline_strategies[throw][score]=[2,score/2]
            else:
                strategy = score - int(2**floor(log(score,2)))
                baseline_strategies[throw][score]=[1,strategy]

    for strategy in recommendations:
        for throw in range(3):
            baseline_strategies[throw][strategy]=recommendations[strategy]

    for score in range(137,502):
        for throw in range(3):
            if baseline_strategies[throw][score] == 0:
                baseline_strategies[throw][score]=['triple',20]

    pds = accuracy['pds']
    pdd = accuracy['pdd']
    pdm = 1 - pds - pdd

    for score in range(3,502):
        # start from 3rd throw and work backwards (so missing board and staying on same score can be tackled)
        for current_throw in [0,1,2]:
             baseline_strategy_values[current_throw][score] = derive_val_from_score(accuracy =accuracy,
                                                                                    strategies=baseline_strategies,
                                                                                    baseline_strategybaseline_strategy_values,score,current_throw)

    return [baseline_strategies, baseline_strategy_values]



def gen_optimal_strategies(accuracy):
    optimal_strategies, optimal_strategy_values = gen_strategy_skeleton()
    pds = accuracy['pds']
    pdd = accuracy['pdd']
    pdm = 1 - pds - pdd
    t0,t1,t2 = evaluate_double(2,optimal_strategy_values,accuracy)
    optimal_strategy_values[0][2]=t0
    optimal_strategy_values[1][2]=t1
    optimal_strategy_values[2][2]=t2
    optimal_strategies[0][2]=[2,1]
    optimal_strategies[1][2]=[2,1]
    optimal_strategies[2][2]=[2,1]
    for score in range(3,502):
        # start from 3rd throw and work backwards (so missing board and staying on same score can be tackled)
        for current_throw in [0,1,2]:
            chosen_strategy = find_optimal_strategy(score,current_throw,optimal_strategy_values )
            optimal_strategies[current_throw][score] = chosen_strategy[0]
            optimal_strategy_values[current_throw][score] = chosen_strategy[1]

    return [optimal_strategies, optimal_strategy_values]

def sim_strategy_values(accuracy,strategy,n):
    #Pandas

    for score in tqdm(range(2,502)):
        for current_throw in [0,2,1]:
            val = calculate_val_from_score(accuracy,strategy,score,current_throw,n)
            sim_strategy_values[current_throw][score]=val
    return sim_strategy_values

def print_recommendations(recommendations,min,max):
    for current_dart in range(3):
            print('throw: ' + str(current_dart+1))
            print("--------------------------------")
            for score in range(min,max):
                clean_rec = convert_rec_to_string(recommendations[current_dart][score])
                print("score: " + str(score))
                print('reccomendation: ' + clean_rec)
            print("---------------------------------")


rec_source = 'http://dartsinfoworld.com/darts-checkout-table/'


optimal_strategies, optimal_strategy_values = gen_optimal_strategies(accuracy)

baseline_strategies, baseline_strategy_values = gen_baseline_strategies_and_expectations(accuracy)

#sim_optimal_strategy_values = sim_strategy_values(accuracy,optimal_strategies,m)

#sim_baseline_strategy_values =  sim_strategy_values(accuracy,baseline_strategies,m)

print('baseline: ' + str(baseline_strategy_values[0][501]))
print('improvement : ' + str(optimal_strategy_values[0][501]))

plt.plot(optimal_strategy_values[0][2:180],'red')
plt.plot(baseline_strategy_values[0][2:180],'yellow')
plt.show() 
