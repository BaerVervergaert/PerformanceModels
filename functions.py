import pandas as pd
from itertools import product
from functools import reduce


class HypotheticalCalculation:
    def __init__(self,col_name,function_relation=None, symbolic_history=None):
        if symbolic_history is None:
            self.symbolic_history = set()
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
            self.history = set()
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
                consumed_function_relations.union(calc.historic_function_relation)
            self.historic_function_relations = consumed_function_relations
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
            self.symbolic_history = symbolic_history
            out = self.symbolic_history
        return(out)


class PartialFunctionRelation:
    def __init__(self,function_dict,all_variables):
        r'''
        PartialFunctionRelation is a class which supports automated calculation of function relations. To define a
        partial function relation all the desired functions with their outcome variable should be provided in the
        function_dict.

        :param function_dict: Dictionary with output variable names as keys and functions taking in pandas DataFrames as
        values.
        :param all_variables: Set of variable names
        '''
        self.function_dict = function_dict
        self.all_variables = set(all_variables)
    def __call__(self,df):
        r'''
        Computes the results from the function relation.

        If all variables are given in the input dataframe columns, then all given outcome variables are
        calculated from the provided data.

        If one variable is missing, then it will be calculated if a function is provided in function_dict. Else, an
        error will be raised.

        :param df: pandas.DataFrame containing all input variables as columns.
        :return:
        '''
        unknown_variables = self.get_unknown_variables(df.columns)
        if len(unknown_variables) == 1:
            output_variable = unknown_variables.pop()
            output = self.compute_variable(df,output_variable)
            output.rename(output_variable,inplace=True)
            return(output)
        elif len(unknown_variables) == 0:
            output = {}
            for output_variable in self.get_output_variables():
                output[output_variable] = self.compute_variable(df,output_variable)
            return(output)
        else:
            msg = f'Cannot perform calculation with more than one missing variable: {unknown_variables}'
            raise ValueError(msg)
    def compute_variable(self,df,output_variable):
        r'''
        Calculate the output_variable from the input df using this function relation.

        :param df:
        :param output_variable:
        :return:
        '''
        input_variables = [ variable for variable in self.get_all_variables() if variable != output_variable ]
        output = self.function_dict[output_variable](df[input_variables])
        return(output)
    def get_all_variables(self):
        r'''
        Returns all variables in the function relation.

        :return:
        '''
        return(self.all_variables)
    def get_input_dimension(self):
        r'''
        Returns the number of required inputs.

        :return:
        '''
        return(len(self.get_all_variables())-1)
    def get_output_variables(self):
        r'''
        Returns all possible output variables of the function relation.

        :return:
        '''
        return(self.function_dict.keys())
    def _columns_can_calculate_column(self,col,cols):
        not_a_member = ( col not in cols )
        all_variables_except_output = self.get_all_variables().copy()
        all_variables_except_output.remove(col)
        can_calculate_col = ( set(cols) == set(all_variables_except_output) )
        return(not_a_member and can_calculate_col)
    def get_unknown_variables(self,variable_list):
        unknown_variables = set( variable for variable in self.get_output_variables() if self._columns_can_calculate_column(variable,variable_list) )
        return(unknown_variables)
    def calculable(self,variable_list):
        unknown_variables = self.get_unknown_variables(variable_list)
        return(len(unknown_variables) <= 1)
    def get_input_variables(self,output_variable):
        input_variables = set( variable for variable in self.get_all_variables() if variable != output_variable )
        return input_variables


