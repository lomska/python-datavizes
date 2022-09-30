# This one is a cool way to show the dynamics of many indicators.
# The source is here https://www.nytimes.com/2018/11/25/opinion/monopolies-in-the-us.html. I adapted this infographic for my Russian regional budgets dataset, to draw the difference in sums of taxes paid to the federal budget by the Russian regions.

# The tricky part here is to draw the arrows, not the usual dumbbells.


import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter
import matplotlib.markers

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


# THE DATA ********************************************************************************************************************


df = pd.read_csv('russian_budget_data.csv', index_col=0)

# To draw the chart, we need three columns: the volume for 2011, the volume for 2011, and the absolute difference between them
# to sort the dumbbells.
# I don't take the regions with negative money flows here.

regs_for_graph = df.query('i1 == 1 & r1 in (1, 3) & r3 == 0')[['year', 'index', 'region_eng', 'value']].query(
    'year in (2011,2021)').pivot(index=['year', 'region_eng'], columns='index', values='value')
regs_for_graph['fedtax_share'] = (regs_for_graph['tax_to_fed']/regs_for_graph['reg_own_revenue']*100).round(1)
regs_for_graph = regs_for_graph.query('tax_to_fed >= 0').reset_index().pivot(
    index='region_eng', columns='year', values='fedtax_share').dropna().sort_values(by=2021).reset_index()
regs_for_graph['region_eng'] = regs_for_graph['region_eng'].str.title()
regs_for_graph['diff'] = regs_for_graph[2021]-regs_for_graph[2011]


# THE CHART *******************************************************************************************************************


hfont = {'fontname':'Calibri'}
font_color = 'k'

plt.figure(figsize=(15,20), facecolor='w') # we need facecolor to have a white background for the saved image
y_range = range(len(regs_for_graph.index)) # names of the regions -> y-axis

# a color palette for increasing and decreasing percentages:
color_lines = dict()
for i in y_range:
    color_lines = []
    for val in regs_for_graph['diff']:
        if val > 0:
            color_lines.append('#A61932')
        else:
            color_lines.append('#808080')

# dividing the growing and falling values to draw an "arrow" on the corresponding side 
z = regs_for_graph['diff']
mask1 = z > 0
mask2 = z < 0

ax = plt.axes(frameon=False) # the chart is frameless

# horizontal lines for the dumbbells:
# xmax + 2 - for the arrows to be fused with lines
plt.hlines(y_range, xmin = regs_for_graph[2011], xmax = regs_for_graph[2021]+2,
           color=color_lines, edgecolor=color_lines, lw=5, zorder=3)
# gray arrows - for the descending rows:
# x + 4 - for the arrows to be fused with lines;
# zorder = 4 - for the arrows to be above the lines
plt.scatter(regs_for_graph[2021][mask2]+4, regs_for_graph[mask2].index, color='#808080', edgecolor='#808080',
            s=75, marker=matplotlib.markers.CARETLEFTBASE, label = 2011, zorder=4)
# red arrows - for the ascending rows:
plt.scatter(regs_for_graph[2021][mask1], regs_for_graph[mask1].index, color='#A61932', edgecolor='#A61932',
            s=75, marker=matplotlib.markers.CARETRIGHTBASE, label = 2021, zorder=4)

# annotations for the top dumbbell
plt.annotate(2011, xy =(regs_for_graph[2011][73]+2, y_range[73]+0.2),
             xytext =(regs_for_graph[2011][73]-25.5, y_range[73]+1.2),
             arrowprops = dict(arrowstyle = '-', color ='k', lw=1),
             fontsize=12, fontweight='bold')
plt.annotate(2021, xy =(regs_for_graph[2021][73]+11, y_range[73]+0.2),
             xytext =(regs_for_graph[2021][73]-17, y_range[73]+1.2),
             arrowprops = dict(arrowstyle = '-', color ='k', lw=1),
             fontsize=12, fontweight='bold')

# axes, grid and ticklabels design
plt.gca().yaxis.grid(color='#E6E6E6', linestyle=':')
plt.gca().xaxis.grid(color='#E6E6E6', linestyle='-')

plt.xticks([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200])
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.xaxis.set_tick_params(labeltop=True, labelbottom=False) # x-axis labels on the top
ax.get_xticklabels()[1].set_weight('bold') # highlighting the 100% value
ax.yaxis.set_tick_params(length=0) # hiding ticks
ax.xaxis.set_tick_params(length=0) # hiding ticks

for label in ax.get_xticklabels():
    label.set(fontsize=12, color='dimgray', **hfont)
for label in ax.get_yticklabels():
    label.set(fontsize=12, color=font_color, **hfont)

plt.yticks(y_range, regs_for_graph['region_eng'])
plt.ylim(-1, 75) # set the length of the x-axis gridlines

ynew = 100
ax.axvline(ynew, color='#BFBFBF', linestyle='-', zorder=1) # highlighting the 100% gridline
ax.legend().set_visible(False)

plt.title("WHAT PERCENTAGE OF A REGION'S REVENUE WAS ITS FEDERAL TAX EQUIVALENT TO",
          x=0.14, y=1.01, fontsize=20, pad=45, **hfont)

plt.tight_layout()

plt.savefig('03_dumbbell_or_arrow_chart_from_nyt.png', dpi=300, bbox_inches='tight')

plt.show()