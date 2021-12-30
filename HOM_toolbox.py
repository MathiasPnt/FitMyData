# -*- coding: utf-8 -*-
"""
@Author: Mathias Pont
"""

import numpy as np
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt

def find_sidepeaks(data):
    # Peak finder
    # peaks is a list of the index of all peaks with a certain prominence and width
    peaks, properties = find_peaks(data, prominence=np.max(data)/2, width=4)

    if len(peaks)==0:
        return "Error: no peaks found"
        plt.figure()
        plt.plot(data)

    # histogram with only the side peaks
    data_pk = data[peaks]

    to_delete = np.where(data_pk < max(data_pk) / 2)
    data_pk = np.delete(data_pk, to_delete)
    peaks = np.delete(peaks, to_delete)

    # Gets the width of the peaks. With 1 we take the full peak. 0.99 allows to get rid of the unwanted noise.
    results_full = peak_widths(data, peaks, rel_height=0.99)

    # get all peak separation
    p_sep = []
    for i in range(len(peaks) - 1):
        to_add = peaks[i + 1] - peaks[i]
        p_sep = p_sep + [to_add]

    # delete the separation that corresponds to the central peak
    # to_delete is then also the index of the first "side peak" in peaks.
    to_delete = np.where(p_sep > np.mean(p_sep) + np.std(p_sep))
    p_sep = np.delete(p_sep, to_delete)

    # Use the mean value and int
    pk_width = int(np.mean(results_full[0]))  # widths
    pk_sep = int(np.mean(p_sep))
    # WE ONLY USE THE FIST OCCURENCE OF A 2 PEAK SEPARATION TO GET THE CENTER PX
    ct_peak = int(peaks[to_delete][0] + pk_sep) + 1

    return peaks, data_pk, ct_peak, pk_sep, pk_width

def get_baseline(data, central_pk, pk_width, pk_sep, num_pks):
    if 4*pk_width > pk_sep:
        print("Error: No baseline, peak is too wide")
        bg = 0
        return bg
    else:
        # Baseline right side (positive times)
        # We integrate starting 2*peakwidth after the first peak and 2*peakwidth before the second.
        bg_1 = [np.mean(data[int(central_pk + k * pk_sep + 2 * pk_width):
                             int(central_pk + (k + 1) * pk_sep - 2 * pk_width)])
                for k in range(1, num_pks + 1)]
        # Baseline left side (negative times)
        bg_2 = [np.mean(data[int(central_pk - (k + 1) * pk_sep + 2 * pk_width):
                             int(central_pk - k * pk_sep - 2 * pk_width)])
                for k in range(1, num_pks + 1)]

        bg = np.mean([bg_1, bg_2])
        return bg


def get_g2_1input(dat_g2, peak_width, peak_sep, central_peak, num_peaks, baseline = True):

    if baseline:
        bg = get_baseline(dat_g2, central_peak, peak_width, peak_sep, num_peaks)
    else:
        bg = 0

    # Integration of central peak - baseline * width peak (which is the window of integration here)
    cent = np.sum(dat_g2[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)]) - bg * peak_width
    err_cent = np.sqrt(cent)

    # k will go from 1 to num_peaks
    #We fill p1 and p2 starting at index 0
    p1 = [np.sum(dat_g2[int(central_peak - k * peak_sep - peak_width / 2):
                        int(central_peak - k * peak_sep + peak_width / 2)])
          - bg * peak_width
          for k in range(1, num_peaks+1)]
    p2 = [np.sum(dat_g2[int(central_peak + k * peak_sep - peak_width / 2):
                        int(central_peak + k * peak_sep + peak_width / 2)])
          - bg * peak_width
          for k in range(1, num_peaks + 1)]

    peak = (np.sum(p1) + np.sum(p2)) / 2 / num_peaks
    err_peak = np.sqrt(peak)

    g2 = cent / peak
    err_g2 = g2 * np.sqrt((err_cent / cent) ** 2 + (err_peak / peak) ** 2)

    return g2, err_g2

def get_HOM_1input(dat_HOM, peak_width, peak_sep, central_peak, num_peaks, baseline = True):

    if baseline:
        bg = get_baseline(dat_HOM, central_peak, peak_width, peak_sep, num_peaks)
    else:
        bg = 0

    cent = np.sum(dat_HOM[int(central_peak - peak_width / 2):
                          int(central_peak + peak_width / 2)]) - bg * peak_width
    err_cent = np.sqrt(cent)

    ct = 0
    # k will go from 1 to num_peaks

    # We fill p1 and p2 starting at index 0
    p1 = [np.sum(dat_HOM[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                         int(central_peak - (k + 1) * peak_sep + peak_width / 2)]) - bg * peak_width
          for k in range(1, num_peaks + 1)]

    p2 = [np.sum(dat_HOM[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                         int(central_peak + (k + 1) * peak_sep + peak_width / 2)]) - bg * peak_width
          for k in range(1, num_peaks + 1)]

    peak = (np.sum(p1) + np.sum(p2)) / 2 / num_peaks
    err_peak = np.sqrt(peak)

    V = 1 - 2 * cent / peak
    err_V = (1-V)*np.sqrt((err_cent / cent)**2 + (err_peak / peak)**2)

    return V, err_V

