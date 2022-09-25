class HypotheticalCalculation:
    def __init__(self,col_name,function_relation=None, symbolic_history=None):
        if symbolic_history is None:
            self.symbolic_history = frozenset()
        else:
            self.symbolic_history = symbolic_history
        self.col_name = col_name
        self.function_relation = function_relation
    def __str__(self):
        r'''
        Returns a human-readable format of the calculation.

        :return:
        '''
        out = tuple( str(symb_part) for symb_part in self.symbolic_representation() )
        out = str(out)
        return(out)

    def symbolic_representation(self):
        r'''
        Generates the symbolic representation of the calculation.

        :return:
        '''
        return((self.col_name, self.function_relation, self.symbolic_history))


class Calculation:
    def __init__(self, col_name, col_df, function_relation=None, history=None):
        r'''
        Calculation is a class that supports storing calculation details such as variable name, input data,
        source function, calculation history and previously used function relations.

        :param col_name: variable name of the calculation result.
        :param col_df: pandas Series or DataFrame of the calculation result.
        :param function_relation: PartialFunctionRelation used to perform the calculation.
        :param history: record of the previous calculation results used to perform the calculation.
        '''
        if history is None:
            self.history = frozenset()
        else:
            self.history = history
        self.col_name = col_name
        self.col_df = col_df
        self.function_relation = function_relation
        self.process()

    def __str__(self):
        r'''
        Returns a human-readable format of the calculation.

        :return:
        '''
        out = tuple( str(symb_part) for symb_part in self.symbolic_representation() )
        out = str(out)
        return(out)

    def symbolic_representation(self):
        r'''
        Generates the symbolic representation of the calculation.

        :return:
        '''
        return((self.col_name, self.function_relation, self.symbolic_history))

    def process(self):
        r'''
        Processes the input information after initialization.

        :return:
        '''
        self.get_consumed_function_relations()
        self.get_symbolic_history()

    def get_consumed_function_relations(self):
        r'''
        Collects the consumed function relations in the calculation history for quick reference.

        :return:
        '''
        try:
            out = self.historic_function_relations
        except AttributeError:
            consumed_function_relations = set()
            if self.function_relation is not None:
                consumed_function_relations.add(self.function_relation)
            for calc in self.history:
                consumed_function_relations.update(calc.historic_function_relations)
            self.historic_function_relations = frozenset(consumed_function_relations)
            out = self.historic_function_relations
        return(out)
    def get_symbolic_history(self):
        r'''
        Collects the symbolic history of the calculation.

        :return:
        '''
        try:
            out = self.symbolic_history
        except AttributeError:
            symbolic_history = set()
            for historic_calculation in self.history:
                symbolic_history.add(historic_calculation.symbolic_representation())
            self.symbolic_history = frozenset(symbolic_history)
            out = self.symbolic_history
        return(out)
