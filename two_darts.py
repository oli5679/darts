from IPython import embed
from math import log10

# 'discount' by 'd' for every 3 darts thrown in order to evalaute relative speen of paths
d = 0.95

# how accurate is our player?
accuracy = {
'pdd': 0.45,
'pds' : 0.325,
'ptt' : 0.4,
'pbb' : 0.40,
'pbob' : 0.4
}

def find_optimal_strategies(accuracy):
	# data structure - 3 lists, one for 1st, 2nd and 3rd throw - within list, index = score
	optimal_strategies = [[],[],[]]

	# calculating remaining accuracy parameters
	accuracy['pdm'] = 1 - accuracy['pdd'] - accuracy['pds']
	accuracy['pts'] = 1 - accuracy['ptt']
	accuracy['pbs'] = (1 - accuracy['pbb'] -accuracy['pbob']) / 20

	# 0 = won, 1 = bust!
	for num in range(0,3):
		optimal_strategies[num].append({'strategy':'game finished','expectation':1})
		optimal_strategies[num].append({'strategy':'N/A','expectation':0})

	# solutions to similtaneous equations for strategy of double 1 on score 2 (only strategy that doesn't go bust!)
	e_2_1_denominator = 1 - (d*(accuracy['pds'] + (accuracy['pdm']*accuracy['pds']) + (accuracy['pdm']*accuracy['pdm']*accuracy['pds']) + (accuracy['pdm']*accuracy['pdm']*accuracy['pdm'])))
	e_2_1 = (accuracy['pdd']*(1 + accuracy['pdm'] + (accuracy['pdm']*accuracy['pdm'])))/e_2_1_denominator
	e_2_3 = accuracy['pdd'] + d*(accuracy['pdm']+accuracy['pds'])*e_2_1
	e_2_2 = accuracy['pdd'] + (accuracy['pdm']*e_2_3) + (d*accuracy['pds']*e_2_1)
	optimal_strategies[0].append({'strategy':'double one','expectation':e_2_1})
	optimal_strategies[1].append({'strategy':'double one','expectation':e_2_2})
	optimal_strategies[2].append({'strategy':'double one','expectation':e_2_3})
	# start from lowest scores and work up
	for score in range(3,502):
		# start from 3rd throw and work backwards (so missing board and staying on same score can be tackled)
		for current_throw in range(3,0,-1):
			optimal_strategy = find_optimal_strategy(score,current_throw,optimal_strategies)
			optimal_strategies[current_throw-1].append(optimal_strategy)
	return optimal_strategies

def find_optimal_strategy(score,current_throw,optimal_strategies):
	# find all strategies and expectations for given score/throw input
	all_strategies = evaluate_all_singles(score,current_throw,optimal_strategies) + evaluate_all_doubles(score,current_throw,optimal_strategies) + evaluate_all_triples(score,current_throw,optimal_strategies)+ evaluate_bull(score,current_throw,optimal_strategies)
	# return strategy and expectation for highest strategy
	optimal = {'strategy':'placeholder','expectation':0}
	for strategy in all_strategies:
		if strategy['expectation']> optimal['expectation']:
			optimal = strategy
	return optimal

# what index shall we use to look up expectations? do we need to discount?
def generate_next_throw_dict(current_throw):
	discount = 1
	if(current_throw == 3):
		current_throw = 0
		discount *= d
	return {'discount':discount,'next_throw_index':current_throw}

def evaluate_all_singles(score,current_throw,optimal_strategies):
	next_throw_dict = generate_next_throw_dict(current_throw)
	possible_single_strategies = []
	for target in range(1,21):
		if(score - target >  1):
			strategy_expectation = (next_throw_dict['discount'])*optimal_strategies[next_throw_dict['next_throw_index']][score-target]['expectation']
			possible_single_strategies.append({'strategy': 'single ' +str(target), 'expectation': strategy_expectation})
	return possible_single_strategies

def evaluate_all_doubles(score, current_throw,optimal_strategies):
	if(current_throw == 3):
		return evaluate_third_doubles(score, optimal_strategies)
	else:
		return evaluate_non_third_doubles(score, current_throw,optimal_strategies)

