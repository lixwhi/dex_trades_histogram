import csv
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timezone
from web3 import Web3
import json
import os


MIN_PRICE = 70
MAX_PRICE = 500
MAX_DAIUSD_ERROR = 1.15
gree = "#74e54708"
ree = "#e5475408"
gold = "#e5b64dff"
silver = '#a5a59dff'
grey3 = "#3d3d3dff"
ill_bid_color = '#2edc9aff'
oll_bid_color = '#86c620ff'
ill_ask_color = '#ea6439ff'
oll_ask_color = '#c51e36ff'
NUM_HOURS = 216
XMIN_PLOT = 0.97
XMAX_PLOT = 1.03
YMIN_PLOT_DAI_REMAINING = 100
YMAX_PLOT_DAI_REMAINING = 100000
YMIN_PLOT_HIST = 0
YMAX_PLOT_HIST = 50
YMAX_PLOT_ERROR_SIGNAL = 0.06
YMIN_PLOT_ERROR_SIGNAL = -0.06
NUM_BINS = 25

MIN_MISPRICED_DAI = 2000
INNER_LIQUID_LINE = MIN_MISPRICED_DAI
OUTER_LIQUID_LINE = 10000

MIN_BLOCKS_MISPRICED = 40

dex_filename = "ethdai-trades-9d-june.csv"
ethusd_filename = "gemini_ETHUSD_2019_1min_Jun.csv"
csv_outfile = "201906_DAIUSD_hourly_error-trades_9d"
png_output_filename = "trade_error_histogram_june_9d"
clean_filename = "cleaned_trades.csv"

def filter_bad(fn):
	with open(fn, 'r') as inp, open(clean_filename, 'w') as out:
		writer = csv.writer(out)
		for row in csv.reader(inp):
			if ((float(row[4]) < MAX_PRICE) and (float(row[4]) > MIN_PRICE)):
				writer.writerow(row)

	inp.close()
	out.close()




