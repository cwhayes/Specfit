from __future__ import print_function, division
import matplotlib.pyplot as plt
import numpy as np
from astropy import modeling
from astropy.io import fits
from astropy.wcs import WCS
from astropy.convolution import convolve, Box1DKernel

##############################################
#              USEFUL FUNCTIONS              #
##############################################

# Create interactive display of the data
def onclick(event):
	global pts
	if (pts == 0):
		print('Please click the right edge of the region.')
	xpts.append(event.xdata)
	pts += 1
	if (pts == 2):
		plt.figure(figsize=(20,6))
		plt.xlim([xpts[0] - 50, xpts[1] + 50])
		plt.axvspan(xpts[0], xpts[1], alpha=0.5, color='red')
		fig.canvas.draw()

		print('Please close the plot window now.')

# Import the fits file and grab the data
def importfits(filename):
	hdulist = fits.open(filename)
	hdu0 = hdulist[0]
	nlam = hdu0.header['NAXIS1']

	wcs = WCS(hdu0.header).sub([1])
	
	wave = wcs.all_pix2world(np.arange(nlam), 0)[0]
	data = hdu0.data[1]

	mask_left = int(raw_input('Please enter left end of mask: '))
	mask_right = int(raw_input('Please enter right end of mask: '))

	mask = (wave > mask_left) & (wave < mask_right)

	box_width = int(raw_input('Please enter box width: '))
	kernel = Box1DKernel(box_width)
	spec_smooth = convolve(hdu0.data[1, mask], kernel, normalize_kernel=True)

	return(wave[mask], spec_smooth)

##############################################
#             THE ACTUAL PROGRAM             #
##############################################

filename = raw_input('Please enter file name: ')

x, y = importfits(filename)

# Running the interactive plot
while True:
	pts = 0
	xpts = []
	ypts = []

	fig,ax = plt.subplots()
	ax.plot(x, y, 'ok')
	fig.canvas.mpl_connect('button_press_event', onclick)
	print('Please click the left edge of the region.')
	plt.show()

	print('Left edge: ', xpts[0])
	print('Right edge: ', xpts[1])
	to_continue = raw_input('Would you like to try again? (y/n) ')

	if (to_continue == 'y'):
		continue
	else:
		break

print('Region accepted!')

# Picking out only the selected data
masked_x = []
masked_y = []

for i in range(len(x)):
	if ( (x[i] > xpts[0]) and (x[i] < xpts[1]) ):
		masked_x.append(x[i])
		masked_y.append(y[i])

# Plotting the full data vs the selected data
plt.plot(x, y, 'ok')
plt.plot(masked_x, masked_y, 'oy')
plt.axvspan(xpts[0], xpts[1], alpha=0.5, color='red')
plt.xlim([xpts[0] - 50, xpts[1] + 50])
plt.show()

# Creating the fit
x2 = np.linspace(xpts[0], xpts[1], len(masked_x))
fitter = modeling.fitting.LevMarLSQFitter()
model = modeling.models.Gaussian1D(amplitude=10**-17, mean=np.mean(xpts))
fitted_model = fitter(model, x2, masked_y)

print(fitted_model)

# Plotting the  fit with the data
plt.plot(x, y, 'ok')
plt.plot(masked_x, masked_y, 'oy')
plt.plot(x2, fitted_model(x2), color = 'green')
plt.axvspan(xpts[0], xpts[1], alpha=0.5, color='red')
plt.xlim([xpts[0] - 50, xpts[1] + 50])
plt.show()