def evaluate_all_triples(score, current_throw,optimal_strategies):
	next_throw_dict = generate_next_throw_dict(current_throw)
	possible_triple_strategies = []
	for target in range(1,21):
		if(score - 3*target > 1):
			strategy_expectation = (next_throw_dict['discount'])*((accuracy['ptt'] * optimal_strategies[next_throw_dict['next_throw_index']][score-3*target]['expectation'])+(accuracy['pts']*optimal_strategies[next_throw_dict['next_throw_index']][score-target]['expectation']))
			possible_triple_strategies.append({'strategy': 'triple ' +str(target), 'expectation': strategy_expectation})
	return possible_triple_strategies

def evaluate_bull(score,current_throw,optimal_strategies):
	next_throw_dict = generate_next_throw_dict(current_throw)
	if(score < 50 or score == 51):
		return []
	else:
		strategy_expectation = (accuracy['pbb'] * optimal_strategies[next_throw_dict['next_throw_index']][score-50]['expectation']) + (accuracy['pbob'] * optimal_strategies[next_throw_dict['next_throw_index']][score-25]['expectation'])
		for number in range(1,21):
			strategy_expectation += accuracy['pbs']*optimal_strategies[next_throw_dict['next_throw_index']][score-number]['expectation']
		strategy_expectation*=(next_throw_dict['discount'])
		return [{'strategy':'bullseye','expectation':strategy_expectation}]

def evaluate_non_third_doubles(score, current_throw,optimal_strategies):
	possible_double_strategies = []
	for target in range(1,21):
		if(score - 2*target > -1 and score - 2* target != 1):
			strategy_expectation =(
			(accuracy['pdd'] * optimal_strategies[current_throw][score - 2*target]['expectation'])+
			(accuracy['pds'] * optimal_strategies[current_throw][score- target]['expectation'])+
			(accuracy['pdm'] * optimal_strategies[current_throw][score]['expectation'])
			)
			possible_double_strategies.append({'strategy': 'double ' +str(target), 'expectation': strategy_expectation})
	return possible_double_strategies

def evaluate_third_doubles(score,optimal_strategies):
	possible_double_strategies = []
	for target in range(1,21):
		if(score - 2*target > -1 and score - 2* target != 1):
			z =(
			(accuracy['pdd']* optimal_strategies[0][score - 2*target]['expectation'])+
			(accuracy['pds']* optimal_strategies[0][score -target]['expectation'])+
			(accuracy['pdm']*accuracy['pdd']*optimal_strategies[1][score - 2*target]['expectation'])+
			(accuracy['pdm']*accuracy['pds']*optimal_strategies[1][score -target]['expectation'])+
			(accuracy['pdm']*accuracy['pdm']*accuracy['pdd']*optimal_strategies[2][score - 2*target]['expectation'])+
			(accuracy['pdm']*accuracy['pdm']*accuracy['pds']*optimal_strategies[2][score -target]['expectation'])
			)
			strategy_expectation = (d * z) / (1 - (d*accuracy['pdm']*accuracy['pdm']*accuracy['pdm']))
			possible_double_strategies.append({'strategy': 'double ' +str(target), 'expectation': strategy_expectation})
	return possible_double_strategies

def convert_expectation_to_avg_time(expectation,d):
	ans = log10(expectation)/log10(d)
	return round(ans,2)

# methods not used in 'find optimal strategies'

def make_recommendation(score, current_throw, optimal_strategies):
	print optimal_strategies[current_throw-1][score]['strategy']
	score_expectation=optimal_strategies[current_throw-1][score]['expectation']
	time = convert_expectation_to_avg_time(score_expectation,d)
	print "expected time left: " + str(time)


def calculate_player_average(optimal_strategies):
	starting_expectation = optimal_strategies[0][501]['expectation']
	avg_time = convert_expectation_to_avg_time(starting_expectation,d)
	print "Average: " + str(round(501/avg_time,2))

def print_strategy_table(optimal_strategies):
	throw_count = 1
	for throw_no in optimal_strategies:
		score_count = 0
		print "---------------------"
		print "throw_no - " + str(throw_count)
		for score in throw_no:
			if(score['expectation'] != 0):
				avg_time = convert_expectation_to_avg_time(score['expectation'],d)
			else:
				avg_time = 'N/A'
			row = "Score: " + str(score_count) + " - Strategy: " + score['strategy'] + " - Avg Time: " + str(avg_time)
			print row
			score_count +=1
		throw_count += 1

optimal_strategies = find_optimal_strategies(accuracy)
print_strategy_table(optimal_strategies)
calculate_player_average(optimal_strategies)
