import numpy as np
import pandas as pd

from FunctionRelations import PartialFunctionRelation, FunctionRelation, SymbolicFunctionRelation
from FunctionSystem import FunctionSystem, SymbolicFunctionSystem

#%% PARTIAL FUNCTION TEST - ALL INPUT

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,3)),
	columns = ['a','b','c'],
	)


function_dict = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
	'c': lambda df: df['a']/df['b'],
}

pfr = PartialFunctionRelation(function_dict,function_dict.keys())
out = pfr(df)

result = \
(out['a'] == df['b']*df['c']).all() &\
(out['b'] == df['a']/df['c']).all() &\
(out['c'] == df['a']/df['b']).all()
print(result)


#%% PARTIAL FUNCTION TEST - ALL INPUT, ONE INCALCULABLE

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,3)),
	columns = ['a','b','c'],
	)


function_dict = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
}

pfr = PartialFunctionRelation(function_dict,['a','b','c'])
out = pfr(df)

result = \
(out['a'] == df['b']*df['c']).all() &\
(out['b'] == df['a']/df['c']).all()
print(result)


#%% PARTIAL FUNCTION TEST - ONE MISSING INPUT, ONE INCALCULABLE

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,2)),
	columns = ['b','c'],
	)


function_dict = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
}

pfr = PartialFunctionRelation(function_dict,['a','b','c'])
out = pfr(df)

result = \
(out == df['b']*df['c']).all()
print(result)


#%% FUNCTION TEST - ONE MISSING INPUT, ONE INCALCULABLE

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,2)),
	columns = ['b','c'],
	)


function_dict = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
	'c': lambda df: df['a']/df['b'],
}

pfr = FunctionRelation(function_dict)
out = pfr(df)

result = \
(out == df['b']*df['c']).all()
print(result)


#%% FUNCTION TEST - ALL INPUT

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,3)),
	columns = ['a','b','c'],
	)


function_dict = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
	'c': lambda df: df['a']/df['b'],
}

pfr = FunctionRelation(function_dict)
out = pfr(df)

result = \
(out['a'] == df['b']*df['c']).all() &\
(out['b'] == df['a']/df['c']).all() &\
(out['c'] == df['a']/df['b']).all()
print(result)


#%% FUNCtION SYSTEM TEST

N = 100
df = pd.DataFrame(
	data = np.random.random(size=(100,4)),
	columns = ['a','b','c','d'],
	)


function_dict1 = {
	'a': lambda df: df['b']*df['c'],
	'b': lambda df: df['a']/df['c'],
	'c': lambda df: df['a']/df['b'],
}

function_dict2 = {
	'd': lambda df: df['b']*df['c'],
	'b': lambda df: df['d']/df['c'],
	'c': lambda df: df['d']/df['b'],
}

pfr1 = FunctionRelation(function_dict1)
pfr2 = FunctionRelation(function_dict2)

fs = FunctionSystem([pfr1,pfr2])
out = fs(df)
for calc in out:
	print(calc)
print(len(out))

import numpy as np
constants = {
	'a':2,
}
function_relations = [
	'c=a*b',
	'd=b*c'
	]
variables = ['b','c','d']
sfs = SymbolicFunctionSystem(function_relations,variables,constants=constants)
print(sfs)
df = pd.DataFrame(data=np.random.random(size=(10,len(variables))),columns=variables)
for calc in sfs(df):
	print(calc)
	print(calc.col_df)

import pandas as pd
import numpy as np

function_relation = 'aaa=a*aa'
variables = ['a','aa','aaa']
sfr = SymbolicFunctionRelation(function_relation,variables)

df = pd.DataFrame(data = np.random.random(size=(10,3)),columns=variables)
print(df)
test_c = sfr(df.loc[:,variables[:-1]])
print(test_c)
a = df['a']
aa = df['aa']
exec(function_relation)
print(aaa)
print((test_c == aaa).all())