def main():
	# filter input prices
	filter_bad(dex_filename)
	# input
	dex_timestamp = np.loadtxt(open(clean_filename, "rb"), delimiter=",", skiprows=0, usecols=0)
	dex_timestamp = dex_timestamp.astype(int)
	price_dex_trade_occured = np.loadtxt(open(clean_filename, "rb"), delimiter=",", skiprows=0, usecols=4)
	ethusd_timestamp = np.loadtxt(open(ethusd_filename, "rb"), delimiter=",", skiprows=1, usecols=0)
	# reduce ethusd timestamp to match dex trade timestamps
	ethusd_timestamp = ethusd_timestamp / 1000
	ethusd_timestamp = ethusd_timestamp.astype(int)

	ethusd_high = np.loadtxt(open(ethusd_filename, "rb"), delimiter=",", skiprows=1, usecols=4)
	ethusd_low = np.loadtxt(open(ethusd_filename, "rb"), delimiter=",", skiprows=1, usecols=5)
	# use the midpoint of the high and low for that minute on gemini
	ethusd_mid = (ethusd_high + ethusd_low) / 2

	# Since I don't have ethusd data for every second, I must assume the ethusd price leads the
	# daiusd dex price. This is often the case because it takes a few blocks to confirm transactions 
	# after they are submitted. However, there is still information lost because the quality of the 
	# ethusd data. If I had ethusd pricing data down to the second, I would use it. For now,
	# I'm just going to round the dex prices down to the nearest minute. This will cause added
	# error to the daiusd error signal.
	# init arrays
	adjusted_dex_timestamp = np.empty(dex_timestamp.size)
	timestamp_day = np.empty(dex_timestamp.size)
	timestamp_month = np.empty(dex_timestamp.size)
	timestamp_hour = np.empty(dex_timestamp.size)
	ethusd_at_blocktime = np.empty(dex_timestamp.size)
	# daiusd_error = np.empty(dex_timestamp.size)
	# round down blocktimes trades occured to nearest minute
	for i in range(0, dex_timestamp.size):
		dayt = datetime.fromtimestamp(dex_timestamp[i])
		ts = datetime(year=dayt.year, month=dayt.month, day=dayt.day, hour=dayt.hour, minute=dayt.minute)
		ts.replace(tzinfo=timezone.utc)
		timestamp_day[i] = ts.day
		timestamp_month[i] = ts.month
		timestamp_hour[i] = ts.hour
		adjusted_dex_timestamp[i] = ts.timestamp()
	adjusted_dex_timestamp = adjusted_dex_timestamp.astype(int)
	timestamp_day = timestamp_day.astype(int)
	timestamp_month = timestamp_month.astype(int)
	timestamp_hour = timestamp_hour.astype(int)


	for i in range(0, adjusted_dex_timestamp.size):
		indx = np.where(ethusd_timestamp == adjusted_dex_timestamp[i])
		if(indx[0].size != 0):
			ethusd_at_blocktime[i] = ethusd_mid[indx[0][0]]


	# if error signal is negative, then DAI is weak
	# if error signal is positive, then DAI is strong
	daiusd_error = (ethusd_at_blocktime / price_dex_trade_occured)
	daiusd_error_abs = np.absolute(daiusd_error)
	indxmax = np.where(daiusd_error_abs > MAX_DAIUSD_ERROR)
	if (indxmax[0].size != 0):
		daiusd_error = np.delete(daiusd_error, indxmax[0])
		timestamp_hour = np.delete(timestamp_hour, indxmax[0])

	list_of_hours = []
	list_of_error = []
	hourly_mean_error = []
	hourly_median_error = []
	hourly_std = []
	prev_hour = timestamp_hour[0]
	hour_count = 0
	timestamp_out = []
	for i in range(0, daiusd_error.size):
		# calculate and plot stuff once per hour
		if (timestamp_hour[i] != prev_hour):
			derror = np.array(list_of_error)
			dmean = np.mean(derror)
			dmedian = np.median(derror)
			dstd = np.std(derror)
			hourly_mean_error.append(dmean)
			hourly_median_error.append(dmedian)
			hourly_std.append(dstd)
			list_of_hours.append(prev_hour)
			timestamp_out.append(adjusted_dex_timestamp[i])

			#plot it
			plot_hour(derror, hour_count, hourly_median_error, hourly_std, adjusted_dex_timestamp[i])
			prev_hour = timestamp_hour[i]
			list_of_error = []
			hour_count += 1

		list_of_error.append(daiusd_error[i])
	# do the final hour
	derror = np.array(list_of_error)
	dmean = np.mean(derror)
	dmedian = np.median(derror)
	dstd = np.std(derror)
	hourly_mean_error.append(dmean)
	hourly_std.append(dstd)
	hourly_median_error.append(dmedian)
	list_of_hours.append(timestamp_hour[timestamp_hour.size - 1])
	timestamp_out.append(adjusted_dex_timestamp[adjusted_dex_timestamp.size - 1])
	plot_hour(derror, hour_count, hourly_median_error, hourly_std, adjusted_dex_timestamp[adjusted_dex_timestamp.size - 1])
	save_error_signal(timestamp_out, hourly_median_error, hourly_std)

def save_error_signal (timestamp_out, hourly_median_error, hourly_std):
	first_hour = datetime.fromtimestamp(timestamp_out[0])
	last_hour = datetime.fromtimestamp(timestamp_out[len(timestamp_out) - 1])
	with open('{0}-{1}_{2}.csv'.format(first_hour.strftime("%Y%m%d%H"), last_hour.strftime("%Y%m%d%H"), csv_outfile), 'w+') as csvF:
		writer = csv.writer(csvF)
		head = ['timestamp', 'hourly_median_error', 'hourly_median_std']
		writer.writerow(head)
		for i in range(0, len(timestamp_out)):
			row = [int(timestamp_out[i]), round(hourly_median_error[i] - 1, 4), round(hourly_std[i], 6)]
			writer.writerow(row)
	csvF.close()

