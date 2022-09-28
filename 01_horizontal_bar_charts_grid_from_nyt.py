# Here I'll adapt an infographics with horizontal bar charts from the NYT to my own dataset.
# The original design is here: https://www.nytimes.com/2021/11/17/upshot/global-survey-optimism.html 

# The tricky part of this viz is the grid: the bars are lying on the gridlines by default, and we want to place them in between. 
# The second trick is the segmentation lines, which should lie under the gridlines but above the bars.
# Each subplot has an individual title and color.

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import FixedLocator

import seaborn as sns

# THE DATA ********************************************************************************************************************

df = pd.read_csv('russian_budget_data.csv', index_col=0)

fed_tax = (df.query('i1 == 2 & r1 == 3 & r3 != 0 & r5 == 0').set_index('index')[['year', 'value']].reset_index().pivot(
    index='year', columns='index', values='value')/1000000000000).round(1)
fed_tax = fed_tax.reindex(fed_tax.mean().sort_values(ascending=False).index, axis=1)

fed_tax['other taxes'] = fed_tax.iloc[:, 6:].sum(axis=1)+fed_tax.iloc[:, 4]
fed_tax = fed_tax.iloc[:, [0,1,2,3,5,-1]]

fed_tax = fed_tax.rename(columns={'additional income from hydrocarbon extraction tax':'hydrocarbon extraction tax',
                                  'corporate income tax full':'corporate income tax',
                                  'vat on sales':'VAT on sales'})

# THE CHART *******************************************************************************************************************

index = fed_tax.index

cols = [fed_tax['minerals extraction tax'], fed_tax['VAT on sales'], fed_tax['corporate income tax'],
       fed_tax['hydrocarbon extraction tax'], fed_tax['excises'], fed_tax['other taxes']]

titles = ['Minerals\nExtraction Tax', 'VAT\nOn Sales', 'Corporate\nIncome Tax',
          'Hydrocarbon\nExtraction Tax', '   Excises', 'Other\nTaxes']

colors = ['#30637f', '#93c2d3', '#98b7bb', '#fdd0a9', '#faaa6d', '#f78562']

hfont = {'fontname':'Calibri'}

sns.set_style("whitegrid")

fig, axes = plt.subplots(figsize=(16,5), facecolor='w', ncols=6, sharey=True) # the facecolor we need to save the figure on the
                                                                              # white background, not transparent. 
fig.tight_layout()

# We build subplots in a cycle. 
for i in range(6):
    axes[i].barh(index, cols[i], align='center', height=0.72, color=colors[i], zorder=0) # zorder parameter = 0 will put the
                                                                                         # bars at the "lowest" level of the
                                                                                         # chart (below the gridlines).
    axes[i].set_title(titles[i], loc='left', fontsize=13.5, fontweight='bold', pad=10, color='k', **hfont) # as the chart is
                                                                                                           # shifted towards the
                                                                                                           # zero line, 
                                                                                                           # the Excises title
                                                                                                           # contains whitespace 
    axes[i].xaxis.tick_bottom() # show x-ticks
    axes[i].tick_params(axis='x', color='#4f5b66', length=6, direction='in') # direction = "in" will align the ticks with the 
                                                                             # zero line
    if i != 4: # the 4th chart has negative values, so we'll design its axes separately
        axes[i].set_xticks([2, 4, 6, 8]) 
        axes[i].xaxis.get_major_ticks()[3].set_visible(False) # the last tick is invisible
        axes[i].set_xticklabels(['2tn', '4tn', '6tn', '']) # just as its ticklabel
    else:
        axes[i].set_xticks([-0.5, 2, 4, 6, 8])
        axes[i].xaxis.get_major_ticks()[0].set_visible(False) # the negative tick is invisible
        axes[i].xaxis.get_major_ticks()[4].set_visible(False) # the rest is similar to other subplots 
        axes[i].set_xticklabels(['', '2tn', '4tn', '6tn', ''])
    # The gridlines design
    axes[i].yaxis.set_major_locator(mtick.FixedLocator(np.arange(2011, 2022, 1))) # define major ticks
    axes[i].yaxis.set_minor_locator(mtick.FixedLocator(np.arange(2010.5, 2022, 1))) # define minor ticks
    axes[i].set_yticklabels(np.arange(2011, 2022, 1)) # set labels 
    axes[i].grid(which='major', axis='x', color='w', linestyle='-', linewidth=0.9, zorder=2) # zorder = 2 for the x-axis will 
                                                                                             # make the vertical gridlines 
                                                                                             # appear above the bars 
    axes[i].grid(which='minor', axis='y', color='#343d46', linestyle='-', linewidth=0.15, zorder=3) # the gridlines for the 
                                                                                                    # y-axes are based on the
                                                                                                    # minor ticks, so that they
                                                                                                    # appear in between the
                                                                                                    # major axes;
                                                                                                    # zorder = 3 will make them
                                                                                                    # appear above the vertical
                                                                                                    # gridlines
    axes[i].grid(b=None, which='major', axis='y') # make the major y-gridlines invisible
    axes[i].axvline(0, color='k', linewidth=0.7, zorder=2) # a bold zero line for each subplot
    # The ticklabels design
    for label in axes[0].get_yticklabels():
        label.set(fontsize=12, color='k', **hfont) 
    for label in axes[i].get_xticklabels(): 
        label.set(fontsize=12, color='#4f5b66', **hfont)

plt.gca().invert_yaxis() # place the years in the chart in ascending order

sns.despine(left=True, bottom=True, right=True) # delete all spines

plt.subplots_adjust(wspace=0, top=0.85, bottom=0.1, left=0.18, right=0.95) # wspace = 0 makes the gridlines continuous

plt.suptitle('AMOUNT OF TAXES PAID TO THE FEDERAL CENTER EACH YEAR: TYPES OF TAXES, RUB TRILLION',
             x=0.725, y=1.06, fontsize=17, ha='right', va='top', **hfont)

plt.savefig('01_horizontal_bar_charts_grid_from_nyt.png', dpi=300, bbox_inches='tight')

plt.show()