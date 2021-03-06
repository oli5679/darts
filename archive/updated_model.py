from IPython import embed
from math import log, ceil, floor
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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
for i in range(1, 21):
    NEIGHBOURS[board[i]] = [board[i-1], board[i+1]]

OUTCOME_MAP = {
    3: [
        ['pts', 1, 'target'],
        ['ptsn', 1, 'upper'],
        ['ptsn', 1, 'lower'],
        ['pttn', 3, 'upper'],
        ['pttn', 3, 'lower'],
        ['ptt', 3, 'target']
    ],
    2:   [
        ['pdd', 2, 'target'],
        ['pddn', 2, 'upper'],
        ['pddn', 2, 'lower'],
        ['pds', 1, 'target'],
        ['pdsn', 1, 'upper'],
        ['pdsn', 1, 'lower'],
        ['pdm', 0, 'constant']
    ],
    1: [
        ['pss', 1, 'target'],
        ['pssn', 1, 'upper'],
        ['pssn', 1, 'lower']
    ],
    50: [
        ['pbb', 25, 'constant'],
        ['pbob', 50, 'constant']
    ],
    51: [
        ['pobb', 25, 'constant'],
        ['pobob', 50, 'constant']
    ]
}

for number in range(1, 21):
    OUTCOME_MAP[50].append(['pbs', number, 'constant'])
    OUTCOME_MAP[51].append(['pobs', number, 'constant'])


ACCURACY = {
    'pss': 0.95,
    'pssn': 0.025,
    'pdd': 0.45,
    'pds': 0.27,
    'pddn': 0,
    'pdsn': 0,
    'pdm': 0.28,
    'ptt': 0.45,
    'pts': 0.55,
    'pttn': 0,
    'ptsn': 0,
    'pbb': 0.35,
    'pbob': 0.45,
    'pbs': 0.01,
    'pobb': 0.34,
    'pobob': 0.46,
    'pobs': 0.01
}


def find_optimal_strategy(score, current_throw, strategy_values, accuracy):
    # returns array with strategy and expectation for all feasible strategies

    strat_evals = evaluate_all_non_doubles(score=score,
                                           current_throw=current_throw,
                                           strategy_values=strategy_values,
                                           accuracy=accuracy)
    double_eval = evaluate_double(score=score,
                                  current_throw=current_throw,
                                  strategy_values=strategy_values,
                                  accuracy=accuracy)

    strat_evals.append(double_eval)
    # return strategy and expectation for highest strategy
    optimal_strat = min(strat_evals, key=lambda x: x[1])
    return optimal_strat


def get_neighbours(target):
    targets = {'target': target}
    targets['lower'] = NEIGHBOURS[target][0]
    targets['upper'] = NEIGHBOURS[target][1]
    targets['constant'] = 1
    return targets


def evaluate_non_double_strategy(score, strategy, strategy_values, accuracy, current_throw):

    strategy_group, strategy_number = strategy
    outcomes = OUTCOME_MAP[strategy_group]
    next_throw = (current_throw + 1) % 3
    targets = get_neighbours(strategy_number)
    bust_prob = 0

    if current_throw == 2:
        expectation = 1
    else:
        expectation = 0
    for outcome in outcomes:
        probability, score_1, score_2 = outcome
        score_2 = targets[score_2]
        probability = accuracy[probability]
        outcome_score = score - (score_1 * score_2)
        if outcome_score <= 1:
            bust_prob += probability
        else:
            expectation += (probability *
                            strategy_values[next_throw][int(outcome_score)])
        if (outcome_score == 0 and score == 50):
            bust_prob -= probability
            expectation -= probability

    if bust_prob > 0.99999 and bust_prob < 1.00001:
        return 10000
    else:
        return (expectation + bust_prob)/(1-bust_prob)


def evaluate_all_non_doubles(score, current_throw, strategy_values, accuracy):
    non_double_evalulations = []
    for target in range(1, 21):
        for strat in [1, 3]:
            strat_eval = evaluate_non_double_strategy(score=score,
                                                      strategy=[strat, target],
                                                      strategy_values=strategy_values,
                                                      accuracy=accuracy,
                                                      current_throw=current_throw)

            non_double_evalulations.append(((strat, target), strat_eval))

    for strat in [50, 51]:
        strat_eval = evaluate_non_double_strategy(score=score,
                                                  strategy=[strat, 1],
                                                  strategy_values=strategy_values,
                                                  accuracy=accuracy,
                                                  current_throw=current_throw)

        non_double_evalulations.append(((strat, 1), strat_eval))

    return non_double_evalulations


