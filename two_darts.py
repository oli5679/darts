from IPython import embed
from math import log10
d = 0.95

# params
pdd = 0.45
pds = 0.325
ptt = 0.4
pbb = 0.40
pbob = 0.4

pdm = 1 - pdd - pds
pts = 1 - ptt
pbs = (1 - pbb -pbob) / 20

board = range(1,21)
current_scores = range(0,502)
optimal_strategies = [[],[],[]]

# set expectation of winning = 1 and getting stuck on 1 to 0
for num in range(0,3):
	optimal_strategies[num].append({'strategy':'game finished','expectation':1})
	optimal_strategies[num].append({'strategy':'N/A','expectation':0})

a = pdd*(1 + pdm + (pdm*pdm))
b = 1 - (d*(pds + (pdm*pds) + (pdm*pdm*pds) + (pdm*pdm*pdm)))
e_2_1 = a / b
e_2_3 = pdd + d*(pdm+pds)*e_2_1
e_2_2 = pdd + (pdm*e_2_3) + (d*pds*e_2_1)

optimal_strategies[0].append({'strategy':'double one','expectation':e_2_1})
optimal_strategies[1].append({'strategy':'double one','expectation':e_2_2})
optimal_strategies[2].append({'strategy':'double one','expectation':e_2_3})

def calculate_discount_and_next_dart(current_throw):
	discount = 1
	if(current_throw == 3):
		current_throw = 0
		discount *= d
	return {'discount':discount,'next_throw_index':current_throw}

def evaluate_all_singles(current_score,current_throw):
	next_dart_dict = calculate_discount_and_next_dart(current_throw)
	possible_single_strategies = []
	for number in range(1,21):
		if(current_score - number >  1):
			strategy_expectation = (next_dart_dict['discount'])*optimal_strategies[next_dart_dict['next_throw_index']][current_score-number]['expectation']
			possible_single_strategies.append({'strategy': 'single ' +str(number), 'expectation': strategy_expectation})

	return possible_single_strategies

def evaluate_non_third_doubles(current_score, current_throw):
	possible_double_strategies = []
	for number in range(1,21):
		if(current_score - 2*number > -1 and current_score - 2* number != 1):
			strategy_expectation =(
			(pdd * optimal_strategies[current_throw][current_score - 2*number]['expectation'])+
			(pds * optimal_strategies[current_throw][current_score- number]['expectation'])+
			(pdm * optimal_strategies[current_throw][current_score]['expectation'])
			)
			possible_double_strategies.append({'strategy': 'double ' +str(number), 'expectation': strategy_expectation})
	return possible_double_strategies

def evaluate_third_double(current_score):
	possible_double_strategies = []
	for number in range(1,21):
		if(current_score - 2*number > -1 and current_score - 2* number != 1):
			z =(
			(pdd* optimal_strategies[0][current_score - 2*number]['expectation'])+
			(pds* optimal_strategies[0][current_score -number]['expectation'])+
			(pdm*pdd*optimal_strategies[1][current_score - 2*number]['expectation'])+
			(pdm*pds*optimal_strategies[1][current_score -number]['expectation'])+
			(pdm*pdm*pdd*optimal_strategies[2][current_score - 2*number]['expectation'])+
			(pdm*pdm*pds*optimal_strategies[2][current_score -number]['expectation'])
			)
			strategy_expectation = (d * z) / (1 - (d*pdm*pdm*pdm))
			possible_double_strategies.append({'strategy': 'double ' +str(number), 'expectation': strategy_expectation})
	return possible_double_strategies

def evaluate_all_doubles(current_score, current_throw):
	if(current_throw == 3):
		return evaluate_third_double(current_score)
	else:
		return evaluate_non_third_doubles(current_score, current_throw)

def evaluate_all_triples(current_score, current_throw):
	next_dart_dict = calculate_discount_and_next_dart(current_throw)
	possible_triple_strategies = []
	for number in range(1,21):
		if(current_score - 3*number > 1):
			strategy_expectation = (next_dart_dict['discount'])*((ptt * optimal_strategies[next_dart_dict['next_throw_index']][current_score-3*number]['expectation'])+(pts*optimal_strategies[next_dart_dict['next_throw_index']][current_score-number]['expectation']))
			possible_triple_strategies.append({'strategy': 'triple ' +str(number), 'expectation': strategy_expectation})
	return possible_triple_strategies

def evaluate_bull(current_score,current_throw):
	next_dart_dict = calculate_discount_and_next_dart(current_throw)
	if(current_score < 50 or current_score == 51):
		return []
	else:
		strategy_expectation = (pbb * optimal_strategies[next_dart_dict['next_throw_index']][current_score-50]['expectation']) + (pbob * optimal_strategies[next_dart_dict['next_throw_index']][current_score-25]['expectation'])
		for number in range(1,21):
			strategy_expectation += pbs*optimal_strategies[next_dart_dict['next_throw_index']][current_score-number]['expectation']
		strategy_expectation*=(next_dart_dict['discount'])
		return [{'strategy':'bullseye','expectation':strategy_expectation}]

def find_best_strategy(current_score,throw):
	all_strategies = evaluate_all_singles(current_score,throw) + evaluate_all_doubles(current_score,throw) + evaluate_all_triples(current_score,throw)+ evaluate_bull(current_score,throw)
	max_strategy = {'strategy':'placeholder','expectation':0}
	for strategy in all_strategies:
		if strategy['expectation']> max_strategy['expectation']:
			max_strategy = strategy
	return max_strategy

def find_all_best_strategies(optimal_strategies):
	for score in range(3,502):
		for throw in range(3,0,-1):
			best_strategy = find_best_strategy(score,throw)
			optimal_strategies[throw-1].append(best_strategy)

def make_recommendation(current_score, current_throw, optimal_strategies):
	print optimal_strategies[current_throw-1][current_score]['strategy']
	current_score_expectation=optimal_strategies[current_throw-1][current_score]['expectation']
	time = convert_expectation_to_avg_time(current_score_expectation,d)
	print "expected time left: " + str(time)

def convert_expectation_to_avg_time(expectation,d):
	ans = log10(expectation)/log10(d)
	return round(ans,2)

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

find_all_best_strategies(optimal_strategies)


print_strategy_table(optimal_strategies)
calculate_player_average(optimal_strategies)
