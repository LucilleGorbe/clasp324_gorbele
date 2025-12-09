'''
This code takes input windspeedRH data and will run an awesome fourier
transform on it. :D
'''

import numpy as np
import matplotlib.pyplot as plt

from scipy.fft import fft, fftfreq
plt.style.use("seaborn-v0_8")

def data_import(fname):
    '''
    Generates and processes data from eddy covariance sensor into real units.
    Additionally performs fourier analysis on the data and plots the results.
    
    Parameters
    ----------
    fname : str
        Input filename to generate data from.

    Returns
    -------
    fig : matplotlib figure object
        The figure to be plotted on.
    '''

    data = np.genfromtxt(fname, delimiter="  ", names=["AH", "Temp_AH101", "Wind_Speed", "Elapsed_Time"], skip_header=2)
    
    # Calculate and report frequency for the data
    freq = 1/((data["Elapsed_Time"][-1]/1000)/data["Elapsed_Time"].size)
    print(f"Frequency: {freq:.2f}")
    
    # filter out junky data
    data = data[data["AH"] < 100]

    # Get absolute humidity, temperature, and windspeed data
    AH = data["AH"]
    temp = data["Temp_AH101"]
    windspeed = data["Wind_Speed"]
    time = data["Elapsed_Time"]/1000  # convert to seconds

    # Use Buck vapor saturation pressure parametrization to convert AH to RH
    esat = (temp >= 0) * (6.1121 * np.exp((18.678 - (temp / 234.5)) * (temp / (257.14 + temp)))) + (temp < 0) * (6.1115 * np.exp((23.036 - (temp /333.7)) * (temp / (279.82 + temp))))

    # calculate instantaneous water vapor density and flux
    rho = AH * esat / (0.46152 * (temp + 273.15)) * 1e6  # g/cm^3

    # Force data to be stationary to find inst. changes
    # Normally achieved by simply subtracting average windspeed/rho
    # But due to sys error, trying w/ subtracting that
    deg = 3
    N = windspeed.size
    ind = np.arange(N)
    wscoefs = np.polyfit(ind, windspeed, deg=deg)
    wspasslin = np.polyval(wscoefs, ind)
    wsDev = windspeed - wspasslin

    rhocoefs = np.polyfit(ind, rho, deg=deg)
    rhopasslin = np.polyval(rhocoefs, ind)
    rhoDev = rho - rhopasslin

    # Calculate the inst. water vapor flux
    wvFlux = wsDev * rhoDev
    wvfft = fft(wvFlux)
    wvfreq = fftfreq(N, 1/freq)  # size of array and time step of points

    print(f"Total water vapor flux: {np.average(wvFlux)}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))

    # Plot normalized frequency data
    ax1.plot(wvfreq[:N//2]/(2*np.pi), 2.0/N * np.abs(wvfft[:N//2]), '-')
    ax1.plot(wvfreq[:N//2]/(2*np.pi), 2.0/N * np.abs(wvfft[:N//2]), 'o')
    ax1.set_title("Fourier Analysis of Data")
    ax1.set_xlabel("Frequency")
    ax1.set_ylabel(r"Flux Amplitude ($\frac{g}{m^2*s}$)")

    # Plot time series data
    ax2.plot(time, wvFlux)
    ax2.set_title("Time series flux data")
    ax2.set_xlabel("Time ($s$)")
    ax2.set_ylabel(r"Flux ($\frac{g}{m^2*s}$)")

    return fig
