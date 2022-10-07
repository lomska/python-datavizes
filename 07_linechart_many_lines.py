# This is another variation of a line chart, which can be used to illustrate a quantity of values, with an emphasis on one or
# several particular items. I'll use it to draw the dynamics of all the key federal spending in Russia in 2011–2021.

# The most interesting items are colored; "the rest" is made in a cycle. 

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.markers

import seaborn as sns


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# extracting major expenditures
spending_change = df.query('i1 == 2 & i2 == 2 & i3 == 2 & 0 < s1 < 13 & s2 == 0')[['index', 'year', 'value']].set_index('year')

# -> trillions of rubles
spending_change['spending_tn'] = (spending_change['value']/1000000000000).round(1)

# items -> columns (years are rows)
spending_change = spending_change[['index', 'spending_tn']].pivot(columns='index', values='spending_tn')


# THE CHART *******************************************************************************************************************


font = {'fontname':'Calibri'}

xticks = spending_change.index # ticklabels: years
x_range = np.arange(len(spending_change['education']))

# a list of sums and a list of labels for spending items
y = []
labels = []
for i in range(len(spending_change.columns)):
    y.append(spending_change.iloc[:, i])
    labels.append(spending_change.iloc[:, i].name.upper())

sns.set_style('whitegrid')

fig, ax = plt.subplots(figsize=(10,4))

# those items that haven't grown notably will be gray and have no markers
for i in [0,1,2,3,5,6,7,9,10]:
    ax.plot(xticks, y[i], color='silver', lw=2.5, zorder=0)

# items that have grown significantly will be colored and will have markers
colors = dict({4:'#9E0085', 8:'#007D61', 11:'#B68600'})
for i in [4,8,11]:
    ax.plot(xticks, y[i], color=colors[i], lw=2.5, zorder=1) # a line
    ax.plot(xticks[-1], y[i][2021]+0.02, 'o', markersize=6, color=colors[i]) # a marker on the end of the line
    ax.text(xticks[-1]+0.2, y[i][2021], labels[i], color ='k', fontsize=10, fontweight='bold', **font) # a label

ax.set_ylim(ymin=0)
ax.set_xlim(xmin=2010.95, xmax=2021.05)

# grid, ticks, and ticklabels design

ax.xaxis.tick_bottom() # show the ticks

ax.set_xticks(xticks)
ax.set_xticklabels(xticks)
ax.set_yticks([1, 2, 3, 4, 5, 6, 7])
ax.set_yticklabels(['1tn', '2tn', '3tn', '4tn', '5tn', '6tn', '7tn'])

ax.grid(axis='x') # show only horizontal gridlines

sns.despine(left=True, top=True, right=True, bottom=True) # delete all spines
ax.axhline(0, color='k', lw=2.5, linestyle='-') # bold zero line

ax.tick_params(axis='x', colors='#4f5b66', direction='out', length=5) # set ticks to be beyond the axes 
ax.tick_params(axis='y', colors='#4f5b66')

ax.spines['bottom'].set_position(('outward', 10)) # shift the bottom spine lower (to place the ticklabels)

for i in ax.xaxis.get_ticklines(): # ticks: vertical lines
    i.set_marker('|')

for label in ax.get_xticklabels():
    label.set(fontsize=12, color='#4f5b66', **font)
for label in ax.get_yticklabels():
    label.set(fontsize=12, color='k', **font)
    
ax.set_title('WHICH FEDERAL SPENDINGS HAVE GROWN SIGNIFICANTLY AFTER 2017, RUB TRILLION', x=0.9, y=1.15, fontsize=15,
             color='k', ha='right', va='top', **font)

plt.savefig('07_linechart_many_lines.png', dpi=300, bbox_inches='tight')

plt.show() 