from functools import reduce
from itertools import product
import re
import pandas as pd

from Calculations import Calculation, HypotheticalCalculation
from FunctionRelations import SymbolicFunctionRelation

class FunctionSystem:
    def __init__(self,function_relations):
        r'''
        A FunctionSystem is a class which represents a collection of function relations which form one consistent whole. The basic example of a FunctionSystem is that of a physical model. In physics we often have a number of functional relations for a particular set up. These exist in parts, a small number of variables sharing one relation, while the whole system may consist of many such relations. We also may be able to measure a large number of these variables. A physics student is often asked to calculate one variable based on the other, but in reality it may be more interesting to compare both measured values and calculated values. This class can be used to perform all these calculations at once, taking away human error in computing inverse and replacing the manual labor of implementing such functions by hand.

        :param function_relations: Iterable of (Partial-)FunctionRelation objects.
        '''
        self.function_relations = list(function_relations)
    def append(self,function_relation):
        r'''
        Adds an existing (Partial-)FunctionRelation to the FunctionSystem.

        :param function_relation: PartialFunctionRelation or FunctionRelation.
        :return:
        '''
        self.function_relations.append(function_relation)
    def __call__(self,df):
        r'''
        Performs the actual calculation of the FunctionSystem based on the input dataframe df. In any Calculation a function relation is only used at most once in the calculation history. The system will perform all possible calculations under this rule. It will be able to complete missing columns as long as it has a function relation which allows the compuation of the missing column.

        :param df: Pandas.DataFrame with column names matching the variable names used in the FunctionRelations..
        :return:
        '''
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
        r'''
        Subroutine to generate all possible input relations based on the optional input variables and a given function relation.

        :param func_rel:  FunctionRelation
        :param options: List-like of input variable names.
        :return: Generator of possible calculation to perform, does not consider calculation history.
        '''
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
        r'''
        Determines if a hypothetical calculation has already been performed in the historical calculations.

        :param hypothetical_calculation:
        :param calculations:
        :return:
        '''
        compare_list = [ hypothetical_calculation.symbolic_representation() == calc.symbolic_representation() for calc in calculations ]
        return(any(compare_list))
    def _compare_function_relation_sets(self,fr_lists):
        r'''
        Determines if a List-like of FunctionRelations contains no duplicates, and hence if it is a valid combination function relation set.

        :param fr_lists: List-like of FunctionRelations
        :return:
        '''
        all_function_relations = reduce(lambda x,y: x|y, [ fr_list for fr_list in fr_lists], frozenset())
        for fr in all_function_relations:
            if len([ None for fr_list in fr_lists if fr in fr_list ]) > 1:
                return(False)
        return(True)

class SymbolicFunctionSystem(FunctionSystem):
    def __init__(self,function_relations,variables,constants=None):
        r'''
        User-friendly helper class to create a FunctionSystem with a symbolic list of function relations in string format. Sympy is used to complete the inversions. Symbolic function relations must follow python syntax. Variables and constants must match case.

        :param function_relations: List-like of string formatted function relations, e.g. 'a * b = c'.
        :param variables: List-like of formatted variables used in function relations.
        :param constants: Dict-like of constants in contant_name:contant_value format.
        '''
        if constants is None:
            constants = dict()
        self.symbolic_function_relations = function_relations
        self.variables = variables
        self.constants = constants
        self.transform_symbolic_function_relations()
        super(SymbolicFunctionSystem,self).__init__(self.function_relations)
    def __str__(self):
        r'''
        Outputs the string formatted collection of the function relations.

        :return:
        '''
        str_rep = '\n'.join(sfr for sfr in self.symbolic_function_relations)
        return(str_rep)
    def transform_symbolic_function_relations(self):
        r'''
        Creates FunctionRelations from the symbolic function relations given during the init.

        :return:
        '''
        function_relations = []
        for sfr in self.symbolic_function_relations:
            variable_in_formula = lambda v,sfr=sfr: re.search(r'\b{v}\b'.format(v=v),sfr) is not None
            sfr_variables = frozenset( v for v in self.variables if variable_in_formula(v))
            fr = SymbolicFunctionRelation(sfr,sfr_variables,constants=self.constants)
            function_relations.append(fr)
        self.function_relations = function_relations

