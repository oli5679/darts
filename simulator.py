import updated_model
import numpy as np

def sim_strat(score,throw,strategies,accuracy):
    count = 0
    ongoing_flag = True
    while ongoing_flag:
        strategy = strategies[throw][score]
        targets = updated_model.get_neighbours(strategy[1])
        outcomes = updated_model.OUTCOME_MAP[strategy[0]]
        probs = [accuracy[outcome[0]] for outcome in outcomes]
        outcome = outcomes[np.random.choice(range(len(outcomes)),p=probs)]
        
        throw += 1
        if throw == 3:
            throw = 0
            count += 1
        
        payoff = outcome[1] * targets[outcome[2]]
        if score - payoff == 0 and outcome[1] == 2:
            ongoing_flag = False
            break
        
        if score == 50 and outcome == 50:
            ongoing_flag = False
            break

        elif ongoing_flag and score - payoff <= 1:
            count += 1
        else:
            score = int(score - payoff)
    return count

def sim_expectations(score,throw,strategies,accuracy,num_sims):
    sims = [sim_strat(score,throw,strategies,accuracy) for x in range(num_sims)]
    return sum(sims)/num_sims