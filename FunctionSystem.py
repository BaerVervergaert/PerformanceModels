from functools import reduce
from itertools import product
import re
import pandas as pd

from Calculations import Calculation, HypotheticalCalculation
from FunctionRelations import SymbolicFunctionRelation

class FunctionSystem:
    def __init__(self,function_relations):
        self.function_relations = function_relations
    def __call__(self,df):
        # Create a list of performed calculations
        calculations = [ (col,frozenset(),df[col]) for col in df.columns ]
        calculations = [Calculation(col, df[col]) for col in df.columns]

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
                        hypothetical_history = frozenset( calc.symbolic_representation() for calc in input_combination )
                        hypothetical_calculation = HypotheticalCalculation(output_variable, function_relation=func_rel, symbolic_history=hypothetical_history)

                        if not self._compare_hypothetical_calculation(hypothetical_calculation,calculations):
                            input_df = pd.concat([ calc.col_df for calc in input_combination ],axis=1)
                            output = func_rel(input_df)
                            new_calc = Calculation(output_variable, output, function_relation=func_rel, history=frozenset(input_combination))
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
        all_function_relations = reduce(lambda x,y: x|y, [ fr_list for fr_list in fr_lists], frozenset())
        for fr in all_function_relations:
            if len([ None for fr_list in fr_lists if fr in fr_list ]) > 1:
                return(False)
        return(True)

class SymbolicFunctionSystem:
    def __init__(self,function_relations,variables,constants=None):
        if constants is None:
            constants = dict()
        self.symbolic_function_relations = function_relations
        self.variables = variables
        self.constants = constants
    def __str__(self):
        str_rep = '\n'.join(sfr for sfr in self.symbolic_function_relations)
        return(str_rep)
    def transform_symbolic_function_relations(self):
        function_relations = []
        for sfr in self.symbolic_function_relations:
            variable_in_formula = lambda v,sfr=sfr: re.search(r'\b{v}\b'.format(v=v),sfr) is not None
            sfr_variables = frozenset( v for v in self.variables if variable_in_formula(v))
            fr = SymbolicFunctionRelation(sfr,sfr_variables,constants=self.constants).to_function_relation()
            function_relations.append(fr)
        self.function_relations = function_relations
    def to_function_system(self):
        self.transform_symbolic_function_relations()
        fs = FunctionSystem(self.function_relations)
        return(fs)