def get_HOM_2input(HOM_ortho, HOM_para, num_peaks=6, baseline = True, plotit = False, manualmode = False,
                   ct_peak=1557, peak_sp=190, peak_w=35):
    """
    :param HOM_ortho: list - histogram of 2-photon correlation with orthogonal polarisation
    :param HOM_para: list - histogram of 2-photon correlation with parallel polarisation
    :param num_peaks: int - number of peaks to integrate
    :param baseline: bool - subtract baseline
    :param plotit:  bool - plot it
    :return: float, float, list, list - 2-photon visibility, err on V, norm. histo ortho, norm histo para
    """

    peaks_ortho, data_pk_ortho, central_peak_ortho, peak_sep_ortho, peak_width_ortho = find_sidepeaks(HOM_ortho)
    peaks_para, data_pk_para, central_peak_para, peak_sep_para, peak_width_para = find_sidepeaks(HOM_para)

    if [central_peak_ortho, peak_sep_ortho, peak_width_ortho] == [central_peak_para, peak_sep_para, peak_width_para]:
        central_peak, peak_sep, peak_width = central_peak_ortho, peak_sep_ortho, peak_width_ortho
    else:
        central_peak, peak_sep, peak_width = central_peak_ortho, peak_sep_ortho, peak_width_ortho
        print('Error: the 2 histo do not seem to match')

    if manualmode:
        central_peak, peak_sep, peak_width = ct_peak, peak_sp, peak_w

    if baseline:
        bg_1 = [np.mean(HOM_para[int(central_peak + k * peak_sep + 2 * peak_width):
                                 int(central_peak + (k + 1) * peak_sep - 2 * peak_width)])
                for k in range(1, num_peaks + 1)]

        bg_2 = [np.mean(HOM_para[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                                 int(central_peak - k * peak_sep - 2 * peak_width)])
                for k in range(1, num_peaks + 1)]

        bg_3 = [np.mean(HOM_ortho[int(central_peak + k * peak_sep + 2 * peak_width):
                                  int(central_peak + (k + 1) * peak_sep - 2 * peak_width)])
                for k in range(1, num_peaks + 1)]

        bg_4 = [np.mean(HOM_ortho[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                                  int(central_peak - k * peak_sep - 2 * peak_width)])
                    for k in range(1, num_peaks + 1)]
        bg_para = np.mean([bg_1, bg_2])
        bg_ortho = np.mean([bg_3, bg_4])

        HOM_para = [x - bg_para for x in HOM_para]
        HOM_ortho = [x - bg_ortho for x in HOM_ortho]


    p1 = [np.sum(HOM_para[int(central_peak - k * peak_sep - peak_width / 2):
                          int(central_peak - k * peak_sep + peak_width / 2)])
            for k in range(1, num_peaks + 1)]

    p2 = [np.sum(HOM_para[int(central_peak + k * peak_sep - peak_width / 2):
                          int(central_peak + k * peak_sep + peak_width / 2)])
          for k in range(1, num_peaks + 1)]

    p3 = [np.sum(HOM_ortho[int(central_peak - k * peak_sep - peak_width / 2):
                           int(central_peak - k * peak_sep + peak_width / 2)])
          for k in range(1, num_peaks + 1)]

    p4 = [np.sum(HOM_ortho[int(central_peak + k * peak_sep - peak_width / 2):
                           int(central_peak + k * peak_sep + peak_width / 2)])
          for k in range(1, num_peaks + 1)]

    ct = len(p1)
    peak_para = (np.sum(p1) + np.sum(p2)) / 2 / ct
    peak_ortho = (np.sum(p3) + np.sum(p4)) / 2 / ct

    HOM_ortho_norm = HOM_ortho / peak_ortho  # not normalized to 1
    HOM_para_norm = HOM_para / peak_para

    # get all peak separation
    p_sep = []
    for i in range(len(peaks_ortho) - 1):
        to_add = peaks_ortho[i + 1] - peaks_ortho[i]
        p_sep = p_sep + [to_add]

    central_index = int(np.where(p_sep > np.mean(p_sep) + 2*np.std(p_sep))[0][0])

    data_pk_ortho_norm = HOM_ortho_norm[peaks_ortho]
    data_pk_para_norm = HOM_para_norm[peaks_para]


    HOM_para_norm_factor = np.mean(data_pk_para_norm[central_index-num_peaks:central_index-2]+
                                   data_pk_para_norm[central_index+2:central_index+num_peaks])/2
    HOM_ortho_norm_factor = np.mean(data_pk_ortho_norm[central_index-num_peaks:central_index-2]+
                                    data_pk_ortho_norm[central_index+2:central_index+num_peaks])/2

    HOM_ortho_norm = HOM_ortho_norm / HOM_ortho_norm_factor  # normalized to 1
    HOM_para_norm = HOM_para_norm / HOM_para_norm_factor

    cent_para = np.sum(HOM_para_norm[int(central_peak - peak_width / 2):
                                     int(central_peak + peak_width / 2)])
    err_cent_para = np.sqrt(np.sum(HOM_para[int(central_peak - peak_width / 2):
                                            int(central_peak + peak_width / 2)]))/peak_para

    cent_ortho = np.sum(HOM_ortho_norm[int(central_peak - peak_width / 2):
                                       int(central_peak + peak_width / 2)])
    err_cent_ortho = np.sqrt(np.sum(HOM_ortho[int(central_peak - peak_width / 2):
                                              int(central_peak + peak_width / 2)]))/peak_ortho

    V = (cent_ortho - cent_para) / cent_ortho

    errV = (1-V)*np.sqrt((err_cent_ortho / cent_ortho)**2 + (err_cent_para / cent_para)**2)

    if plotit:
        title_fig = 'HOM =' + str(round(V, 4)) + '±' + str(round(errV, 4))
        time = np.arange(0, len(HOM_para))
        # PLot it
        fig, ax = plt.subplots()
        ax.set_title(title_fig)
        ax.plot(time, HOM_ortho_norm, '-o', label = 'Ortho')
        ax.plot(time, HOM_para_norm, '-o', label = 'Para')
        # Center peak
        ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                HOM_para_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                color = 'seagreen')
        ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                HOM_ortho_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                color='seagreen')

        ax.axhline(1, linestyle='--', color='dimgray')
        ax.axhline(0.75, linestyle='--', color='dimgray')
        ax.axhline(0.5, linestyle='--', color='dimgray')

        ax.set_xlim(central_peak - 5 * peak_sep, central_peak + 5 * peak_sep)
        ax.axvline(central_peak, linestyle='--')
        ax.legend()


    return V, errV, HOM_ortho_norm, HOM_para_norm

