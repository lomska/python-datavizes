# This chart is a variation of ggplot boxplots, which I found on the web. This particular color and shape decision turned out
# to be quite complicated to implement with pandas; this is my own solution in combination with a bit of code from stackoverflow.

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import PathPatch
import matplotlib.font_manager as font_manager

import seaborn as sns


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# Extracting the data on own revenues, federal taxes, and federal transfers
regional_flows = df.query('i1 == 1 & r1 != 0 & r3 == 0')[['year', 'index', 'region_eng', 'value']].pivot(index=['year', 'region_eng'], columns='index', values='value').fillna(0)

# Net cash flow between the region and the federal center
regional_flows['flow_to_fed'] = regional_flows['transfers_to_reg']-regional_flows['tax_to_fed']

# If net money flow (transfers from the federal center minus taxes to it) is more than 100% of own revenue for the corresponding
# year, we'll consider this region a dependent by 100% and more. If the flow is -100% or less, the region is a 100%+ donor. If
# the region gives away or takes from the federation a sum equivalent to less than 100% of its own revenue, it'll be called up
# to 100% donor or dependent, correspondingly.

def region_class(s):
    if s['flow_to_fed'] == 0:
        return 'no_data'
    elif s['flow_to_fed'] <= -s['reg_own_revenue']:
        return 'donor_100_and_more'
    elif -s['reg_own_revenue'] < s['flow_to_fed'] < 0:
        return 'donor_up_to_100'
    elif 0 < s['flow_to_fed'] < s['reg_own_revenue']:
        return 'dependent_up_to_100'
    elif s['flow_to_fed'] > s['reg_own_revenue']:
        return 'dependent_100_and_more'
regional_flows['region_class'] = regional_flows.apply(region_class, axis=1)

# Extracting the data on key budget spending, population, and USD exchange rate
regional_spendings = df.query(
    '(i1 == 1 & i3 == 2 & s1 in (5,7,9,10) & s2 == 0) | (i1 == 1 & i3 == 2 & s1 == 4 & s2 in (8,9))')[[
    'year', 'index', 'region_eng', 'value']].pivot(index=['year', 'region_eng'], columns='index', values='value').fillna(0)
population = df.query('i3 == 5')[['year', 'index', 'region_eng', 'value']].pivot(index=['year', 'region_eng'],
                                                                                 columns='index', values='value').fillna(0)
rub_usd = df.query('i3 == 9')[['year', 'index', 'region_eng', 'value']].pivot(index=['year', 'region_eng'],
                                                                              columns='index', values='value').fillna(0)
# Regional classes as of 2021
classes2021 = regional_flows.loc[2021][['region_class']]

# -> USD
regional_spendings_usd = regional_spendings.div(rub_usd.rub_usd, axis=0).round(1)
# -> per capita
regional_spendings_pc = regional_spendings_usd.div(population.population, axis=0).round(1)

# We'll analyse the regions in classes as of 2021
regional_spendings_pc = regional_spendings_pc.join(classes2021).reset_index()

regional_spendings_pc = regional_spendings_pc[['year', 'region_eng', 'healthcare', 'education', 'social policy ',
                                               'housing and utilities sector', 'public road system', 'transportation',
                                               'region_class']]


# THE CHART *******************************************************************************************************************


# The next function narrows the boxes, I took it from Stackoverflow and modified it a bit
def adjust_box_widths(g, fac):

    for ax in g.axes:

        for c in ax.get_children():

            if isinstance(c, PathPatch):
                p = c.get_path()
                verts = p.vertices
                verts_sub = verts[:-1]
                xmin = np.min(verts_sub[:, 0])
                xmax = np.max(verts_sub[:, 0])
                xmid = 0.5*(xmin+xmax)
                xhalf = 0.5*(xmax - xmin)

                xmin_new = xmid-fac*xhalf
                xmax_new = xmid+fac*xhalf
                verts_sub[verts_sub[:, 0] == xmin, 0] = xmin_new
                verts_sub[verts_sub[:, 0] == xmax, 0] = xmax_new

                for l in ax.lines:
                    if np.all(l.get_xdata() == [xmin, xmax]):
                        l.set_xdata([xmin_new+0.01, xmax_new-0.01])

