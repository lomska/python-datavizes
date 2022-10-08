# Another horizontal bar chart, this time to compare two groups of values with positive and negative meanings. 
# The model: https://www.nytimes.com/2020/09/16/business/retail-sales-consumer-spending-rise.html 
# Besides the grid design, it is interesting how the positive and negative values are labeled. 
# This chart will possibly be improved in the future.

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import FixedLocator


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# Extracting the data on federal taxes and transfers from the federal center + USDRUB exchange rate
cum_flow = df.query('(i1 == 1 & r1 > 1 & r3 == 0) | (i1 == 1 & i3 == 9)')[['index', 'year', 'region_eng', 'value']].pivot(
    index=['year', 'region_eng'], columns='index', values='value').fillna(0)

# Absolute money flow between the region and the state, in $ mln
cum_flow['flow_to_fed_usdbn'] = ((cum_flow['tax_to_fed']-cum_flow['transfers_to_reg'])/cum_flow['rub_usd']/1000000000).round(1)

# Flow totals for each region for 2017–2021 
cum_flow_2017_2021 = cum_flow.loc[2017:2021][['flow_to_fed_usdbn']].groupby(level=1).cumsum().loc[2021].sort_values(
    by='flow_to_fed_usdbn', ascending=True)
cum_flow_2017_2021['flow_to_fed_usdbn'] = cum_flow_2017_2021['flow_to_fed_usdbn'].astype('int')

# Filter out the regions which gave away or absorbed less than $1 billion in 2017–2021
cum_flow_2017_2021 = cum_flow_2017_2021.query('flow_to_fed_usdbn < -1 | flow_to_fed_usdbn > 1')

# Flow totals for each region for for 2012–2016
cum_flow_2012_2016 = cum_flow.loc[2012:2016][['flow_to_fed_usdbn']].groupby(level=1).cumsum().loc[2016].sort_values(
    by='flow_to_fed_usdbn', ascending=True)
cum_flow_2012_2016['flow_to_fed_usdbn_prev'] = cum_flow_2012_2016['flow_to_fed_usdbn'].astype('int')

# Joining the tables to filer and sort the values for 2012–2016
cum_flow_2017_2021 = cum_flow_2017_2021.join(cum_flow_2012_2016[['flow_to_fed_usdbn_prev']], how='left')


# THE CHART *******************************************************************************************************************


x = cum_flow_2017_2021.index.str.title() # region names
y1 = cum_flow_2017_2021['flow_to_fed_usdbn'] # 2017-2021 cumulative flows 
y2 = cum_flow_2017_2021['flow_to_fed_usdbn_prev'] # 2012-2016 cumulative flows 

# Positive and negative flow colors for 2017-2021 
color_bars_1 = dict()
for i in range(len(x)):
    color_bars_1 = []
    for val in cum_flow_2017_2021['flow_to_fed_usdbn']:
        if val > 0:
            color_bars_1.append('#fd9f1a')
        else:
            color_bars_1.append('#467481')

# Positive and negative flow colors for 2012-2016 
color_bars_2 = dict()
for i in range(len(x)):
    color_bars_2 = []
    for val in cum_flow_2017_2021['flow_to_fed_usdbn_prev']:
        if val > 0:
            color_bars_2.append('#b46406')
        else:
            color_bars_2.append('#003e4f')

font = {'fontname':'Calibri'}
            
fig, ax = plt.subplots(figsize=(12,20), facecolor='w', ncols=2, sharey=True)

# The bars
ax[0].barh(x, y1, color=color_bars_1, align='center', height=0.72)
ax[1].barh(x, y2, color=color_bars_2, alpha=0.6, align='center', height=0.72)

# The titles
ax[0].set_title('2017-2021', loc='left', x=0.09, fontsize=13.5, fontweight='bold', pad=10, color='k', **font)
ax[1].set_title('2012-2016', loc='left', x=0.09, fontsize=13.5, fontweight='bold', pad=10, color='k', **font)

# Annotating the 2017-2021 bars
for n, m in enumerate(y1):
    if m > 0:
        p = -3 # the label position is to the left of the positive bar 
    else:
        p = 26 # the label position is to the right of the negative bar 
        m = -m # hiding the 'minus' before the label

    ax[0].text(x = p, y = n - 0.2, s = f'${m} B', color = 'k', fontsize = 10, horizontalalignment = 'right', **font)

# Annotating the 2012-2016 bars
for n, m in enumerate(y2):
    if m > 0:
        p = -3
    else:
        p = 26
        m = -m

    ax[1].text(x = p, y = n - 0.2, s = f'${m} B', color = 'k', fontsize = 10, horizontalalignment = 'right', **font)

# Setting the minor ticks to draw gridlines between the bars, not over
ax[0].yaxis.set_major_locator(mtick.FixedLocator(np.arange(len(cum_flow_2017_2021.index))))
ax[0].yaxis.set_minor_locator(mtick.FixedLocator(np.arange(-0.5, len(cum_flow_2017_2021.index), 1)))
ax[0].set_yticklabels(x) 
ax[0].grid(which='minor', axis='y', color='#E6E6E6', linestyle=':', linewidth=1, zorder=3)
ax[0].grid(visible=None, which='major', axis='y')

ax[1].yaxis.set_major_locator(mtick.FixedLocator(np.arange(len(cum_flow_2017_2021.index))))
ax[1].yaxis.set_minor_locator(mtick.FixedLocator(np.arange(-0.5, len(cum_flow_2017_2021.index), 1)))
ax[1].set_yticklabels(x) 
ax[1].grid(which='minor', axis='y', color='#E6E6E6', linestyle=':', linewidth=1, zorder=3)
ax[1].grid(visible=None, which='major', axis='y')

# Labelling the common y-axis
for label in ax[0].get_yticklabels():
    label.set(fontsize=12, color='k', **font)

# Hiding the x-axis and y-ticks
ax[0].get_xaxis().set_visible(False)
ax[1].get_xaxis().set_visible(False)
ax[0].yaxis.set_tick_params(which='both', length=0)
ax[1].yaxis.set_tick_params(which='both', length=0)

# Setting the bold zero-line
ax[0].axvline(0, color='k', linestyle='-', linewidth=0.5, zorder=1)
ax[1].axvline(0, color='k', linestyle='-', linewidth=0.5, zorder=1)

# Hiding all the spines
plt.setp(ax[0].spines.values(), visible=False) 
plt.setp(ax[1].spines.values(), visible=False) 

# Defining the borders
ax[0].set_xlim(xmin=-50, xmax=220)
ax[0].set_ylim(ymin=-0.7, ymax=len(cum_flow_2017_2021.index)-0.3)
ax[1].set_xlim(xmin=-50, xmax=220)
ax[1].set_ylim(ymin=-0.7, ymax=len(cum_flow_2017_2021.index)-0.3)

plt.tight_layout()

plt.suptitle('CUMULATIVE NET CASH FLOW BETWEEN THE REGIONS AND THE FEDERAL CENTER IN 2017-2021', x=0.78, y=1.02, fontsize=17,
             ha='right', va='top', **font)

plt.savefig('08_positive_and_negative_bar_charts_comparison.png', dpi=300, bbox_inches='tight')

plt.show()