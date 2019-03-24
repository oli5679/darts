from IPython import embed
# params
pdd = 0.45
pds = 0.325
ptt = 0.4
pbb = 0.3
pbob = 0.4
delta = 0.95

board = range(1, 21)
current_scores = range(0, 502)
best_strategies_list = []

# set expectation of winning = 1
best_strategies_list.append({'strategy': 'game finished', 'expectation': 1})
best_strategies_list.append({'strategy': 'give-up', 'expectation': 0})
denominator = (1/delta) - 1 + pdd + pds + (delta*pds)
single_one_expectation = pdd/denominator
best_strategies_list.append(
    {'strategy': 'double one', 'expectation': single_one_expectation})


def evaluate_all_singles(current_score):
    possible_single_strategies = []
    for number in range(1, 21):
        if(current_score - number > 1):
            strategy_expectation = delta * \
                best_strategies_list[current_score-number]['expectation']
            possible_single_strategies.append(
                {'strategy': 'single ' + str(number), 'expectation': strategy_expectation})
    return possible_single_strategies


def evaluate_all_doubles(current_score):
    possible_double_strategies = []
    for number in range(1, 21):
        if(current_score - 2*number > -1 and current_score - 2 * number != 1):
            a = (pdd * best_strategies_list[current_score - 2*number]['expectation']) + (
                pds * best_strategies_list[current_score - number]['expectation'])
            b = 1 - delta + (delta * pdd) + (delta*pds)
            strategy_expectation = (a * delta) / b
            possible_double_strategies.append(
                {'strategy': 'double ' + str(number), 'expectation': strategy_expectation})
    return possible_double_strategies


def evaluate_all_triples(current_score):
    possible_triple_strategies = []
    for number in range(1, 21):
        if(current_score - 3*number > 1):
            strategy_expectation = delta * ((ptt * best_strategies_list[current_score-3*number]['expectation'])+(
                1-ptt)*best_strategies_list[current_score-number]['expectation'])
            possible_triple_strategies.append(
                {'strategy': 'triple ' + str(number), 'expectation': strategy_expectation})
    return possible_triple_strategies


def evaluate_bull(current_score):
    if(current_score < 50 or current_score == 51):
        return []
    else:
        bullseye_expectation = delta * (pbb * best_strategies_list[current_score-50]['expectation'] + (
            1-pbb) * best_strategies_list[current_score-25]['expectation'])
        return [{'strategy': 'bullseye', 'expectation': bullseye_expectation}]


def find_best_strategy(current_score):
    all_strategies = evaluate_all_singles(current_score) + evaluate_all_doubles(
        current_score) + evaluate_all_triples(current_score) + evaluate_bull(current_score)
    max_strategy = {'strategy': 'placeholder', 'expectation': 0}
    for strategy in all_strategies:
        if strategy['expectation'] > max_strategy['expectation']:
            max_strategy = strategy
    return max_strategy


def find_all_best_strategies(best_strategies_list):
    for number in range(3, 502):
        best_strategy = find_best_strategy(number)
        best_strategies_list.append(best_strategy)


def make_recommendation(current_score, best_strategies_list):
    print best_strategies_list[current_score]['strategy']


def print_strategy_table(best_strategies_list):
    count = 0
    for score in best_strategies_list:
        row = "Score: " + str(count) + " - " "Strategy: " + score['strategy']
        print row
        count += 1


find_all_best_strategies(best_strategies_list)

print_strategy_table(best_strategies_list)
# print best_strategies_list
# print evaluate_all_singles(5)
