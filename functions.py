import pandas as pd
from itertools import product




class PartialFunctionRelation:
    def __init__(self,function_dict,all_variables):
        self.function_dict = function_dict
        self.all_variables = all_variables
    def __call__(self,df):
        unknown_variables = self.get_unknown_variables(df.columns)
        if len(unknown_variables) == 1:
            output_variable = unknown_variables[0]
            output = self.compute_variable(df,output_variable)
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
    def get_output_variables(self):
        return(self.function_dict.keys())
    def get_unknown_variables(self,variable_list):
        unknown_variables = [ variable for variable in self.get_output_variables() if variable not in variable_list ]
        return(unknown_variables)
    def calculable(self,variable_list):
        unknown_variables = self.get_unknown_variables(df.columns)
        return(len(unknown_variables) <= 1)



class FunctionRelation(PartialFunctionRelation):
    def __init__(self,function_dict):
        super(PartialFunctionRelation,self).__init__(function_dict,function_dict.keys())



class FunctionRelation:
    def __init__(self,function_dict):
        self.function_dict = function_dict
    def __call__(self,df):
        unknown_variables = self.get_unknown_variables(df.columns)
        if len(unknown_variables) == 1:
            output_variable = unknown_variables[0]
            output = self.compute_variable(df,output_variable)
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
        input_variables = self.get_input_variables(output_variable)
        output = self.function_dict[output_variable](df[input_variables])
        return(output)
    def get_input_variables(self,output_variable):
        input_variables = [ variable for variable in self.get_all_variables() if variable != output_variable ]
        return input_variables
    def get_all_variables(self):
        return(self.function_dict.keys())
    def get_output_variables(self):
        return(self.function_dict.keys())
    def get_unknown_variables(self,variable_list):
        unknown_variables = [ variable for variable in self.get_output_variables() if variable not in variable_list ]
        return(unknown_variables)
    def calculable(self,variable_list):
        unknown_variables = self.get_unknown_variables(variable_list)
        return(len(unknown_variables) <= 1)


class FunctionSystem:
    def __init__(self,function_relations):
        self.function_relations = function_relations
    def __call__(self,df):
        calculations = [ (col,list(),df[col]) for col in df.columns ]
        for func_rel in self.function_relations:
            candidate_columns = [ col for (col,fr_list,col_df) in calculations if func_rel not in fr_list ]
            if func_rel.calculable(candidate_columns):
                options = [ (col,fr_list,col_df) for (col,fr_list,col_df) in calculations if (col in func_rel.get_all_variables()) and (func_rel not in fr_list) ]
                for (output_variable, input_combination) in self._possible_input_sets(func_rel,options):
                    input_df = pd.concat([ col_df for (col,fr_list,col_df) in input_combination ],axis=1)
                    output = func_rel(input_df)
                    calculations.append((output_variable,fr_list.copy().append(func_rel),output))
    def _possible_input_sets(self,func_rel,options):
        for output_variable in func_rel.get_output_variables():
            input_variables = func_rel.get_input_variables(output_variable)
            input_combinations = [ [ (col,fr_list,col_df) for (col,fr_list,col_df) in options ] for input_variable in input_variables ]
            for input_combination in product(*input_combinations):
                yield(output_variable,input_combination)