def plot_hour(trade_error, hour_count, hourly_median_error, hourly_std, timest):
	print('ploting {0}'.format(hour_count))
	dt = datetime.fromtimestamp(timest)
	
	fig = plt.figure()
	ax1 = plt.subplot2grid((3,1), (0,0), rowspan=2, colspan=1)
	#ax2 = plt.subplot2grid((4,2), (0,1), rowspan=3, colspan=1)
	ax3 = plt.subplot2grid((3,1), (2,0), rowspan=1, colspan=1)
	#ax4 = plt.subplot2grid((4,2), (3,1), rowspan=1, colspan=1)

	ax1.set_xlim(XMIN_PLOT, XMAX_PLOT)
	ax1.set_title('DAI/USD Trades from dai.stablecoin.science')
	ax1.set_ylabel('hourly trade distribution')
	ax1.axvline(np.median(trade_error), linewidth=0.75, color=gold)
	#ax1.axhline(INNER_LIQUID_LINE, linewidth=0.25)
	ax1.annotate(' hour count: {0}'.format(hour_count), (XMIN_PLOT, 48), xytext=(XMIN_PLOT, 48), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=grey3)
	ax1.annotate(' num trades: {0}'.format(trade_error.size), (XMIN_PLOT, 44), xytext=(XMIN_PLOT, 44), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=grey3)
	ax1.annotate(' timestamp: {0}'.format(timest), (XMIN_PLOT, 40), xytext=(XMIN_PLOT, 40), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=grey3)
	ax1.annotate(' {0}'.format(dt.strftime("%Y%m%d%-H")), (XMIN_PLOT, 36), xytext=(XMIN_PLOT, 36), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=grey3)

	# ax1.annotate('hourly WETH/DAI {0} ask depth'.format(INNER_LIQUID_LINE), (XMIN_PLOT, 0.25), xytext=(XMIN_PLOT, 0.25), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=ill_ask_color)
	# ax1.annotate('hourly WETH/DAI {0} ask depth'.format(OUTER_LIQUID_LINE), (XMIN_PLOT, 0.2), xytext=(XMIN_PLOT, 0.2), xycoords='data',textcoords='data', arrowprops=None, fontsize=8, color=oll_ask_color)
	ax1.set_ylim(YMIN_PLOT_HIST, YMAX_PLOT_HIST)
	#weights_te = np.ones_like(trade_error)/float(len(trade_error))
	ax1.hist(trade_error, bins='auto', color=grey3)

	ax3.set_xlabel('hours')
	ax3.axhline(0, linewidth=0.25)
	ax3.set_ylabel('DAI/USD error signal')
	ax3.set_xlim(0, NUM_HOURS)
	ax3.set_ylim(YMIN_PLOT_ERROR_SIGNAL, YMAX_PLOT_ERROR_SIGNAL)
	hme = np.asarray(hourly_median_error) - 1
	hstd = np.asarray(hourly_std)
	day0 = np.arange(0, hme.size)
	ax3.errorbar(day0, hme, yerr=hstd, fmt='o', markersize=0.7, color=grey3, capsize=0.8, elinewidth=0.5)


	fig.savefig(png_output_filename + str(hour_count) + '.png', dpi=250)
	fig.clf()
	plt.clf()


if __name__ == "__main__":
	main()

# # input price array
# old_filename = "201904_DAIUSD_hourly_error-old.csv"
# new_filename = "2019040223-2019040623_DAIUSD_hourly_error_signal-new.csv"
# title = "comparing sampling by trades vs order book depth"
# hour_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=0)
# hour_new = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=0)
# hour_old0 = np.arange(0, hour_old.size)
# hour_new0 = np.arange(0, hour_new.size)
# mean_error_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=1)
# mean_error_old = mean_error_old * 100
# std_error_old = np.loadtxt(open(old_filename, "rb"), delimiter=",", skiprows=1, usecols=2)
# std_error_old = std_error_old * 100
# error_new2 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=1)
# error_new2 = error_new2 * 100
# error_new10 = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=2)
# error_new10 = error_new10 * 100
# # std_error_new = np.loadtxt(open(new_filename, "rb"), delimiter=",", skiprows=1, usecols=2)
# # std_error_new = std_error * 100


# fig = plt.figure()
# st = fig.suptitle(title, fontsize=32)

# ax1 = plt.subplot(211)
# ax1.set_title(title)
# ax1.title.set_fontsize(18)
# ax1.set_ylabel("old sampling method with using trades")
# ax1.yaxis.label.set_fontsize(12)
# ax1.set_ylim(-5, 5)
# ax1.errorbar(hour_old0, mean_error_old, yerr=std_error_old, fmt='o')
# ax1.plot(mean_error_old)

# ax2 = plt.subplot(212)
# ax2.set_ylabel("new sampling method using order book")
# ax2.yaxis.label.set_fontsize(12)
# ax2.set_ylim(-5, 5)
# #ax2.errorbar(hour_new0, mean_error_new, yerr=std_error_new, fmt='o')
# ax2.plot(error_new2)
# ax2.plot(error_new10)


# plt.show()
































