import pandas as pd
from itertools import product
from functools import reduce


class Calculation:
    def __init__(self,col_name,col_df,history,prev_function_relation):
        self.history = history
        self.col_name = col_name
        self.col_df = col_df
        self.prev_function_relation = prev_function_relation
        self.process()
    def symbolic_representation(self):
        return((self.col_name,self.prev_function_relation,self.history))
    def process(self):
        self.get_consumed_function_relations()
    def get_consumed_function_relations(self):
        try:
            out = self.historic_function_relations
        except AttributeError:
            consumed_function_relations = {self.prev_function_relation}
            for calc in self.history:
                consumed_function_relations.add(calc.historic_function_relation)
            self.historic_function_relations = consumed_function_relations
            out = self.historic_function_relations
        return(out)


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

        # Set a boolean to keep track of continuing calculations
        performed_new_calculations = True
        while performed_new_calculations:
            # Reset boolean
            performed_new_calculations = False

            # Iterate of all possible function relations we can choose
            for func_rel in self.function_relations:

                # Find calculated columns we can use with the function relation
                # candidate_columns = [ col for (col,fr_list,col_df) in calculations if func_rel not in fr_list ]
                candidate_input = [ (col,fr_list,col_df) for (col,fr_list,col_df) in calculations if func_rel not in fr_list ]
                candidate_columns = [ col for (col,fr_list,col_df) in candidate_input ]

                # Check if the function_relation can use the columns to compute any output
                if func_rel.calculable(candidate_columns):

                    # Gather optional input columns
                    options = [ (col,fr_list,col_df) for (col,fr_list,col_df) in candidate_input if (col in func_rel.get_all_variables()) ]

                    # Loop over all valid input combinations
                    for (output_variable, input_combination) in self._possible_input_sets(func_rel,options):

                        # Check if proposed calculation is desirable
                        fr_list = reduce(lambda x,y: x|y, [ fr_list for (col,fr_list,col_df) in input_combination ], set())
                        fr_list.add(func_rel)
                        hypothetical_calculation = (output_variable,fr_list)

                        if not self._compare_hypothetical_calculation(hypothetical_calculation,calculations):
                            input_df = pd.concat([ col_df for (col,fr_list,col_df) in input_combination ],axis=1)
                            output = func_rel(input_df)
                            calculations.append((output_variable,fr_list,output))
                            performed_new_calculations = True
        return(calculations)
    def _possible_input_sets(self,func_rel,options):
        # Per output_variable yield potential input combinations
        for output_variable in func_rel.get_output_variables():

            # Gather all input_variables
            input_variables = func_rel.get_input_variables(output_variable)

            # Construct input_variable options per dimension
            input_combinations = [ [ (col,fr_list,col_df) for (col,fr_list,col_df) in options if input_variable == col ] for input_variable in input_variables ]

            # Per input_combination yield output_variable with input_combination
            for input_combination in product(*input_combinations):

                # Only yield if input_combination is a valid pairing of input dimensions
                if self._compare_function_relation_sets([fr_list for (col,fr_list,col_df) in input_combination ]):

                    # Yield output_variable with input_combination
                    yield(output_variable,input_combination)
    def _compare_hypothetical_calculation(self,hypothetical_calculation,calculations):
        compare_list = [ hypothetical_calculation == (col,fr_list) for (col,fr_list,col_df) in calculations ]
        return(any(compare_list))
    def _compare_function_relation_sets(self,fr_lists):
        all_function_relations = reduce(lambda x,y: x|y, [ fr_list for fr_list in fr_lists], set())
        for fr in all_function_relations:
            if len([ None for fr_list in fr_lists if fr in fr_list ]) > 1:
                return(False)
        return(True)






