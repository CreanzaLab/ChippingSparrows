import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns; sns.set()
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import ranksums
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
import csv
from matplotlib.ticker import FuncFormatter

"""
Load data song data
"""
data_path = 'C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\FinalDataCompilation' + \
            '/FinalDataframe_CombinedTables_withReChipper_thenWithReExportedAs44100Hz_LogTransformed.csv'
log_song_data = pd.DataFrame.from_csv(data_path, header=0, index_col=None)

log_song_data_unique = log_song_data.loc[log_song_data['ComparedStatus'].isin(['unique', 'use'])].copy().reset_index(
    drop=True)
col_to_skip = ['CatalogNo', 'FromDatabase', 'ComparedStatus', 'RecordingDay', 'RecordingMonth', 'RecordingYear',
               'RecordingTime']
data_subset = log_song_data_unique.drop(col_to_skip, axis=1)
print(data_subset.shape)

# use only east, west and south data for wilcoxon rank sums
data_for_wrs = data_subset.drop(data_subset[data_subset.Region == 'mid'].index).copy().reset_index(drop=True)

# use all unique/use data, do not remove any mid region data, for heatmaps
data_for_heatmaps = data_subset.copy()


"""
Discrete Stats Tests using Regions:
Wilcoxon Rank sums for regions: east, west, south and the 16 song variables
"""
with open('C:/Users/abiga/Box Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported/BoxPlots_Norm'
          '/region_WilcoxonRanksums.csv', 'wb') as file:
    filewriter = csv.writer(file, delimiter=',')
    filewriter.writerow(['Song Variable', 'EW Wilcoxon p', 'EW p-value', 'ES Wilcoxon p', 'ES p-value', 'WS Wilcoxon p',
                         'WS p-value'])

    for sv in data_for_wrs.columns[3:]:
        e = data_for_wrs.loc[data_for_wrs['Region'] == 'east', sv]
        w = data_for_wrs.loc[data_for_wrs['Region'] == 'west', sv]
        s = data_for_wrs.loc[data_for_wrs['Region'] == 'south', sv]

        filewriter.writerow([sv, ranksums(e, w)[0], ranksums(e, w)[1], ranksums(e, s)[0], ranksums(e, s)[1],
                             ranksums(w, s)[0], ranksums(w, s)[1]])

""""
Box plot of results
"""
song_variables = ['Mean Note Duration',
                  'Mean Note Frequency Modulation',
                  'Mean Note Frequency Trough',
                  'Mean Note Frequency Peak',
                  'Mean Inter-Syllable Silence Duration',
                  'Mean Syllable Duration',
                  'Mean Syllable Frequency Modulation',
                  'Mean Syllable Frequency Trough',
                  'Mean Syllable Frequency Peak',
                  'Duration of Song Bout',
                  'Mean Stereotypy of Repeated Syllables',
                  'Number of Notes per Syllable',
                  'Syllable Rate',
                  'Total Number of Syllables',
                  'Standard Deviation of Note Duration',
                  'Standard Deviation of Note Frequency Modulation']

log_var = {3: 'ms', 7: 'ms', 8: 'ms', 14: 'number', 16: 'number', 17: 'ms'}
log_convert_var = {9: 'kHz', 4: 'kHz', 5: 'kHz', 6: 'kHz', 10: 'kHz', 11: 'kHz', 12: 'seconds'}
log_convert_inverse_var = {15: 'number/second'}
no_log = {13: '%'}
no_log_convert = {18: 'kHz'}
print(data_for_wrs.columns)