class PartialFunctionRelation:
    def __init__(self,function_dict,all_variables):
        self.function_dict = function_dict
        self.all_variables = set(all_variables)
    def __call__(self,df):
        unknown_variables = self.get_unknown_variables(df.columns)
        if len(unknown_variables) == 1:
            output_variable = unknown_variables.pop()
            output = self.compute_variable(df,output_variable)
            output.rename(output_variable,inplace=True)
            return(output)
        elif len(unknown_variables) == 0:
            output = {}
            for output_variable in self.get_output_variables():
                output[output_variable] = self.compute_variable(df,output_variable)
            return(output)
        else:
            msg = f'Cannot perform calculation with more than one missing variable: {unknown_variables}'
            raise ValueError(msg)
    def compute_variable(self,df,output_variable):
        input_variables = [ variable for variable in self.get_all_variables() if variable != output_variable ]
        output = self.function_dict[output_variable](df[input_variables])
        return(output)
    def get_all_variables(self):
        return(self.all_variables)
    def get_input_dimension(self):
        return(len(self.get_all_variables()))
    def get_output_variables(self):
        return(self.function_dict.keys())
    def _columns_can_calculate_column(self,col,cols):
        not_a_member = ( col not in cols )
        all_variables_except_output = self.get_all_variables().copy()
        all_variables_except_output.remove(col)
        can_calculate_col = ( set(cols) == set(all_variables_except_output) )
        return(not_a_member and can_calculate_col)
    def get_unknown_variables(self,variable_list):
        unknown_variables = set( variable for variable in self.get_output_variables() if self._columns_can_calculate_column(variable,variable_list) )
        return(unknown_variables)
    def calculable(self,variable_list):
        unknown_variables = self.get_unknown_variables(variable_list)
        return(len(unknown_variables) <= 1)
    def get_input_variables(self,output_variable):
        input_variables = set( variable for variable in self.get_all_variables() if variable != output_variable )
        return input_variables


class FunctionRelation(PartialFunctionRelation):
    def __init__(self,function_dict):
        super(FunctionRelation,self).__init__(function_dict,function_dict.keys())


class FunctionSystem:
    def __init__(self,function_relations):
        self.function_relations = function_relations
    def __call__(self,df):
        # Create a list of performed calculations
        calculations = [ (col,set(),df[col]) for col in df.columns ]
        calculations = [ Calculation(col,df[col]) for col in df.columns ]

        # Set a boolean to keep track of continuing calculations
        performed_new_calculations = True
        while performed_new_calculations:
            # Reset boolean
            performed_new_calculations = False

            # Iterate of all possible function relations we can choose
            for func_rel in self.function_relations:

                # Find calculated columns we can use with the function relation
                # candidate_columns = [ col for (col,fr_list,col_df) in calculations if func_rel not in fr_list ]
                # candidate_input = [ (col,fr_list,col_df) for (col,fr_list,col_df) in calculations if func_rel not in fr_list ]
                candidate_input = [
                    calc for calc in calculations
                    if (func_rel not in calc.historic_function_relations)
                       and (calc.col_name in func_rel.get_all_variables())
                ]
                candidate_columns = [ calc.col_name for calc in candidate_input ]

                # Check if the function_relation can use the columns to compute any output
                if func_rel.calculable(candidate_columns):

                    # Loop over all valid input combinations
                    for (output_variable, input_combination) in self._possible_input_sets(func_rel,candidate_input):
                        input_combination = list(input_combination)

                        # Check if proposed calculation is desirable
                        hypothetical_history = set( calc.symbolic_history for calc in input_combination )
                        hypothetical_calculation = HypotheticalCalculation(output_variable,function_relation=func_rel,symbolic_history=hypothetical_history)

                        if not self._compare_hypothetical_calculation(hypothetical_calculation,calculations):
                            input_df = pd.concat([ calc.col_df for calc in input_combination ],axis=1)
                            output = func_rel(input_df)
                            new_calc = Calculation(output_variable,output,function_relation=func_rel,history=set(input_combination))
                            calculations.append(new_calc)
                            performed_new_calculations = True
        return(calculations)
    def _possible_input_sets(self,func_rel,options):
        # Per output_variable yield potential input combinations
        for output_variable in func_rel.get_output_variables():

            # Gather all input_variables
            input_variables = func_rel.get_input_variables(output_variable)

            # Construct input_variable options per dimension
            input_combinations = [ [ calc for calc in options if input_variable == calc.col_name ] for input_variable in input_variables ]

            # Per input_combination yield output_variable with input_combination
            for input_combination in product(*input_combinations):

                # Only yield if input_combination is a valid pairing of input dimensions
                if self._compare_function_relation_sets([calc.historic_function_relations for calc in input_combination ]):

                    # Yield output_variable with input_combination
                    yield(output_variable,input_combination)
    def _compare_hypothetical_calculation(self,hypothetical_calculation,calculations):
        compare_list = [ hypothetical_calculation.symbolic_representation() == calc.symbolic_representation() for calc in calculations ]
        return(any(compare_list))
    def _compare_function_relation_sets(self,fr_lists):
        all_function_relations = reduce(lambda x,y: x|y, [ fr_list for fr_list in fr_lists], set())
        for fr in all_function_relations:
            if len([ None for fr_list in fr_lists if fr in fr_list ]) > 1:
                return(False)
        return(True)






