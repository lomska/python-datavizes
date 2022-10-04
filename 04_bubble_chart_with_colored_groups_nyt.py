# There's another NYT-inspired graph (https://www.nytimes.com/2022/01/06/learning/whats-happening-in-this-graph-jan-12-2022.html). 
# Here, I map the regions depending on the direction and the amount of their money exchange with the federal center and on their
# budget balances (surplus or deficit).

# There are several intricate steps here: the bubble edgecolors (corresponding to the main colors), the axes label design (as
# the default looks don't explain what is happening on the chart properly), and the annotations.

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter

import seaborn as sns

# THE DATA ********************************************************************************************************************

df = pd.read_csv('russian_budget_data.csv', index_col=0)

# Extracting the data on own revenues, federal taxes, federal transfers, income per capita, and population
regional_flows = df.query(
    '(i1 == 1 & r1 != 0 & r3 == 0) | (i1 == 1 & i3 in (5, 7)) | (i1 == 1 & i3 == 2 & s1 == 0)')[[
    'year', 'index', 'region_eng', 'value']].pivot(index=['year', 'region_eng'], columns='index', values='value').fillna(0)

# Deficit = own revenue + federal transfers - spending
regional_flows['deficit'] = regional_flows['reg_own_revenue']+regional_flows['transfers_to_reg']-regional_flows['reg_spending']
# Net money flow with the federal center = incoming transfers - owtcoming taxes
regional_flows['flow_to_fed'] = regional_flows['transfers_to_reg']-regional_flows['tax_to_fed']

regional_flows[['reg_own_revenue',
                'tax_to_fed',
                'transfers_to_reg',
                'deficit',
                'flow_to_fed']] = (regional_flows[['reg_own_revenue',
                                                   'tax_to_fed',
                                                   'transfers_to_reg',
                                                   'deficit',
                                                   'flow_to_fed']]/1000000000).round(1) # -> RUB bn

# Budget surplus/deficit as a percentage of the regional's own revenue
regional_flows['deficit_rev_share'] = (regional_flows['deficit']/regional_flows['reg_own_revenue']*100).round(1)
# Money flow with the federal center as a percentage of the regional's own revenue
regional_flows['flow_to_fed_rev_share'] = (regional_flows['flow_to_fed']/regional_flows['reg_own_revenue']*100).round(1)

# Income per capita as a percentage of the average Russian income per capita for the corresponding year
regional_flows['income_tw_mean'] = regional_flows['income_per_cap']/regional_flows.groupby(level=0)[
    'income_per_cap'].mean()

# Defining regions' per capita income classes: the poorest 40%, 20%, 20%, and the richest 20%; the mean per capita income
# fluctuates around the 7th quantile (70%)

quantiles = dict()
years = pd.Series(range(2011,2022))

for year in years:
    quantiles[year] = []
    inc_quantile_80 = float(regional_flows.loc[year].income_per_cap.quantile([0.8])) # the 8th quartile (80%)
    inc_quantile_60 = float(regional_flows.loc[year].income_per_cap.quantile([0.6])) # the 6th quartile (60%)
    inc_quantile_40 = float(regional_flows.loc[year].income_per_cap.quantile([0.4])) # the 4th quartile (40%)
    quantiles[year].append([inc_quantile_80, inc_quantile_60, inc_quantile_40])

df_quantiles = pd.DataFrame(quantiles).T
df_quantiles['inc_quantile_80'], df_quantiles['inc_quantile_60'],  df_quantiles['inc_quantile_40'] = zip(*df_quantiles[0])
df_quantiles = df_quantiles.rename(index={'index':'year'}).drop(0, axis=1)

# Joining the quartile columns to the dataframe
regional_flows = regional_flows.reset_index().set_index('year').join(df_quantiles).reset_index().rename(
    columns={'index':'year'}).set_index(['year', 'region_eng'])

