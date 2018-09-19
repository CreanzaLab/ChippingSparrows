import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import seaborn as sns; sns.set()
import csv
from mpl_toolkits.basemap import Basemap
from scipy.stats import ranksums

"""
Load song and recorder type data, organize/subset for testing differences in recorder type
"""
data_path = 'C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\FinalDataCompilation' + \
            '/FinalDataframe_CombinedTables_withReChipper_thenWithReExportedAs44100Hz_LogTransformed.csv'
log_song_data = pd.DataFrame.from_csv(data_path, header=0, index_col=None)

# remove all duplicate birdsongs
# keep unique and use (which is the one I choose if there were multiples from the same bird)
log_song_data_unique = log_song_data.loc[log_song_data['ComparedStatus'].isin(['unique', 'use'])].copy().reset_index(
    drop=True)

# drop any metadata that is not needed for this analysis and any missing data
col_to_skip = ['FromDatabase', 'ComparedStatus', 'RecordingDay', 'RecordingMonth', 'RecordingYear',
               'RecordingTime']
data_for_song = log_song_data_unique.drop(col_to_skip, axis=1).dropna(axis=0)
fn = lambda x: x['CatalogNo'].split('.')[0]
data_for_song['CatalogNo'] = data_for_song.apply(fn, axis=1)
# data_for_song.to_csv('C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject\FinalDataCompilation' + \
#             '/testingCatalogNo.csv')

# load recorder data
recorder_path = "C:/Users/abiga\Box Sync\Abigail_Nicole\ChippiesProject/recorder spreadsheets from nicole/recorder " \
                "data.csv"
data_for_rec = pd.DataFrame.from_csv(recorder_path, header=0, index_col=None)
data_for_rec['CatalogNo'] = data_for_song['CatalogNo'].astype(object)

# combine tables using CatalogNo
combined_table = data_for_song.merge(data_for_rec, on='CatalogNo')

#divide up by signal type
analog = combined_table[combined_table.SignalType == 'Analog']
digital = combined_table[combined_table.SignalType == 'Digital']

#divide up by recorder type
reelToReel = combined_table[combined_table.RecorderType == 'Reel-to-reel']
digitalRec = combined_table[combined_table.RecorderType == 'Digital recorder']


"""
Location of data, colored by signal type
"""

# Set the dimension of the figure
my_dpi = 96
fig = plt.figure(figsize=(2600 / my_dpi, 1800 / my_dpi), dpi=my_dpi, frameon=False)

#make the geographic background map
m = Basemap(llcrnrlat=10, llcrnrlon=-140, urcrnrlat=65, urcrnrlon=-62)
m.drawcoastlines(color='gray')
m.drawcountries(color='k', linewidth=1)
m.drawstates(color='gray')
m.drawmapboundary(fill_color='w', color='none')

# # #plot points at sampling locations
# m.scatter(analog['Longitude'], analog['Latitude'], latlon=True, label=None, zorder=10, c='#dfc27d',
#           edgecolor='black', linewidth=1)
#
# #plot points at sampling locations
# m.scatter(digital['Longitude'], digital['Latitude'], latlon=True, label=None, zorder=10, c='#8c510a',
#           edgecolor='black', linewidth=1)

# #plot points at sampling locations
m.scatter(reelToReel['Longitude'], reelToReel['Latitude'], latlon=True, label=None, zorder=10, c='#dfc27d',
          edgecolor='black', linewidth=1)

#plot points at sampling locations
m.scatter(digitalRec['Longitude'], digitalRec['Latitude'], latlon=True, label=None, zorder=10, c='#8c510a',
          edgecolor='black', linewidth=1)

plt.tight_layout()

plt.savefig("C:/Users/abiga/Box Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported"
            "/RecorderAnalysis/recorderType_geoSpreadOfData_reelToReelLightdigitalRecDark.pdf", type='pdf', dpi=fig.dpi,
            bbox_inches='tight')

# plt.show()

""""
Wilcoxon Ranksums
"""
with open('C:/Users/abiga/Box Sync/Abigail_Nicole/ChippiesProject/StatsOfFinalData_withReChipperReExported'
          '/RecorderAnalysis/recorder_WilcoxonRanksums.csv', 'wb') as file:
    filewriter = csv.writer(file, delimiter=',')
    filewriter.writerow(['Song Variable', 'Analog vs Digital w', 'Analog vs Digital p-value', 'ReelToReel vs '
                                                                                              'DigitalRec w',
                         'ReelToReel vs DigitalRec p-value'])

    for sv in (['Longitude'] + combined_table.columns[4:-5].tolist()):
        a = np.asarray(analog[sv])
        d = np.asarray(digital[sv])
        rr = np.asarray(reelToReel[sv])
        dr = np.asarray(digitalRec[sv])
        filewriter.writerow([sv, ranksums(a, d)[0], ranksums(a, d)[1], ranksums(rr, dr)[0], ranksums(rr, dr)[1]])