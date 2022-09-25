import sympy
import warnings
import traceback
import re

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
        self.all_variables = frozenset(all_variables)
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
        output = {}
        for output_variable in self.get_unknown_variables(df.columns):
            output[output_variable] = self.compute_variable(df,output_variable)
        if len(unknown_variables)==1:
            return(output[output_variable])
        elif len(unknown_variables)>1:
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
        input_variables = list(self.get_input_variables(output_variable))
        output = self.function_dict[output_variable](df[input_variables])
        output.rename(output_variable, inplace=True)
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
        r'''
        Determine if col can be computed if cols are provided. Moreover, col is not allowed to be present in cols.

        :param col: The name of the output variable.
        :param cols: The names of the input variables.
        :return:
        '''
        #not_a_member = ( col not in cols )
        all_variables_except_output = self.get_input_variables(col)
        can_calculate_col = set(cols).issuperset(all_variables_except_output)
        return(can_calculate_col)
    def get_unknown_variables(self,variable_list):
        r'''
        Returns the set of variables which can be calculated from given variables.

        :param variable_list: Iterable of variable names which symbolize the input.
        :return: Set of unknown variables which can be ccomputed from variable_list.
        '''
        unknown_variables = set( variable for variable in self.get_output_variables() if self._columns_can_calculate_column(variable,variable_list) )
        return(unknown_variables)
    def calculable(self,variable_list):
        r'''
        Determines if variable_list can use this function relation to calculation any unknown variable.

        :param variable_list: Iterable of variable names.
        :return:
        '''
        out = any([ True for variable in self.get_output_variables() if self._columns_can_calculate_column(variable,variable_list) ])
        return(out)
    def get_input_variables(self,output_variable):
        r'''
        Determine the necessary input variables from a given output variable.

        :param output_variable: variable name.
        :return:
        '''
        input_variables = set( variable for variable in self.get_all_variables() if variable != output_variable )
        return input_variables


class FunctionRelation(PartialFunctionRelation):
    def __init__(self,function_dict):
        super(FunctionRelation,self).__init__(function_dict,function_dict.keys())

class SymbolicFunctionRelation(PartialFunctionRelation):
    def __init__(self,function_relation,variables,constants=None):
        r'''
        A user-friendly helper class to construct a function relation from a string formatted relation.

        :param function_relation: Str formatted function relation.
        :param all_variables: List-like of variables used in the function relation.
        :param constants: Dict-like of (constant_name,constant_value) pairs of constants used in the fucntion relation.
        '''
        if constants is None:
            constants = dict()
        self.function_relation = function_relation
        self.variables = frozenset(variables)
        self.constants = constants
        self.to_function_relation()
    def __str__(self):
        str_rep = f'SymbolicFunctionRelation: {self.function_relation}'
        return(str_rep)
    def transform_variables_to_sympy(self):
        try:
            self.sympy_variables
        except AttributeError:
            self.sympy_variables = {v:sympy.symbols(v) for v in self.variables}
    def transform_formula_to_sympy(self):
        self.transform_variables_to_sympy()
        hash_map = {v:hash(v) for v in self.variables}
        hash_fr = self.function_relation
        for variable in self.variables:
            pattern = r'\b{variable}\b'.format(variable=variable)
            repl = str(hash_map[variable])
            hash_fr = re.sub(pattern,repl,hash_fr)
        for constant_name,constant_value in self.constants.items():
            pattern = r'\b{constant_name}\b'.format(constant_name=constant_name)
            repl = constant_value.__repr__()
            hash_fr = re.sub(pattern,repl,hash_fr)
        for variable in self.variables:
            pattern = str(hash_map[variable])
            repl = "self.sympy_variables['{variable}']".format(variable=variable)
            hash_fr = re.sub(pattern,repl,hash_fr)
        hash_fr = hash_fr.replace('=','-')
        self.sympy_function_relation = eval(hash_fr)
    def to_function_relation(self):
        self.transform_variables_to_sympy()
        self.transform_formula_to_sympy()
        func_dict = {}
        variables = self.sympy_variables
        formula = self.sympy_function_relation
        for variable in variables:
            try:
                res_formula = sympy.solve(formula,variable)
                if len(res_formula)>1:
                    raise NotImplementedError('No implementation for formula with multiple inversion solutions.')
                res_formula = res_formula[0]
                input = tuple(v for v in variables if v != variable)
                function = sympy.lambdify(input,res_formula)
                function = lambda df,function=function,input=input: function(*tuple(df[str(v)] for v in input))
                func_dict[str(variable)] = function
            except NotImplementedError as nie:
                traceback.print_exception(nie)
                warnings.warn(f'Skipping variable {variable} because it is not uniquely invertible for sympy.')
        variables = frozenset( str(v) for v in variables )
        super(SymbolicFunctionRelation,self).__init__(func_dict,variables)

