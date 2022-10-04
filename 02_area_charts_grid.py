# This infographic was designed by me. Here I map the distribution of taxes for the Russian regions that are the largest
# federal tax payers.

# The tricky part here is the colored borders between the areas; I use the line charts to draw them.
# To locate everything properly, the attention to the data preparation is needed.


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches # patches are needed to create a legend


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# First of all, we define the list of regions to be drawn; here, I need the 20 leading regions by the paid federal tax amount that are
# in the top-25 but beyond the top-5.

# sums paid for the federal budget in 2011 and 2021 for each key tax for each region
key_taxes_sums = df.query(
    '(i1 == 1 & r1 == 3 & r3 == 3 & r4 == 1) | (i1 == 1 & r1 == 3 & r3 == 7 & r4 == 5 & r5 == 0) |\
    (i1 == 1 & r1 == 3 & r3 == 1 & r4 == 1 & r5 == 0) | (i1 == 1 & r1 == 3 & r3 == 7 & r4 == 1 & r5 == 0)')[[
    'region_eng', 'index', 'year', 'value']].query('year in (2011,2021)').pivot(
    index=['region_eng', 'index'], columns='year', values='value')

# the difference in sums between 2021 and 2011
key_taxes_sums['difference'] = key_taxes_sums[2021]-key_taxes_sums[2011]

# taxes names -> columns names, 11-year difference -> values
key_taxes_sums = key_taxes_sums.drop([2011, 2021], axis=1).reset_index().pivot(
    index='region_eng', columns='index', values='difference')

# the difference in the total amount paid in key taxes for each region 
key_taxes_sums['all_key_taxes'] = key_taxes_sums.sum(axis=1)

# the percentage contribution of each region to the total difference
key_taxes_sums['perc_all_key'] = (key_taxes_sums['all_key_taxes'] / key_taxes_sums['all_key_taxes'].sum()*100).round(1)

# sorting the regions by their percentage contribution 
key_taxes_sums = key_taxes_sums.sort_values(by='perc_all_key', ascending=False)

# top-20 regions beyond the top-5 (Khanty-Mansiysk, Yamalo-Nenets, Moscow, Tatarstan, and Saint Petersburg)
key_taxes_regions = key_taxes_sums.head(25).index.str.lower().values # the top-25
key_taxes_regions_subtr = key_taxes_sums.iloc[[0,1,2,3,9], :].index.str.lower().values # to exclude
key_taxes_regions = list(set(key_taxes_regions) - set(key_taxes_regions_subtr)) # final list

# Now there's a list of regions for the plot. In the next step, we extract them from the dataframe.

# extract the data for the listed regions
key_taxes = df.query(
    '((i1 == 1 & r1 == 3 & r3 == 3 & r4 == 1) | (i1 == 1 & r1 == 3 & r3 == 7 & r4 == 1) |\
    (i1 == 1 & r1 == 3 & r3 == 1 & r4 == 1 & r5 == 0) | (i1 == 1 & r1 == 3 & r3 == 7 & r4 == 5 & r5 == 0) |\
    (i1 == 1 & i3 == 9)) & region_eng in @key_taxes_regions')[['index', 'region_eng', 'year', 'value']].pivot(
    index=['year', 'region_eng'], columns='index', values='value').fillna(0)

# RUB -> RUB bn
key_taxes['vat'] = (key_taxes['vat on sales']/1000000000).round(1)
key_taxes['mining'] = (key_taxes['minerals extraction tax']/1000000000).round(1)
key_taxes['corporate'] = (key_taxes['corporate income tax full']/1000000000).round(1)
key_taxes['hydrocarbon'] = (key_taxes['additional income from hydrocarbon extraction tax']/1000000000).round(1)
key_taxes['oil'] = (key_taxes['oil extraction tax']/1000000000).round(1)
key_taxes['gas'] = (key_taxes['gas extraction tax']/1000000000).round(1)
key_taxes['gas_condensate'] = (key_taxes['gas condensate extraction tax']/1000000000).round(1)
key_taxes = key_taxes[['vat', 'mining', 'corporate', 'hydrocarbon', 'oil', 'gas', 'gas_condensate']].reset_index()

# wide -> long data 
table_graph = pd.melt(key_taxes, id_vars=['year', 'region_eng'],
                      value_vars=['vat', 'corporate', 'hydrocarbon', 'oil', 'gas', 'gas_condensate'],
                      var_name='tax_type', value_name='amount')
table_graph['region_eng'] = table_graph['region_eng'].str.title()
table_graph['year'] = table_graph['year'].astype('int')

# We need no negative values for this chart; if the tax is negative (e.g. the tax return), the federal revenue is equal to 0.
table_graph.amount=table_graph.amount.mask(table_graph.amount.lt(0),0) 

table_graph = table_graph.sort_values(by=['year', 'region_eng', 'tax_type'])

# A sorted (by 2021) list of regions to set the order for the grid
table_graph_index = table_graph.pivot_table(
    index='region_eng', columns='year', values='amount', aggfunc='sum').fillna(0).astype('int')[[2021]].sort_values(
    by=2021, ascending=False).index.values.tolist()