# Defining the region's income class: 
# "high" refers to regions in the top 20% by income per capita;
# "higher average" refers to regions where income per capita is higher than 60% but lower than the top 20%;
# "lower average" refers to regions where income per capita is higher than 40% but lower than the top-40%;
# "low" refers to regions in the bottom 40% by income per capita. 
def region_inc(s):
    if s['income_per_cap'] == 0:
        return 'nodata'
    elif s['income_per_cap'] >= s['inc_quantile_80']:
        return 'high'
    elif s['inc_quantile_60'] <= s['income_per_cap'] < s['inc_quantile_80']:
        return 'higher_avg'
    elif s['inc_quantile_60'] > s['income_per_cap'] >= s['inc_quantile_40']:
        return 'lower_avg'
    elif s['income_per_cap'] < s['inc_quantile_40']:
        return 'low'
regional_flows['region_inc'] = regional_flows.apply(region_inc, axis=1)

# To set the color rules for the bubbles' edges, we need to sort the classes (by which we'll color the bubbles)
def inc_order(s):
    if s['region_inc'] == 'high':
        return 0
    elif s['region_inc'] == 'higher_avg':
        return 1
    elif s['region_inc'] == 'lower_avg':
        return 2
    elif s['region_inc'] == 'low':
        return 3
    elif s['region_inc'] == 'nodata':
        return 4
    else:
        return 5
regional_flows['inc_order'] = regional_flows.apply(inc_order, axis=1)

regional_flows = regional_flows[['deficit_rev_share',
                                 'flow_to_fed_rev_share',
                                 'population',
                                 'region_inc',
                                 'inc_order']].sort_values(by=['year', 'inc_order'])

# Making coordinates for the annotations for 2021; we're looking for regions that gave away or received more than 100% of their
# own revenues. 
coordinates = regional_flows.loc[2021][(
    regional_flows.loc[2021]["flow_to_fed_rev_share"] >= 100)|(
    regional_flows.loc[2021]["flow_to_fed_rev_share"] <= -100)][['flow_to_fed_rev_share', 'deficit_rev_share']]

# Renaming some regions for more beautiful mapping
coordinates = coordinates.rename(index={'chukotka autonomous okrug':'Chukotka AO',
                                       'jewish autonomous oblast':'Jewish AO',
                                       'khanty-mansiysk autonomous okrug – ugra':'Khanty-Mansiysk AO',
                                       'nenets autonomous okrug':'Nenets AO',
                                       'north osetia - alania':'North Osetia',
                                       'yamalo-nenets autonomous okrug':'Yamalo-Nenets AO'})

# Capitalising and transforming long names into two-row
coordinates.index = coordinates.index.str.upper()
coordinates.index = coordinates.index.str.replace(' OBLAST', '\nOBLAST', regex=True)
coordinates.index = coordinates.index.str.replace(' KRAI', '\nKRAI', regex=True)
coordinates.index = coordinates.index.str.replace(' OKRUG', '\nOKRUG', regex=True)

# THE CHART *******************************************************************************************************************

font = {'fontname':'Calibri'}

sns.set_style('whitegrid')

x = regional_flows.loc[2021]['flow_to_fed_rev_share'] # money flows between the region and the center as a percentage
                                                      # of the region's revenue
y = regional_flows.loc[2021]['deficit_rev_share'] # region's surplus/deficit as a percentage of the region's revenue
color = regional_flows.loc[2021]['region_inc'] # color by the income group
size = regional_flows.loc[2021]['population'] # size by the population

# Defining an edgecolor for each class (without this list, they won't coincide with the bubbles' colors)
z = regional_flows.loc[2021]['region_inc'].dropna()
colors = []
for i in range(len(z)):
    if z[i] == "high":
        colors.append('#be490b')
    if z[i] == "higher_avg":
        colors.append('#d18a09')
    if z[i] == "lower_avg":
        colors.append('#4496c3')
    if z[i] == "low":
        colors.append('#264c67')
        
fig, ax = plt.subplots(figsize=(18,7))

ax = sns.scatterplot(x=x, y=y, data=regional_flows.loc[2021], hue=color, size=size, sizes=(50,1500),
                     alpha=.8, lw=20, palette=['#f26419','#f6ae2d','#86bbd8','#33658a'], edgecolor=colors, zorder=3)