# And this one sets color parameters for the boxes and their whiskers; we'll set one color for all the components except the 
# median line
def set_4_boxpairs_colors(ax, colors):
    for i in range(len(ax.artists)):
        mybox = ax.artists[i]
        if i == 0 or i == 4: # set color for the 1st and the 5th box out of eight
            mybox.set_facecolor(colors[0])
            mybox.set_edgecolor(colors[0])
            for j in range(i*6, i*6+2):
                line = ax.lines[j]
                line.set_color(colors[0])
        elif i == 1 or i == 5: # set color for the 2nd and the 6th box out of eight
            mybox.set_facecolor(colors[1])
            mybox.set_edgecolor(colors[1])
            for j in range(i*6, i*6+2):
                line = ax.lines[j]
                line.set_color(colors[1])
        elif i == 2 or i == 6: # set color for the 3rd and the 7th box out of eight
            mybox.set_facecolor(colors[2])
            mybox.set_edgecolor(colors[2])
            for j in range(i*6, i*6+2):
                line = ax.lines[j]
                line.set_color(colors[2])
        elif i == 3 or i == 7: # set color for the 4th and the 8th box out of eight
            mybox.set_facecolor(colors[3])
            mybox.set_edgecolor(colors[3])
            for j in range(i*6, i*6+2):
                line = ax.lines[j]
                line.set_color(colors[3])
        mybox.set_linewidth(1)

# Set the axes, titles, and colors
x = 'year'

y = []
for n in regional_spendings_pc.columns[2:8]:
    y.append(n)

titles = []
for n in regional_spendings_pc.columns[2:8].str.title():
    titles.append(n)
    
colors = ['#b46406', '#fd9f1a', '#467481', '#003e4f']

# Set properties for the boxes

font = {'fontname':'Calibri'}

boxprops = {'linewidth': 1}
lineprops = {'linewidth': 1}
medianprops = {'color': 'w', 'linewidth': 1}
capprops = {'linewidth': 0}

boxplot_kwargs = dict({'boxprops': boxprops, 'medianprops': medianprops, 'whiskerprops': lineprops,
                       'capprops': lineprops, 'capprops':capprops, 'width': 0.7})

# ...and for the legend
font_legend = font_manager.FontProperties(family='Calibri', size=13)

fig, axes = plt.subplots(sharex=True, sharey=True, squeeze=False, figsize=(15,12))

# A cycle to make a grid of charts
i = 0
for n in range(2):
    for m in range(3):
        ax = plt.subplot2grid((2, 3), (n, m), zorder=2)
        
        sns.boxplot(x=x, y=y[i], data=regional_spendings_pc.query('year in (2016, 2021)'),
                    hue='region_class', hue_order = ['donor_100_and_more',    # we need a hue order to sort the boxes inside 
                                                     'donor_up_to_100',       # the subplot, so the particular meaning 
                                                     'dependent_up_to_100',   # corresponds to the particular color
                                                     'dependent_100_and_more'],
                    dodge=True, fliersize=0, **boxplot_kwargs, ax=ax, zorder = 3) # fliersize = 0 -> no outliers on the graph
        
        set_4_boxpairs_colors(ax, colors) # coloring the whiskers and box lines
        
        # Axes and grid design
        ax.set_ylim(ymin=0, ymax=700)
        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)
        ax.set_title(titles[i], fontsize=14, fontweight='bold', pad=10, **font)
        ax.grid(which='major', axis='y', color='silver', linestyle=':', zorder=0)
        for label in ax.get_xticklabels():
            label.set(fontsize=12, fontweight='bold', color='#4f5b66', **font)
        for label in ax.get_yticklabels():
            label.set(fontsize=12, **font)
        ax.yaxis.set_major_formatter('${x:1.0f}') 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('silver')
        ax.spines['left'].set_color('silver')
        ax.tick_params(axis='both', color='silver')
        ax.legend().set_visible(False)
        ax.set_axisbelow(True) # helps when the grid appears above the plot
        if i == 0:
            h,l = ax.get_legend_handles_labels() # extracting values for the legend
        i+=1

# Narrowing the boxes
adjust_box_widths(fig, 0.8)

# Legend
patch1 = mpatches.Patch(color='#b46406', label='donate more than 100% of revenue')
patch2 = mpatches.Patch(color='#fd9f1a', label='donate up to 100% of revenue')
patch3 = mpatches.Patch(color='#467481', label='get up to 100% of revenue')
patch4 = mpatches.Patch(color='#003e4f', label='get more than 100% of revenue')
fig.legend(handles=[patch1, patch2, patch3, patch4], ncol=2, bbox_to_anchor=(0, 1.06, 1, 0), loc='upper right',
           frameon=False, handlelength=1, handletextpad=0.5, title="REGIONS' ROLE IN 2021:", title_fontsize=13,
           prop=font_legend)

fig.suptitle("HOW THE REGIONS' SPENDINGS HAVE CHANGED SINCE 2016", x=0.02, y=1.05, fontsize=20, ha='left', va='top', **font)
fig.text(0.02,1.01,"YEARLY SPENDING PER CAPITA", fontsize=15, **font)

plt.tight_layout()

plt.savefig('05_boxplots_from_ggplot.png', dpi=300, bbox_inches='tight')

plt.show()