# take e^x for y-axis
for key, value in log_var.items():
    fig = plt.figure(figsize=(7, 11))
    my_dpi = 96
    sns.set(style='white')
    ax = sns.boxplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]], color='None',
                     fliersize=0, width=0.5,
                     linewidth=2)
    ax = sns.stripplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]],
                       palette=['#f17300', '#1f78b4', '#33a02c'],
                       size=7, jitter=True, lw=1, alpha=0.6)

    # Make the boxplot fully transparent
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0))

    ax.set_ylabel(song_variables[key-3] + ' (' + value + ')', fontsize=30)
    ax.set_xlabel('')
    ax.tick_params(labelsize=30, direction='out')
    ax.set(xticklabels=[])
    plt.setp(ax.spines.values(), linewidth=2)
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: "%.1f" % (np.exp(x))))

    # # plt.tight_layout()
    # pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
    #                "/PaperVersion/" + sv + '.pdf')
    # pdf.savefig(orientation='landscape')
    # pdf.close()

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()

    plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
                "/PaperVersion_noLogAxis_largerFont/" + data_for_wrs.columns[key] + '_noLogAxis_largerFont' + '.pdf', type='pdf', dpi=fig.dpi,
                bbox_inches='tight', transparent=True)
    # plt.cla()
    # plt.clf()
    plt.close()

    # plt.show()

# take e^x for each variable and also convert from Hz to kHz or ms to seconds
for key, value in log_convert_var.items():
    fig = plt.figure(figsize=(7, 11))
    my_dpi = 96
    sns.set(style='white')
    ax = sns.boxplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]], color='None',
                     fliersize=0, width=0.5,
                     linewidth=2)
    ax = sns.stripplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]],
                       palette=['#f17300', '#1f78b4', '#33a02c'],
                       size=7, jitter=True, lw=1, alpha=0.6)

    # Make the boxplot fully transparent
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0))

    ax.set_ylabel(song_variables[key-3] + ' (' + value + ')', fontsize=30)
    ax.set_xlabel('')
    ax.tick_params(labelsize=30, direction='out')
    ax.set(xticklabels=[])
    plt.setp(ax.spines.values(), linewidth=2)
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: "%.1f" % (np.exp(x)/1000)))

    # # plt.tight_layout()
    # pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
    #                "/PaperVersion/" + sv + '.pdf')
    # pdf.savefig(orientation='landscape')
    # pdf.close()

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()

    plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
                "/PaperVersion_noLogAxis_largerFont/" + data_for_wrs.columns[key] + '_noLogAxis_largerFont' + '.pdf', type='pdf', dpi=fig.dpi,
                bbox_inches='tight', transparent=True)
    # plt.cla()
    # plt.clf()
    plt.close()

    # plt.show()

# take e^x for each variable and convert from 1/ms to 1/seconds
for key, value in log_convert_inverse_var.items():
    fig = plt.figure(figsize=(7, 11))
    my_dpi = 96
    sns.set(style='white')
    ax = sns.boxplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]], color='None',
                     fliersize=0, width=0.5,
                     linewidth=2)
    ax = sns.stripplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]],
                       palette=['#f17300', '#1f78b4', '#33a02c'],
                       size=7, jitter=True, lw=1, alpha=0.6)

    # Make the boxplot fully transparent
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0))

    ax.set_ylabel(song_variables[key-3] + ' (' + value + ')', fontsize=30)
    ax.set_xlabel('')
    ax.tick_params(labelsize=30, direction='out')
    ax.set(xticklabels=[])
    plt.setp(ax.spines.values(), linewidth=2)
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: "%.1f" % (np.exp(x)*1000)))

    # # plt.tight_layout()
    # pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
    #                "/PaperVersion/" + sv + '.pdf')
    # pdf.savefig(orientation='landscape')
    # pdf.close()

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()

    plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
                "/PaperVersion_noLogAxis_largerFont/" + data_for_wrs.columns[key] + '_noLogAxis_largerFont' + '.pdf', type='pdf', dpi=fig.dpi,
                bbox_inches='tight', transparent=True)
    # plt.cla()
    # plt.clf()
    plt.close()

    # plt.show()

