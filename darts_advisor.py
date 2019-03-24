import numpy as np
import pandas as pd


class Player():
    def __init__(self, discount_rate, accuracy):
        self.discount_rate = discount_rate
        self.accuracy = self.generate_accuracy(accuracy)
        self.strategy_values = np.zeros((3, 502))
        self.strategies = pd.DataFrame(index=range(502), columns=[
                                       'first', 'second', 'third'])
        self.add_finished_and_bust_strategy_values()
        self.add_double_one_strategy()
        self.find_all_optimal_strategies()

    def add_finished_and_bust_strategy_values(self):
        self.strategy_values[:, 0] = 1
        self.strategies.loc[0] = ('finished', 'finished', 'finished')
        self.strategies.loc[1] = ('bust', 'bust', 'bust')

    def generate_accuracy(self, accuracy):
        accuracy['pdm'] = 1 - accuracy['pdd'] - accuracy['pds']
        accuracy['pts'] = 1 - accuracy['ptt']
        accuracy['pbs'] = (1 - accuracy['pbb'] - accuracy['pbob']) / 20
        return accuracy

    def add_double_one_strategy(self):
        d = self.discount_rate
        pdd = self.accuracy['pdd']
        pds = self.accuracy['pds']
        pdm = self.accuracy['pdm']

        # solutions to similtaneous equations for strategy of double 1 on score 2 (only strategy that doesn't go bust!)
        e_2_1_denominator = 1 - \
            (d*(pds + (pdm*pds) + (pdm*pdm*pds) + (pdm*pdm*pdm)))
        e_2_1 = (pdd*(1 + pdm +
                      (pdm*pdm)))/e_2_1_denominator
        e_2_3 = pdd + d*(pdm+pds)*e_2_1
        e_2_2 = pdd + (pdm*e_2_3) + (d*pds*e_2_1)
        self.strategy_values[:, 2] = (e_2_1, e_2_2, e_2_3)
        self.strategies.loc[2] = ('double 1', 'double 1', 'double 1',)

    def find_all_optimal_strategies(self):
        for score in range(3, 502):
            # start from 3rd throw and work backwards
            for current_throw in range(2, -1, -1):
                self.find_optimal_strategy(score, current_throw)

    def find_optimal_strategy(self, score, current_throw):
        # find all strategies and expectations for given score/throw input
        all_strategies = (self.evaluate_all_singles(score, current_throw) +
                          self.evaluate_all_doubles(score, current_throw) +
                          self.evaluate_all_triples(score, current_throw) +
                          self.evaluate_bull(score, current_throw))
        # return strategy and expectation for highest strategy
        optimal = sorted(all_strategies, key=lambda x: x['expectation'])[-1]
        self.strategy_values[current_throw, score] = optimal['expectation']
        self.strategies.iloc[score, current_throw] = optimal['strategy']

    def generate_next_throw_details(self, current_throw):
        # what index shall we use to look up expectations? do we need to discount?
        discount = 1
        next_throw = current_throw + 1
        if(next_throw == 3):
            next_throw = 0
            discount = self.discount_rate
        return (discount, next_throw)

    def evaluate_all_singles(self, score, current_throw):
        discount, next_throw = self.generate_next_throw_details(current_throw)
        single_strategies = []
        for target in range(1, 21):
            if(score - target > 1):
                strategy_expectation = discount * \
                    self.strategy_values[next_throw, score-target]
                single_strategies.append(
                    {'strategy': 'single ' + str(target),
                     'expectation': strategy_expectation})
        return single_strategies

    def evaluate_all_doubles(self, score, current_throw):
        _, next_throw = self.generate_next_throw_details(current_throw)
        double_strategies = []
        for target in range(1, 21):
            if(score - 2*target > -1 and score - 2 * target != 1):
                pdd = self.accuracy['pdd']
                pds = self.accuracy['pds']
                pdm = self.accuracy['pdm']
                d = self.discount_rate
                if(current_throw == 2):
                    z = ((pdd * self.strategy_values[0, score - 2 * target]) +
                         (pds * self.strategy_values[0, score - target]) +
                         (pdm * pdd * self.strategy_values[1, score - 2 * target]) +
                         (pdm * pds * self.strategy_values[1, score - target]) +
                         (pdm * pdm * pdd * self.strategy_values[2, score - 2 * target]) +
                         (pdm * pdm * pds * self.strategy_values[2, score - target]))
                    strategy_expectation = (d * z) / (1 - (d*pdm*pdm*pdm))
                else:
                    strategy_expectation = (
                        (pdd * self.strategy_values[next_throw, score-2*target]) +
                        (pds * self.strategy_values[next_throw, score-target]) +
                        (pdm * self.strategy_values[next_throw, score]))
                double_strategies.append(
                    {'strategy': 'double ' + str(target), 'expectation': strategy_expectation})
        return double_strategies

    def evaluate_all_triples(self, score, current_throw):
        discount, next_throw = self.generate_next_throw_details(current_throw)
        triple_strategies = []
        for target in range(1, 21):
            if(score - 3*target > 1):
                strategy_expectation = \
                    discount*((self.accuracy['ptt'] * self.strategy_values[next_throw, score-3*target]) +
                              (self.accuracy['pts'] * self.strategy_values[next_throw, score-target]))
                triple_strategies.append(
                    {'strategy': 'triple ' + str(target), 'expectation': strategy_expectation})
        return triple_strategies

    def evaluate_bull(self, score, current_throw):
        discount, next_throw = self.generate_next_throw_details(current_throw)
        if(score < 50 or score == 51):
            return []
        else:
            strategy_expectation = ((self.accuracy['pbb'] * self.strategy_values[next_throw, score-50]) +
                                    (self.accuracy['pbob'] * self.strategy_values[next_throw, score-25]))
            for number in range(1, 21):
                strategy_expectation += self.accuracy['pbs'] * \
                    self.strategy_values[next_throw, score-number]
            strategy_expectation * discount
            return [{'strategy': 'bullseye', 'expectation': strategy_expectation}]