def evaluate_double(score, current_throw, strategy_values, accuracy):
    miss = accuracy['pdm']
    s1, s2, s0, bust = (0, 0, 0, 0)
    target = min(score // 2, 20)
    targets = get_neighbours(target)
    for target_type in ['upper', 'lower', 'target']:
        if target_type == 'target':
            pdd = accuracy['pdd']
            pds = accuracy['pds']
        else:
            pdd = accuracy['pddn']
            pds = accuracy['pdsn']
        target = targets[target_type]
        if(score-target < 2):
            bust += pds
        else:
            s1 += pds*strategy_values[1][score-target]
            s2 += pds*strategy_values[2][score-target]
            s0 += pds*strategy_values[0][score-target]
        if(score-(2*target) < 2 and score - (2*target) != 0):
            bust += pdd
        elif(score - (2*target) >= 2):
            s1 += pdd*strategy_values[1][score-2*target]
            s2 += pdd*strategy_values[2][score-2*target]
            s0 += pdd*strategy_values[0][score-2*target]

    A = bust + (bust*miss) + (bust*miss*miss) + (miss*miss*miss)

    B = s0 + bust + (s1*miss) + (bust*miss) + (s2*miss*miss) \
        + (miss*miss) - miss*miss*accuracy['pdd']

    x0 = B / (1-A)
    x2 = s2 + (bust+miss)*x0 + 1 - accuracy['pdd']
    x1 = s1 + bust + bust*x0 + miss*x2
    double_evaluations = (x0, x1, x2)
    return ((2, target), double_evaluations[current_throw])


def derive_val_from_score(accuracy, strategy, strategy_values, score, current_throw):

    if strategy[0] == 2:
        return evaluate_double(score=score,
                               current_throw=current_throw,
                               strategy_values=strategy_values,
                               accuracy=accuracy)[1]
    else:
        return evaluate_non_double_strategy(score=score,
                                            strategy=strategy,
                                            strategy_values=strategy_values,
                                            accuracy=accuracy,
                                            current_throw=current_throw)


def gen_baseline_strategies(accuracy, max_score):

    baseline_strategy_values = np.empty((3, max_score))
    baseline_strategies = np.empty((3, max_score, 2))

    recommendations = pd.read_csv('strategy.csv', index_col=0)

    # filling in baseline strategies
    for score in range(2, 50):
        for throw in range(3):
            if score % 2 == 0 and score < 41:
                baseline_strategies[throw][score] = [2, int(score//2)]
            else:
                strategy = score - int(2**floor(log(score, 2)))
                baseline_strategies[throw][score] = [1, int(strategy)]

    for score, strategy in recommendations.iterrows():
        for throw in range(3):
            baseline_strategies[throw][score][0] = strategy[0]
            baseline_strategies[throw][score][1] = strategy[1]

    for score in range(137, max_score):
        for throw in range(3):
            if baseline_strategies[throw][score][0] == 0:
                baseline_strategies[throw][score] = [3, 20]

    for score in tqdm(range(2, max_score)):
        # start from 3rd throw and work backwards (so missing board and staying on same score can be tackled)
        for current_throw in range(3):
            baseline_strategy_values[current_throw][score] = derive_val_from_score(accuracy=accuracy,
                                                                                   strategy=baseline_strategies[
                                                                                       current_throw][score],
                                                                                   strategy_values=baseline_strategy_values,
                                                                                   score=score,
                                                                                   current_throw=current_throw)

    return (baseline_strategies, baseline_strategy_values)


def gen_optimal_strategies(accuracy, max_score):

    optimal_strategy_values = np.empty((3, max_score))
    optimal_strategies = np.empty((3, max_score, 2))

    for score in tqdm(range(2, max_score)):
        for current_throw in range(3):
            chosen_strategy = find_optimal_strategy(score=score,
                                                    current_throw=current_throw,
                                                    strategy_values=optimal_strategy_values,
                                                    accuracy=accuracy)

            optimal_strategies[current_throw][score] = chosen_strategy[0]
            optimal_strategy_values[current_throw][score] = chosen_strategy[1]

    return (optimal_strategies, optimal_strategy_values)


if __name__ == '__main__':
    #rec_source = 'http://dartsinfoworld.com/darts-checkout-table/'

    optimal_strategies, optimal_strategy_values = gen_optimal_strategies(
        ACCURACY, 502)
    baseline_strategies, baseline_strategy_values = gen_baseline_strategies(
        ACCURACY)
