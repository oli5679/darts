import pytest 
import updated_model
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
for i in range(1,21):
    NEIGHBOURS[board[i]]=[board[i-1],board[i+1]]

OUTCOME_MAP = {
    3 : [
        ['pts', 1,'target'],
        ['ptsn', 1, 'upper'],
        ['ptsn', 1, 'lower'],
        ['pttn', 3,'upper'],
        ['pttn', 3, 'lower'],
        ['ptt', 3, 'target']
    ],
    1 : [
        ['pss', 1, 'target'],
        ['pssn',1 , 'upper'],
        ['pssn', 1, 'lower']
    ],
    50: [
        ['pbb',25, 'constant'],
        ['pbob', 50, 'constant']
    ], 
    51:[
        ['pobb',25, 'constant'],
        ['pobob', 50, 'constant']
    ]
}

for number in range(1,21):
    OUTCOME_MAP[50].append(['pbs', number,'constant'])
    OUTCOME_MAP[51].append(['pobs',number,'constant'])

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
'pbs':0.01,
'pobb':0.34,
'pobob':0.46,
'pobs':0.01
}


OPTIMAL_STRATEGY_VALUES = np.ones((502,3))*10000
OPTIMAL_STRATEGIES = np.zeros((502,3,2))

def test_get_neighbours():
    n_1 = updated_model.get_neighbours(1)
    assert sorted(n_1.values()) == [1,1,18,20]
    assert sorted(n_1.keys()) == ['constant','lower','target','upper']
    n_15 = updated_model.get_neighbours(15)
    assert sorted(n_15.values()) == [1,2,10,15]
    assert sorted(n_15.keys())  == ['constant','lower','target','upper']

def test_bust_strategies_return_10000():
   
    for target in range(1,21):
        for throw in range(3):
            single_strat_eval = updated_model.evaluate_non_double_strategy(score = 2, 
                                strategy = (1,target), 
                                strategy_values=OPTIMAL_STRATEGY_VALUES, 
                                accuracy = ACCURACY, 
                                current_throw=throw)
           
            triple = updated_model.evaluate_non_double_strategy(score = 2, 
                                strategy = (3,target), 
                                strategy_values=OPTIMAL_STRATEGY_VALUES, 
                                accuracy = ACCURACY, 
                                current_throw=throw)
            assert single_strat_eval == 10000

            assert single_strat_eval == 10000

def test_bust_bull_strategies_return_10000():
   
    for throw in range(3):
        bull_strat_eval = updated_model.evaluate_non_double_strategy(score = 2, 
                                strategy = (50,1), 
                                strategy_values=OPTIMAL_STRATEGY_VALUES, 
                                accuracy = ACCURACY, 
                                current_throw=throw)
           
        outer_bull_strat_eval = updated_model.evaluate_non_double_strategy(score = 2, 
                                strategy = (50,1), 
                                strategy_values=OPTIMAL_STRATEGY_VALUES, 
                                accuracy = ACCURACY, 
                                current_throw=throw)
        assert bull_strat_eval == 10000

        assert outer_bull_strat_eval == 10000


def test_double_one_strategy():
    throw_one_eval = updated_model.evaluate_double(score=2,
                            current_throw=0, 
                            strategy_values=OPTIMAL_STRATEGY_VALUES, 
                            accuracy=ACCURACY)
    
    throw_two_eval = updated_model.evaluate_double(score=2,
                            current_throw=1, 
                            strategy_values=OPTIMAL_STRATEGY_VALUES, 
                            accuracy=ACCURACY)
    
    throw_three_eval = updated_model.evaluate_double(score=2,
                            current_throw=2, 
                            strategy_values=OPTIMAL_STRATEGY_VALUES, 
                            accuracy=ACCURACY)

    #for now just checking non-zero. Will add explicit calculations later
    assert throw_one_eval[1] > 0
    assert throw_two_eval[1] > 0
    assert throw_three_eval[1] > 0

def test_find_first_double():
    first_dart_strat = updated_model.find_optimal_strategy(score = 2, 
                                        current_throw = 0, 
                                        strategy_values = OPTIMAL_STRATEGY_VALUES,
                                        accuracy=ACCURACY)

    second_dart_strat = updated_model.find_optimal_strategy(score = 2, 
                                        current_throw = 1, 
                                        strategy_values = OPTIMAL_STRATEGY_VALUES,
                                        accuracy=ACCURACY)

    third_dart_strat = updated_model.find_optimal_strategy(score = 2, 
                                        current_throw = 2, 
                                        strategy_values = OPTIMAL_STRATEGY_VALUES,
                                        accuracy=ACCURACY)
    
    assert first_dart_strat[0] == (2,1)
    assert second_dart_strat[0] == (2,1)
    assert third_dart_strat[0] == (2,1)