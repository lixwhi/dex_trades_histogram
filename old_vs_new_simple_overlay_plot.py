import csv
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
gree = "#74e54708"
ree = "#e5475408"
gold = "#e5b64dff"
silver = '#a5a59dff'
grey3 = "#3d3d3dff"

# input price array
old_filename = "2019062100-2019062923_201906_DAIUSD_hourly_error-trades_9d.csv"
new_filename = "2019062100-2019062923_DAIUSD_hourly_error_signal-0621.csv"
title = "comparing sampling by trades vs order book depth"
time_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=0)
time_new = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=0)
hour_old0 = np.arange(0, time_old.size)
hour_new0 = np.arange(0, time_new.size)
x_time = np.linspace(time_old[0], time_old[time_old.size - 1], time_old[time_old.size - 1] - time_old[0] - 1)
median_error_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=1)
median_error_old = median_error_old * 100
std_error_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=2)
std_error_old = std_error_old * 100
median_error_new2 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=1)
median_error_new2 = median_error_new2 * 100
std_error_new2 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=2)
std_error_new2 = std_error_new2 * 100
median_error_new20 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=3)
median_error_new20 = median_error_new20 * 100
std_error_new20 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=4)
std_error_new20 = std_error_new20 * 100




fig, ax = plt.subplots()

ax.set_title(title)
ax.title.set_fontsize(18)
ax.set_ylabel("DAI/USD error signal")
ax.set_xlabel("hours")
ax.yaxis.label.set_fontsize(12)
ax.set_ylim(-5, 5)
ax.axhline(0, linewidth=0.25)

ax.annotate(' DAI/USD from trades', (1, 4.7), xytext=(1, 4.7), xycoords='data',textcoords='data', arrowprops=None, fontsize=10, color=grey3)
ax.annotate(' DAI/USD from orderbook 2000 depth', (1, 4.2), xytext=(1, 4.2), xycoords='data',textcoords='data', arrowprops=None, fontsize=10, color=gold)
ax.annotate(' DAI/USD from orderbook 20000 depth', (1, 3.7), xytext=(1, 3.7), xycoords='data',textcoords='data', arrowprops=None, fontsize=10, color=silver)

ax.errorbar(hour_old0, median_error_old, yerr=std_error_old, fmt='o', markersize=1.7, color=grey3, capsize=2, ls='-', elinewidth=0.85)
ax.errorbar(hour_new0, median_error_new2, yerr=std_error_new2, fmt='o', markersize=1.7, color=gold, capsize=2, ls='-', elinewidth=0.85)
ax.errorbar(hour_new0, median_error_new20, yerr=std_error_new20, fmt='o', markersize=1.7, color=silver, capsize=2, ls='-', elinewidth=0.85)
#ax.plot(mean_error_old)

# ax2 = plt.subplot(212)
# ax2.set_ylabel("new sampling method using order book")
# ax2.yaxis.label.set_fontsize(12)
# ax2.set_ylim(-5, 5)
# #ax2.errorbar(hour_new0, mean_error_new, yerr=std_error_new, fmt='o')
# ax2.plot(error_new2)
# ax2.plot(error_new10)


plt.show()
