# Display the axes values as percentages
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

# Annotations for the legend
ax.text(-1100, 67, "Circles are sized by region population", color ='k', fontsize=13) # bubble sizes
ax.text(-280, 67, "Income group:", color ='k', fontsize=13, fontweight='bold') # the name of the legend

# We use annotations with arrows to label the x and y axes so that they define the chart's meaning more clearly
ax.annotate("SURPLUS", xy=(-1380, 60), xytext=(-1380, 5), arrowprops=dict(arrowstyle="-|>", color ='k', lw=0.9),
            color='k', fontsize=9, fontweight='bold', horizontalalignment='center', annotation_clip=False)
ax.annotate("DEFICIT", xy=(-1380, -60), xytext=(-1380, -7), arrowprops=dict(arrowstyle="-|>", color ='k', lw=0.9),
            color='k', fontsize=9, fontweight='bold', horizontalalignment='center', annotation_clip=False)
ax.annotate("TO THE REGION", xy=(700, -72), xytext=(50, -72), arrowprops=dict(arrowstyle="-|>", color ='k', lw=0.9),
            color='k', fontsize=9, fontweight='bold', verticalalignment='center', annotation_clip=False)
ax.annotate("TO THE FEDERAL BUDGET", xy=(-1250, -72), xytext=(-300, -72), arrowprops=dict(arrowstyle="-|>", color ='k', lw=0.9),
            color='k', fontsize=9, fontweight='bold', verticalalignment='center', annotation_clip=False)

# Hide the default axes labels
ax.xaxis.label.set_visible(False)
ax.yaxis.label.set_visible(False)

# Design of a grid and ticklabels 
ax.grid(which='major', axis='both', color='#808080', linestyle=':', linewidth=1, zorder=0)
for label in ax.get_xticklabels():
    label.set(fontsize=12, color='#4f5b66', **font)
for label in ax.get_yticklabels():
    label.set(fontsize=12, color='k', **font)

# Highlight the 0 lines on both axes
plt.axhline(0, color='#808080', linewidth=1, zorder=1)
plt.axvline(0, color='#808080', linewidth=1, zorder=1)

# The edges
plt.ylim(ymin=-60, ymax=60)
plt.xlim(xmin=-1250, xmax=700)

# Legend: we only need a part with colors; sizes spoil the view and don't add much sense. We've added an annotation instead
h,l = ax.get_legend_handles_labels()
plt.legend(h[1:5], ['high', 'higher average', 'lower average', 'low'], ncol=4, bbox_to_anchor=(-0.06, 1.02, 1.02, 0),
           loc='lower right', fontsize=13, frameon=False, handlelength=0.7, handletextpad=0.15)

# Annotation style dicts
arrowprops1 = dict(arrowstyle = '-', color ='#4f5b66', lw=0.7, connectionstyle="angle,angleA=0,angleB=90,rad=5")
arrowprops2 = dict(arrowstyle = '-', color ='#4f5b66', lw=0.7, connectionstyle="angle,angleA=90,angleB=0,rad=5")
kwargs1 = {'fontname':'Calibri', 'fontsize':11, 'horizontalalignment':'center', 'color':'#4f5b66'}
kwargs2 = {'fontname':'Calibri', 'fontsize':11, 'horizontalalignment':'center', 'verticalalignment':'center', 'color':'#4f5b66'}

# Making annotations
c_x = coordinates["flow_to_fed_rev_share"] # x-value
c_y = coordinates["deficit_rev_share"] # y-value
c_i = coordinates.index # the name of the region