# are not log(value) so no need to take exponential and no conversion
for key, value in no_log.items():
    fig = plt.figure(figsize=(7, 11))
    my_dpi = 96
    sns.set(style='white')
    ax = sns.boxplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]], color='None',
                     fliersize=0, width=0.5,
                     linewidth=2)
    ax = sns.stripplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]],
                       palette=['#f17300', '#1f78b4', '#33a02c'],
                       size=7, jitter=True, lw=1, alpha=0.6)

    # Make the boxplot fully transparent
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0))

    ax.set_ylabel(song_variables[key-3] + ' (' + value + ')', fontsize=30)
    ax.set_xlabel('')
    ax.tick_params(labelsize=30, direction='out')
    ax.set(xticklabels=[])
    plt.setp(ax.spines.values(), linewidth=2)
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: "%.1f" % x))

    # # plt.tight_layout()
    # pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
    #                "/PaperVersion/" + sv + '.pdf')
    # pdf.savefig(orientation='landscape')
    # pdf.close()

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()

    plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
                "/PaperVersion_noLogAxis_largerFont/" + data_for_wrs.columns[key] + '_noLogAxis_largerFont' + '.pdf', type='pdf', dpi=fig.dpi,
                bbox_inches='tight', transparent=True)
    # plt.cla()
    # plt.clf()
    plt.close()

    # plt.show()

# are not log(value) so no need to take exponential, convert from Hz to kHz
for key, value in no_log_convert.items():
    fig = plt.figure(figsize=(7, 11))
    my_dpi = 96
    sns.set(style='white')
    ax = sns.boxplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]], color='None',
                     fliersize=0, width=0.5,
                     linewidth=2)
    ax = sns.stripplot(x='Region', y=data_for_wrs.columns[key], data=data_for_wrs[['Region', data_for_wrs.columns[key]]],
                       palette=['#f17300', '#1f78b4', '#33a02c'],
                       size=7, jitter=True, lw=1, alpha=0.6)

    # Make the boxplot fully transparent
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0))

    ax.set_ylabel(song_variables[key-3] + ' (' + value + ')', fontsize=30)
    ax.set_xlabel('')
    ax.tick_params(labelsize=30, direction='out')
    ax.set(xticklabels=[])
    plt.setp(ax.spines.values(), linewidth=2)
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: "%.1f" % (x/1000)))

    # # plt.tight_layout()
    # pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
    #                "/PaperVersion/" + sv + '.pdf')
    # pdf.savefig(orientation='landscape')
    # pdf.close()

    # manager = plt.get_current_fig_manager()
    # manager.window.showMaximized()

    plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported/BoxPlots_Norm"
                "/PaperVersion_noLogAxis_largerFont/" + data_for_wrs.columns[key] + '_noLogAxis_largerFont' + '.pdf', type='pdf', dpi=fig.dpi,
                bbox_inches='tight', transparent=True)
    # plt.cla()
    # plt.clf()
    plt.close()

    # plt.show()

""""
Binned heatmap showing geographical distribution of data
"""

# plot locations of all the song data collected --> this includes for all regions the unique songs and all songs
# chosen as use for possible duplicates

my_dpi = 96
fig = plt.figure(figsize=(2600 / my_dpi, 1800 / my_dpi), dpi=my_dpi, frameon=False)

# make the background map
m = Basemap(llcrnrlat=8, llcrnrlon=-169, urcrnrlat=72, urcrnrlon=-52)
m.drawcoastlines(color='k', linewidth=1.5)
m.drawcountries(color='k', linewidth=1.5)
m.drawstates(color='gray')
m.drawmapboundary(fill_color='w', color='none')

hb = m.hexbin(data_for_heatmaps['Longitude'], data_for_heatmaps['Latitude'], bins='log', mincnt=1, gridsize=50,
           cmap='cool')
cb = m.colorbar()

ticks_number = []
t_old = []
for t in cb.ax.get_yticklabels():
    t_old.append(float(t.get_text()))
    new_tick = float(t.get_text().replace(t.get_text(), str(int(round(10**float(t.get_text()))))))
    ticks_number.append(new_tick)
cb.set_ticks(t_old)
cb.set_ticklabels(["%.2f" % e for e in ticks_number])
cb.ax.tick_params(labelsize=25)
cb.set_label('Number', size=25)

plt.tight_layout()

pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported\GeoSpreadOfRecordings/" +
               'AllRecordingLocations_UniqueUse_logBins_rounded' + '.pdf')

pdf.savefig(dpi=fig.dpi, orientation='landscape', transparent=True)
pdf.close()

plt.show()

# plot locations of song data used for computations--> this includes all unique songs and all songs chosen as use for
# possible duplicates but only for East and West and South (excludes mid)
my_dpi = 96
fig = plt.figure(figsize=(2600 / my_dpi, 1800 / my_dpi), dpi=my_dpi, frameon=False)

