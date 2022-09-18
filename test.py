import pandas as pd
import numpy as np
from functions import *




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