# Filtering the regions we are interested in
mask1 = (c_x < -280) # those that give 280%+ of revenue to the federal center
mask2 = (c_x > 250) # those that take 250%+ of revenue from the federal center
mask3 = (c_y > 20) # those with 20%+ surplus
mask4 = (c_y < -20) # those with 20%+ deficit
mask5 = ((c_i == "KOMI")|(c_i == "SAMARA\nOBLAST")|(c_i == "UDMURTIA")) # Komi, Samara, Udmurtia
tomsk = (c_i == "TOMSK\nOBLAST") # Tomsk Oblast
perm = (c_i == "PERMSKY\nKRAI") # Permsky Krai
tyumen = (c_i == "TYUMEN\nOBLAST") # Tyumen Oblast
irkutsk = (c_i == "IRKUTSK\nOBLAST") # Irkutsk Oblast
kalin = (c_i == "KALININGRAD\nOBLAST") # Kaliningrad Oblast
tatar = (c_i == "TATARSTAN") # Tatarstan
astr = (c_i == "ASTRAKHAN\nOBLAST") # Astrakhan Oblast
crimea = (c_i == "CRIMEA") # Crimea

# Annotating groups of regions
x1 = c_x[mask1 | mask3 | perm]
y1 = c_y[mask1 | mask3 | perm]
names1 = c_i[mask1 | mask3 | perm]
for x0,y0,name in zip(x1,y1,names1):
    ax.annotate(name, xy =(x0, y0), xytext =(x0-1, y0+6), arrowprops = arrowprops1, **kwargs1, zorder=0)

x2 = c_x[mask2 | mask4 | tomsk]
y2 = c_y[mask2 | mask4 | tomsk]
names2 = c_i[mask2 | mask4 | tomsk]
for x0,y0,name in zip(x2,y2,names2):
    ax.annotate(name, xy =(x0, y0), xytext =(x0-1, y0-8), arrowprops = arrowprops1, **kwargs1, zorder=0)

x3 = c_x[mask5]
y3 = c_y[mask5]
names3 = c_i[mask5]
for x0,y0,name in zip(x3,y3,names3):
    ax.annotate(name, xy =(x0, y0), xytext =(x0-90, y0-1), arrowprops = arrowprops2, **kwargs2, zorder=0)

# Annotating individual regions
x4 = c_x[tatar][0]
y4 = c_y[tatar][0]
names4 = c_i[tatar][0]
ax.annotate(names4, xy =(x4, y4), xytext =(x4-1, y4-6), arrowprops = arrowprops2, **kwargs2, zorder=0)

x5 = c_x[astr][0]
y5 = c_y[astr][0]
names5 = c_i[astr][0]
ax.annotate(names5, xy =(x5, y5), xytext =(x5-200, y5-1), arrowprops = arrowprops2, **kwargs2, zorder=0)

x6 = c_x[crimea][0]
y6 = c_y[crimea][0]
names6 = c_i[crimea][0]
ax.annotate(names6, xy =(x6, y6), xytext =(x6-1, y6-10), arrowprops = arrowprops2, **kwargs2, zorder=0)

x7 = c_x[tyumen][0]
y7 = c_y[tyumen][0]
names7 = c_i[tyumen][0]
ax.annotate(names7, xy =(x7, y7), xytext =(x7+10, y7+25), arrowprops = arrowprops1, **kwargs2, zorder=0)

x8 = c_x[kalin][0]
y8 = c_y[kalin][0]
names8 = c_i[kalin][0]
ax.annotate(names8, xy =(x8, y8), xytext =(x8+10, y7+18), arrowprops = arrowprops1, **kwargs2, zorder=0)

x9 = c_x[irkutsk][0]
y9 = c_y[irkutsk][0]
names9 = c_i[irkutsk][0]
ax.annotate(names9, xy =(x9, y9), xytext =(x9-1, y9-20), arrowprops = arrowprops1, **kwargs2, zorder=0)

plt.suptitle('NET CASH FLOW WITH THE FEDERAL CENTER IN 2021', x=0.448, y=1.07, fontsize=22, ha='right', va='top', **font)
plt.title("REGION'S OWN YEARLY REVENUE = 100%", x=0.21, y=1.16, fontsize=16, ha='right', va='top', **font)

plt.savefig('04_bubble_chart_with_colored_groups_nyt.png', dpi=300, bbox_inches='tight')

plt.show()