# make the background map
m = Basemap(llcrnrlat=8, llcrnrlon=-169, urcrnrlat=72, urcrnrlon=-52)
m.drawcoastlines(color='k', linewidth=1.5)
m.drawcountries(color='k', linewidth=1.5)
m.drawstates(color='gray')
m.drawmapboundary(fill_color='w', color='none')

m.hexbin(data_for_wrs['Longitude'], data_for_wrs['Latitude'], bins='log', mincnt=1, gridsize=50, cmap='cool')
cb = m.colorbar()

ticks_number = []
t_old = []
for t in cb.ax.get_yticklabels():
    t_old.append(float(t.get_text()))
    new_tick = float(t.get_text().replace(t.get_text(), str(int(round(10**float(t.get_text()))))))
    ticks_number.append(new_tick)
cb.set_ticks(t_old)
cb.set_ticklabels(["%.2f" % e for e in ticks_number])
cb.ax.tick_params(labelsize=25)
cb.set_label('Number', size=25)

plt.tight_layout()

pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported\GeoSpreadOfRecordings/" +
               'EastWestSouthRecordingLocations_UniqueUse_logBins_rounded' + '.pdf')

pdf.savefig(dpi=fig.dpi, orientation='landscape', transparent=True)
pdf.close()

plt.show()


"""
Downsampling of data to check we get the same results - only one random sample from each lat/long
"""
pd.set_option("display.max_rows", 500)
# print(data_for_wrs.groupby(['Latitude', 'Longitude']).apply(lambda x: x.sample(1)).reset_index(drop=True))

# just checking my work
# print(data_for_wrs.shape)
print(data_for_wrs.duplicated(subset=('Latitude', 'Longitude')).sum())
print(data_for_wrs.groupby(['Latitude', 'Longitude'], as_index=False).size())
# print(len(data_for_wrs.groupby(['Latitude', 'Longitude']).apply(lambda x: x.sample(1)).reset_index(drop=True)))

# round to the third decimal place
data_for_wrs_rounded = data_for_wrs.round({'Latitude': 3, 'Longitude': 3})
data_downsampled = data_for_wrs_rounded.groupby(['Latitude', 'Longitude']).apply(lambda x: x.sample(1)).reset_index(drop=True)
# print(data_downsampled)

# plot the new geographical spread of subset of data
my_dpi = 96
fig = plt.figure(figsize=(2600 / my_dpi, 1800 / my_dpi), dpi=my_dpi)

m = Basemap(llcrnrlat=8, llcrnrlon=-169, urcrnrlat=72, urcrnrlon=-52)
m.drawcoastlines(color='k', linewidth=1.5)
m.drawcountries(color='k', linewidth=1.5)
m.drawstates(color='gray')
m.drawmapboundary(fill_color='w', color='none')

m.hexbin(data_downsampled['Longitude'], data_downsampled['Latitude'], bins='log', mincnt=1, gridsize=50, cmap='cool')
cb = m.colorbar()

ticks_number = []
t_old = []
for t in cb.ax.get_yticklabels():
    t_old.append(float(t.get_text()))
    new_tick = float(t.get_text().replace(t.get_text(), str(int(round(10**float(t.get_text()))))))
    ticks_number.append(new_tick)
cb.set_ticks(t_old)
cb.set_ticklabels(["%.2f" % e for e in ticks_number])
cb.ax.tick_params(labelsize=25)
cb.set_label('Number', size=25)

plt.tight_layout()

pdf = PdfPages("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported\GeoSpreadOfRecordings/" +
               'EastWestSouthRecordingLocations_UniqueUse_downsampled_logBins_rounded' + '.pdf')

pdf.savefig(dpi=fig.dpi, orientation='landscape', transparent=True)
pdf.close()

# plt.show()

