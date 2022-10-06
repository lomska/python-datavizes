# This chart is a cool way to show the growth or fall of some amount that was caused by a certain component. 
# Source: https://www.nytimes.com/2018/11/15/health/ecigarettes-fda-flavors-ban.html 
# Here, we'll use the same design to illustrate the divergence of the two types of federal budget revenue, which was caused by
# the rise in regional tax collection and the fall in international trade revenues in Russia.

# Nothing tricky here except for some small details; just the line charts and markers pointing to the last (current) values
# from these charts, with labels on the ends of each line, beyond the axes.

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.markers

import seaborn as sns


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# Extracting the data on total tax and non-tax revenues and their components: the regional taxes and international trade
fedrev_table = df.query(
    '(i1 == 2 & i2 == 2 & i3 == 1 & r3 == 0) | (i1 == 2 & i2 == 1 & r1 == 3 & r2 == 0) |\
    (i1 == 2 & i2 == 2 & i3 == 2 & s1 == 0) | (i1 == 2 & i2 == 2 & r3 == 10 & r4 == 0)').set_index(
    'index')[['year','value']].reset_index().pivot(index='year', columns='index', values='value')

fedrev_table = (fedrev_table/1000000000000).round(1) # -> RUB tn


# THE CHART *******************************************************************************************************************


font = {'fontname':'Calibri'}

xticks = fedrev_table.index # ticklabels: years
x_range = np.arange(len(fedrev_table['tax_to_fed']))
y1 = fedrev_table['tax_to_fed'] # regional taxes to the federal center
y2 = fedrev_table['fed_tax_revenue'] # total federal tax revenues
y3 = fedrev_table['fed_nontax_revenue'] # total federal non-tax revenues
y4 = fedrev_table['international trade revenues'] # federal revenues from international trade

sns.set_style('whitegrid')

fig, ax = plt.subplots(figsize=(10,4))

ax.plot(x_range, y1, color='#465e81', lw=2.5, linestyle=':') # dashed lines for parts
ax.plot(x_range, y2, color='#465e81', lw=2.5) # solid lines for totals
ax.plot(x_range, y4, color='#f9ba3e', lw=2.5, linestyle=':')
ax.plot(x_range, y3, color='#f9ba3e', lw=2.5)
ax.plot(x_range[-1], y1[2021], 'o', markersize=6, color='#465e81') # "empty" markers for parts
ax.plot(x_range[-1], y1[2021], 'o', markersize=3, color='w')
ax.plot(x_range[-1], y2[2021], 'o', markersize=6, color='#465e81') # "solid" markers for totals
ax.plot(x_range[-1], y3[2021]+0.1, 'o', markersize=6, color='#f9ba3e')
ax.plot(x_range[-1], y4[2021], 'o', markersize=6, color='#f9ba3e')
ax.plot(x_range[-1], y4[2021], 'o', markersize=3, color='w')

ax.set_ylim(ymin=0)
ax.set_xlim(xmin=-0.05, xmax=10.05) # set x-max to fit the markers on the graph but to minimize the x-lines length

# Labelling the lines
ax.text(x_range[-1]+0.2, y1[2021], "TAXES FROM REGIONS", color ='k', fontsize=10, **font)
ax.text(x_range[-1]+0.2, y2[2021], "FEDERAL TAX REVENUE", color ='k', fontsize=10, fontweight='bold', **font)
ax.text(x_range[-1]+0.2, y3[2021], "FEDERAL NON-TAX REVENUE", color ='k', fontsize=10, fontweight='bold', **font)
ax.text(x_range[-1]+0.2, y4[2021], "INTERNATIONAL TRADE", color ='k', fontsize=10, **font)

# Grid, ticks, and ticklabels design

ax.xaxis.tick_bottom() # show the ticks

ax.set_xticks(x_range)
ax.set_xticklabels(xticks)
ax.set_yticks([5, 10, 15, 20])
ax.set_yticklabels(['5tn', '10tn', '15tn', '20tn'])

ax.grid(axis='x') # show only horizontal gridlines
sns.despine(left=True, top=True, right=True, bottom=True) # delete all spines

ax.axhline(0, color='k', lw=3.3, linestyle='-') # bold zero line

ax.tick_params(axis='x', colors='#4f5b66', direction='out', length=5) # set ticks to be beyond the axes 
ax.tick_params(axis='y', colors='#4f5b66')

ax.spines['bottom'].set_position(('outward', 10)) # shift the bottom spine lower (to place the ticklabels)
for i in ax.xaxis.get_ticklines(): # ticks: vertical lines
    i.set_marker('|')

for label in ax.get_xticklabels():
    label.set(fontsize=12, color='#4f5b66', **font)
for label in ax.get_yticklabels():
    label.set(fontsize=12, color='k', **font)
    
ax.set_title("REGIONS' ROLE IN FEDERAL REVENUE GROWTH, RUB TRILLION", x=0.63, y=1.18, fontsize=15, color='k',
             ha='right', va='top', **font)

plt.savefig('06_linechart_totals_and_key_parts_nyt.png', dpi=300, bbox_inches='tight')

plt.show() 