def plot_histo(string, data, num_peaks = 6):
    """
    :param string: str - 'HOM' or 'g2'
    :param data: list - histogram of 2-photon correlation
    :return: int - central_peak, peak_sep, peak_width, num_peaks
    """

    peaks, data_pk, central_peak, peak_sep, peak_width = find_sidepeaks(data)

    if string == 'HOM':
        HOM, errHOM = get_HOM_1input(data, peak_width, peak_sep, central_peak, num_peaks)
        title_fig = 'HOM =' + str(round(HOM, 4)) + '±' + str(round(errHOM, 4))
    if string == 'g2':
        g2, errg2 = get_g2_1input(data, peak_width, peak_sep, central_peak, num_peaks)
        title_fig = 'g2 =' + str(round(g2, 4)) + '±' + str(round(errg2, 4))

    time = np.arange(0, len(data))

    # PLot it
    fig, ax = plt.subplots()
    ax.set_title(title_fig)
    ax.bar(time, data)
    #ax.plot(time, data, '-o')
    ax.plot(peaks, data_pk, 'o', markersize = 6, color = 'gold')
    if string == 'HOM':
        # Side peaks left
        [ax.plot(time[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                      int(central_peak - (k + 1) * peak_sep + peak_width / 2)],
                 data[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                      int(central_peak - (k + 1) * peak_sep + peak_width / 2)],
                 color='gold') for k in range(1,num_peaks+1)]
        # Side peaks right
        [ax.plot(time[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                      int(central_peak + (k + 1) * peak_sep + peak_width / 2)],
                 data[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                      int(central_peak + (k + 1) * peak_sep + peak_width / 2)],
                 color='gold') for k in range(1, num_peaks + 1)]

    if string == 'g2':
        # Side peaks left
        [ax.plot(time[int(central_peak - k * peak_sep - peak_width / 2):
                      int(central_peak - k * peak_sep + peak_width / 2)],
                 data[int(central_peak - k * peak_sep - peak_width / 2):
                      int(central_peak - k * peak_sep + peak_width / 2)],
                 color='gold') for k in range(1, num_peaks + 1)]
        # Side peaks right
        [ax.plot(time[int(central_peak + k * peak_sep - peak_width / 2):
                      int(central_peak + k * peak_sep + peak_width / 2)],
                 data[int(central_peak + k * peak_sep - peak_width / 2):
                      int(central_peak + k * peak_sep + peak_width / 2)],
                 color='gold') for k in range(1, num_peaks + 1)]
    # Center peak
    ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
            data[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
            )
    # Baseline right
    [ax.plot(time[int(central_peak + k * peak_sep + 2 * peak_width):
                  int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
             data[int(central_peak + k * peak_sep + 2 * peak_width):
                  int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
            color='red') for k in range(1, num_peaks + 1)]

    # Baseline left
    [ax.plot(time[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                  int(central_peak - k * peak_sep - 2 * peak_width)],
             data[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                  int(central_peak - k * peak_sep - 2 * peak_width)],
             color='red') for k in range(1, num_peaks + 1)]

    ax.set_xlim(central_peak-(num_peaks+2)*peak_sep, central_peak+(num_peaks+2)*peak_sep)

    ax.axvline(central_peak, linestyle='--')

    return central_peak, peak_sep, peak_width, num_peaks