ranksums_EW = pd.DataFrame(index=range(1000), columns=[data_for_wrs_rounded.columns[3:]])
ranksums_ES = pd.DataFrame(index=range(1000), columns=[data_for_wrs_rounded.columns[3:]])
ranksums_WS = pd.DataFrame(index=range(1000), columns=[data_for_wrs_rounded.columns[3:]])
for r in range(1000):
    sample = data_for_wrs_rounded.groupby(['Latitude', 'Longitude']).apply(lambda x: x.sample(1)).reset_index(drop=True)

    for sv in sample.columns[3:]:
        e = sample.loc[sample['Region'] == 'east', sv]
        w = sample.loc[sample['Region'] == 'west', sv]
        s = sample.loc[sample['Region'] == 'south', sv]

        ranksums_EW.iloc[r][sv] = ranksums(e, w)[1]
        ranksums_ES.iloc[r][sv] = ranksums(e, s)[1]
        ranksums_WS.iloc[r][sv] = ranksums(w, s)[1]

downsampling_results = pd.concat([ranksums_EW.max(axis=0), ranksums_EW.min(axis=0), ranksums_ES.max(axis=0),
                                  ranksums_ES.min(axis=0), ranksums_WS.max(axis=0), ranksums_WS.min(axis=0)],
                                 axis=1, keys=['EW_max', 'EW_min', 'ES_max', 'ES_min', 'WS_max', 'WS_min'])
downsampling_results.to_csv('C:/Users/abiga/Box '
                            'Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported/BoxPlots_Norm'
                            '/region_WilcoxonRanksums_downsampled.csv')

"""
See if there is a difference in spread of year of recording between East and West
"""

col_to_skip_notYear = ['CatalogNo', 'FromDatabase', 'ComparedStatus', 'RecordingDay', 'RecordingMonth', 'RecordingTime']
data_subset_wYear = log_song_data_unique.drop(col_to_skip_notYear, axis=1)
data_subset_wYear = data_subset_wYear.dropna(subset=['RecordingYear'])

with open('C:/Users/abiga/Box Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported/YearRegion'
          '/yearRegion_WilcoxonRanksums.csv', 'wb') as file:
    filewriter = csv.writer(file, delimiter=',')
    filewriter.writerow(['Song Variable', 'EW Wilcoxon p', 'EW p-value'])

    e = data_subset_wYear.loc[data_subset_wYear['Region'] == 'east', 'RecordingYear']
    w = data_subset_wYear.loc[data_subset_wYear['Region'] == 'west', 'RecordingYear']

    filewriter.writerow(['RecordingYear', ranksums(e, w)[0], ranksums(e, w)[1]])

# boxplot of the results

data_for_year = data_subset_wYear.drop(data_subset_wYear[data_subset_wYear.Region == 'mid'].index).copy().reset_index(drop=True)
data_for_year = data_for_year.drop(data_for_year[data_for_year.Region == 'south'].index).copy().reset_index(drop=True)

fig = plt.figure(figsize=(7, 11))
my_dpi = 96
sns.set(style='white',
        rc={"font.style": "normal",
            'lines.markersize': 2,
            'axes.labelsize': 20,
            'xtick.labelsize': 18,
            'ytick.labelsize': 18,
            })

ax = sns.boxplot(x='Region', y='RecordingYear',
                 data=data_for_year, order=['east', 'west'],
                 color='None',
                 fliersize=0, width=0.5,
                 linewidth=2)
ax = sns.stripplot(x='Region', y='RecordingYear',
                   data=data_for_year, order=['east', 'west'],
                   palette=['#1f78b4', '#33a02c'],
                   size=7, jitter=True, lw=1, alpha=0.6)

# Make the boxplot fully transparent
for patch in ax.artists:
    r, g, b, a = patch.get_facecolor()
    patch.set_facecolor((r, g, b, 0))

plt.setp(ax.spines.values(), linewidth=2)

plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported"
            "/YearRegion/yearRegionBoxPlot.pdf", type='pdf', dpi=fig.dpi,
            bbox_inches='tight', transparent=True)
# plt.cla()
# plt.clf()
plt.close()

plt.show()

"""
Downsampling by decade to check if we get the same results
"""

data_subset_wYear = data_subset_wYear.drop(data_subset_wYear[data_subset_wYear.Region == 'south'].index).\
    copy().reset_index(drop=True)