# Now we have to make two modifications to the dataframe: one for the linecharts and one for the area chart.

# To locate the lines, we need to count the cumulative input.

# a copy of a table for drawing the area chart's edgelines (linecharts)
table_graph_lines = table_graph.sort_values(by=['year', 'region_eng', 'tax_type'])
# the total amount of key taxes levied in each region
table_graph_lines['cum_amount'] = table_graph_lines.groupby(['year', 'region_eng']).cumsum(numeric_only=True)
# values for line charts
table_graph_lines = table_graph_lines.pivot(index=['region_eng', 'tax_type'], columns='year', values='cum_amount').fillna(0)

# The areas are located automatically, so we need individual sums.

table_graph = table_graph.pivot(index=['region_eng', 'tax_type'], columns='year', values='amount').fillna(0)

# Reindexing the data 

# reindexing the linecharts according to the list of regions (setting their grid orger)
table_graph_lines = table_graph_lines.reindex(table_graph_index, level=0)

# reindexing the taxes inside each linechart
table_graph_lines = table_graph_lines.reindex(['vat', 'oil', 'hydrocarbon', 'gas_condensate', 'gas', 'corporate'], level=1)

# reindexing the area charts according to the list of regions (setting their grid orger)
table_graph = table_graph.reindex(table_graph_index, level=0)


# THE CHART *******************************************************************************************************************


hfont = {'fontname':'Calibri'}

x = table_graph.columns.values.tolist() # columns names -> the x-axis

# adding the tax values, tax names, and a title for each region to the list
y = [] # the list of values
keys = [] # the list of tax names
titles = [] # the list of titles
for n in table_graph.index.get_level_values('region_eng').unique():
    area = table_graph.loc[n].reset_index().iloc[:, 1:].values.tolist()
    key = table_graph.loc[n].reset_index().iloc[:, 0].values.tolist()
    y.append(area)
    keys.append(key)
    titles.append(n)   

# adding the tax values to the line charts list    
l = [] # the list of charts
for n in table_graph_lines.index.get_level_values('region_eng').unique():
    p = [] # the list of lines inside each chart
    for m in table_graph_lines.index.get_level_values('tax_type').unique():
        plot = table_graph_lines.loc[n,m].round(3).values
        plots = plot.tolist()
        p.append(plots)
    l.append(p)
    
color_map = ['#93c2d3', '#faaa6d', '#fdd0a9', '#F7C815', '#f78562', '#30637f']

fig, axes = plt.subplots(sharex=True, sharey=True, squeeze=False, figsize=(20,16), facecolor='w')

# Making a grid of 20 area charts
i = 0
for n in range(4):
    for m in range(5):
        ax = plt.subplot2grid((4, 5), (n, m))
        ax.stackplot(x, y[i], labels = keys[i], colors=color_map, edgecolor=None, alpha=0.9, zorder=2) # the area chart
        for m in range(6):
            ax.plot(x, l[i][m], color=color_map[5-m], linewidth=3, zorder=3) # the line charts;
                                                                             # the coloring order is reversed from the area chart;
                                                                             # zorder = 3 to place the lines above the areas
                                                                             # (whose zorder = 2)
        ax.yaxis.set_major_formatter('{x:1.0f}B')
        ax.set_title(titles[i], fontweight='bold', fontsize=17, pad=20, **hfont)
        ax.set_ylim(ymin=0, ymax=600)
        ax.set_xlim(xmin=2010.99, xmax=2021.01)
        for label in ax.get_xticklabels():
            label.set(fontsize=12, fontweight='bold', color='#4f5b66')
        for label in ax.get_yticklabels():
            label.set(fontsize=13)
        ax.grid(visible=None, which='major', axis='both')
        
        # spines design
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_zorder(3)
        ax.spines['bottom'].set_zorder(3)
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        
        # hide 0 ticklabel for y-axis
        yticks = ax.yaxis.get_major_ticks()
        yticks[0].label.set_visible(False)
        
        i+=1

# a unified legend for all subplots
patch1 = mpatches.Patch(color='#93c2d3', label='corporate income tax')
patch2 = mpatches.Patch(color='#faaa6d', label='gas extraction tax')
patch3 = mpatches.Patch(color='#fdd0a9', label='gas condensate extraction tax')
patch4 = mpatches.Patch(color='#F7C815', label='hydrocarbon extraction tax')
patch5 = mpatches.Patch(color='#f78562', label='oil extraction tax')
patch6 = mpatches.Patch(color='#30637f', label='VAT')
fig.legend(handles=[patch1,patch2,patch3,patch4,patch5,patch6], ncol=3,
           bbox_to_anchor=(0., 1, 1, 0), loc='lower right', fontsize=15, frameon=False)

plt.suptitle("MAJOR DONORS' PAYMENTS TO THE STATE, RUB BILLION", x=0.01, y=1.04, fontsize=28, ha='left', va='top', **hfont)

fig.tight_layout()

plt.savefig('02_area_charts_grid.png', dpi=300, bbox_inches='tight')

plt.show()