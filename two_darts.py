from IPython import embed
d = 0.95

# params
pdd = 0.45
pds = 0.325
ptt = 0.4
pbb = 0.3
pbob = 0.4

pdm = 1 - pdd - pds
pts = 1 - ptt
pbs = (1 - pbb -pbob) / 20

board = range(1,21)
current_scores = range(0,502)
best_strategies_list = [[],[],[]]

# set expectation of winning = 1 and getting stuck on 1 to 0
for num in range(0,3):
	best_strategies_list[num].append({'strategy':'game finished','expectation':1})
	best_strategies_list[num].append({'strategy':'give-up','expectation':0})

a = pdd*(1 + pdm + (pdm*pdm))
b = 1 - (d*(pds + (pdm*pds) + (pdm*pdm*pds) + (pdm*pdm*pdm)))
e_2_1 = a / b
e_2_3 = pdd + d*(pdm+pds)*e_2_1
e_2_2 = pdd + (pdm*e_2_3) + (d*pds*e_2_1)

best_strategies_list[0].append({'strategy':'double one','expectation':e_2_1})
best_strategies_list[1].append({'strategy':'double one','expectation':e_2_2})
best_strategies_list[2].append({'strategy':'double one','expectation':e_2_3})

def evaluate_all_singles(current_score,current_dart):
	discount = 1
	if(current_dart == 3):
		current_dart = 0
		discount *= d
	possible_single_strategies = []
	for number in range(1,21):
		if(current_score - number >  1):
			strategy_expectation = discount*best_strategies_list[current_dart][current_score-number]['expectation']
			possible_single_strategies.append({'strategy': 'single ' +str(number), 'expectation': strategy_expectation})

	return possible_single_strategies

def evaluate_non_third_doubles(current_score, current_dart):
	possible_double_strategies = []
	for number in range(1,21):
		if(current_score - 2*number > -1 and current_score - 2* number != 1):
			strategy_expectation =(
			(pdd * best_strategies_list[current_dart][current_score - 2*number]['expectation'])+
			(pds * best_strategies_list[current_dart][current_score- number]['expectation'])+
			(pdm * best_strategies_list[current_dart][current_score]['expectation'])
			)
			possible_double_strategies.append({'strategy': 'double ' +str(number), 'expectation': strategy_expectation})
	return possible_double_strategies

def evaluate_third_double(current_score):
	possible_double_strategies = []
	for number in range(1,21):
		if(current_score - 2*number > -1 and current_score - 2* number != 1):
			z =(
			(pdd* best_strategies_list[0][current_score - 2*number]['expectation'])+
			(pds* best_strategies_list[0][current_score -number]['expectation'])+
			(pdm*pdd*best_strategies_list[1][current_score - 2*number]['expectation'])+
			(pdm*pds*best_strategies_list[1][current_score -number]['expectation'])+
			(pdm*pdm*pdd*best_strategies_list[2][current_score - 2*number]['expectation'])+
			(pdm*pdm*pds*best_strategies_list[2][current_score -number]['expectation'])
			)
			strategy_expectation = (d * z) / (1 - (d*pdm*pdm*pdm))
			possible_double_strategies.append({'strategy': 'double ' +str(number), 'expectation': strategy_expectation})
	return possible_double_strategies

def evaluate_all_doubles(current_score, current_dart):
	if(current_dart == 3):
		return evaluate_third_double(current_score)
	else:
		return evaluate_non_third_doubles(current_score, current_dart)

def evaluate_all_triples(current_score, current_dart):
	discount = 1
	if(current_dart == 3):
		current_dart = 0
		discount *= d
	possible_triple_strategies = []
	for number in range(1,21):
		if(current_score - 3*number > 1):
			strategy_expectation = discount*((ptt * best_strategies_list[current_dart][current_score-3*number]['expectation'])+(pts*best_strategies_list[current_dart][current_score-number]['expectation']))
			possible_triple_strategies.append({'strategy': 'triple ' +str(number), 'expectation': strategy_expectation})
	return possible_triple_strategies

# def evaluate_bull(current_score):
# 	if(current_score < 50 or current_score == 51):
# 		return []
# 	else:
# 		bullseye_expectation = d * (pbb * best_strategies_list[current_score-50]['expectation'] + (1-pbb) * best_strategies_list[current_score-25]['expectation'])
# 		return [{'strategy':'bullseye','expectation':bullseye_expectation}]

def find_best_strategy(current_score,throw):
	all_strategies = evaluate_all_singles(current_score,throw) + evaluate_all_doubles(current_score,throw) + evaluate_all_triples(current_score,throw)
	#  + evaluate_bull(current_score)
	max_strategy = {'strategy':'placeholder','expectation':0}
	for strategy in all_strategies:
		if strategy['expectation']> max_strategy['expectation']:
			max_strategy = strategy
	return max_strategy

def find_all_best_strategies(best_strategies_list):
	for score in range(3,502):
		for throw in range(3,0,-1):
			best_strategy = find_best_strategy(score,throw)
			best_strategies_list[throw-1].append(best_strategy)

def make_recommendation(current_score, best_strategies_list):
	print best_strategies_list[current_score]['strategy']

def print_strategy_table(best_strategies_list):
	throw_count = 1
	for throw in best_strategies_list:
		score_count = 0
		print "---------------------"
		print "throw - " + str(throw_count)
		for score in throw:
			row = "Score: " + str(score_count) + " - " "Strategy: " + score['strategy']
			print row
			score_count +=1
		throw_count += 1

find_all_best_strategies(best_strategies_list)


print_strategy_table(best_strategies_list)
embed()
# print best_strategies_list
# print evaluate_all_singles(5)