# use only east and west wilcoxon rank sums
data_for_sampleYear = data_subset_wYear.drop(data_subset_wYear[data_subset_wYear.Region == 'mid'].index).copy(). \
    reset_index(drop=True)

pd.set_option("display.max_rows", 500)

# just checking my work
data_for_sampleYear['Decade'] = [str(d)[2]+'0' for d in data_for_sampleYear['RecordingYear']]

num_per_decade = {'00': 25, '10': 78, '50': 7, '60': 15, '70': 13, '80': 8, '90': 30, 'n0': 0}
region_decade_groups = data_for_sampleYear.groupby(['Region', 'Decade'])
# print(data_for_sampleYear.groupby(['Region', 'Decade']).count())

downsampled_df = pd.DataFrame()
for name, group in data_for_sampleYear.groupby(['Region', 'Decade']):
    sample_num = num_per_decade[name[1]]
    downsampled_df = downsampled_df.append(group.sample(sample_num).reset_index(drop=True))
print(downsampled_df.shape)

# check the spread in year again now that it has been downsampled by decade
with open('C:/Users/abiga/Box Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported/YearRegion'
          '/yearRegionDownsampledByDecade_WilcoxonRanksums.csv', 'wb') as file:
    filewriter = csv.writer(file, delimiter=',')
    filewriter.writerow(['Song Variable', 'EW Wilcoxon p', 'EW p-value'])

    e = downsampled_df.loc[downsampled_df['Region'] == 'east', 'RecordingYear']
    w = downsampled_df.loc[downsampled_df['Region'] == 'west', 'RecordingYear']

    filewriter.writerow(['RecordingYear', ranksums(e, w)[0], ranksums(e, w)[1]])

# figure of one downsampling by decade
fig = plt.figure(figsize=(7, 11))
my_dpi = 96
sns.set(style='white',
        rc={"font.style": "normal",
            'lines.markersize': 2,
            'axes.labelsize': 20,
            'xtick.labelsize': 18,
            'ytick.labelsize': 18,
            })

ax = sns.boxplot(x='Region', y='RecordingYear',
                 data=downsampled_df, order=['east', 'west'],
                 color='None',
                 fliersize=0, width=0.5,
                 linewidth=2)
ax = sns.stripplot(x='Region', y='RecordingYear',
                   data=downsampled_df, order=['east', 'west'],
                   palette=['#1f78b4', '#33a02c'],
                   size=7, jitter=True, lw=1, alpha=0.6)

# Make the boxplot fully transparent
for patch in ax.artists:
    r, g, b, a = patch.get_facecolor()
    patch.set_facecolor((r, g, b, 0))

plt.setp(ax.spines.values(), linewidth=2)

plt.savefig("C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\StatsOfFinalData_withReChipperReExported"
            "/YearRegion/yearRegionBoxPlot_downsampledByDecade.pdf", type='pdf', dpi=fig.dpi,
            bbox_inches='tight', transparent=True)
# plt.cla()
# plt.clf()
plt.close()

# plt.show()


# now repeat the downsampling many times and conduct wilcoxon rank sum tests for each (keeping max and min p-value)
ranksums_EW = pd.DataFrame(index=range(1000), columns=[data_for_sampleYear.columns[4:]])

for r in range(1000):

    downsampled_df = pd.DataFrame()
    for name, group in data_for_sampleYear.groupby(['Region', 'Decade']):
        sample_num = num_per_decade[name[1]]
        downsampled_df = downsampled_df.append(group.sample(sample_num).reset_index(drop=True))

    for sv in downsampled_df.columns[3:]:
        e = downsampled_df.loc[downsampled_df['Region'] == 'east', sv]
        w = downsampled_df.loc[downsampled_df['Region'] == 'west', sv]

        ranksums_EW.iloc[r][sv] = ranksums(e, w)[1]

downsampling_results = pd.concat([ranksums_EW.max(axis=0), ranksums_EW.min(axis=0)],
                                 axis=1, keys=['EW_max', 'EW_min'])
downsampling_results.to_csv('C:/Users/abiga/Box '
                            'Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported/YearRegion'
                            '/yearRegion_WilcoxonRanksums_downsampledByDecade.csv')
