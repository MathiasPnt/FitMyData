# -*- coding: utf-8 -*-
"""
@author: Mathias
"""

import numpy as np

def get_g2_1input(dat_g2, peak_width, peak_sep, central_peak, num_peaks, baseline = True):

    bg_1 = np.zeros(num_peaks)
    bg_2 = np.zeros(num_peaks)

    p1 = np.zeros(num_peaks)
    p2 = np.zeros(num_peaks)


    for k in range(1, num_peaks + 1):
        bg_1[k - 1] = np.mean(dat_g2[int(central_peak + k * peak_sep + 2 * peak_width):
                                     int(central_peak + (k + 1) * peak_sep - 2 * peak_width)])
        bg_2[k - 1] = np.mean(dat_g2[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                                     int(central_peak- k * peak_sep - 2 * peak_width)])

    if baseline:
        bg = np.mean([bg_1, bg_2])
    else:
        bg = 0

    cent = np.sum(dat_g2[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)])- bg * (peak_width)
    err_cent = np.sqrt(cent)

    ct = 0
    for k in range(1, num_peaks + 1):
        p1[k - 1] = np.sum(dat_g2[int(central_peak - k * peak_sep - peak_width / 2):
                                  int(central_peak - k * peak_sep + peak_width / 2)]) - bg * (peak_width)
        p2[k - 1] = np.sum(dat_g2[int(central_peak + k * peak_sep - peak_width / 2):
                                  int(central_peak + k * peak_sep + peak_width / 2)]) - bg * (peak_width)
        ct = ct + 1

    peak = ((np.sum(p1) + np.sum(p2)) / 2 )/ ct
    err_peak = np.sqrt(peak)

    print(bg*peak_width, peak, cent, ct)

    g2 = cent / peak
    err_g2 = g2 * np.sqrt((err_cent / cent) ** 2 + (err_peak / peak) ** 2)

    return [g2, err_g2]


def get_HOM_1input(dat_HOM, peak_width, peak_sep, central_peak, num_peaks, baseline = False):

    bg_1 = np.zeros(num_peaks)
    bg_2 = np.zeros(num_peaks)

    p3 = np.zeros(num_peaks)
    p4 = np.zeros(num_peaks)

    if baseline:
        for k in range(1, num_peaks + 1):
            bg_1[k - 1] = np.mean(dat_HOM[int(central_peak + k * peak_sep + 2 * peak_width):
                                          int(central_peak + (k + 1) * peak_sep - 2 * peak_width)])

            bg_2[k - 1] = np.mean(dat_HOM[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                                          int(central_peak - k * peak_sep - 2 * peak_width)])
        bg = np.mean([bg_1, bg_2])
    else:
        bg = 0

    cent = np.sum(dat_HOM[int(central_peak - peak_width / 2):
                          int(central_peak + peak_width / 2)]-bg*peak_width)
    err_cent = np.sqrt(cent)

    ct = 0
    for k in range(1, num_peaks+1):
        p3[k-1] = np.sum(dat_HOM[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                                 int(central_peak - (k + 1) * peak_sep + peak_width / 2)]-bg*peak_width)

        p4[k-1] = np.sum(dat_HOM[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                                 int(central_peak + (k + 1) * peak_sep + peak_width / 2)]-bg*peak_width)
        ct = ct + 1

    peak = ((np.sum(p3) + np.sum(p4)) / 2) / ct
    err_peak = np.sqrt(peak)

    V = 1-(2*cent)/peak
    err_V = (1-V)*np.sqrt((err_cent / cent)**2 + (err_peak / peak)**2)

    return [V, err_V]


def get_HOM_2input(HOM_ortho, HOM_para, peak_width, peak_sep, central_peak, num_peaks):

    p1 = np.zeros(num_peaks)
    p2 = np.zeros(num_peaks)
    p3 = np.zeros(num_peaks)
    p4 = np.zeros(num_peaks)

    ct = 0
    for k in range(1, num_peaks+1):
        p1[k - 1] = np.sum(HOM_para[int(central_peak - k * peak_sep - peak_width / 2):
                                    int(central_peak - k * peak_sep + peak_width / 2)])

        p2[k - 1] = np.sum(HOM_para[int(central_peak + k * peak_sep - peak_width / 2):
                                    int(central_peak + k * peak_sep + peak_width / 2)])

        p3[k - 1] = np.sum(HOM_ortho[int(central_peak - k * peak_sep - peak_width / 2):
                                     int(central_peak - k * peak_sep + peak_width / 2)])

        p4[k - 1] = np.sum(HOM_ortho[int(central_peak + k * peak_sep - peak_width / 2):
                                     int(central_peak + k * peak_sep + peak_width / 2)])
        ct = ct + 1
    peak_para = (np.sum(p1) + np.sum(p2)) / 2 / ct
    peak_ortho = (np.sum(p3) + np.sum(p4)) / 2 / ct

    HOM_ortho_norm = HOM_ortho / peak_ortho  # not normalized to 1
    HOM_para_norm = HOM_para / peak_para

    n = num_peaks
    HOM_para_norm_factor = np.max(HOM_para_norm[int(central_peak - n * peak_sep):int(central_peak + n * peak_sep)])
    HOM_ortho_norm_factor = np.max(HOM_ortho_norm[int(central_peak - n * peak_sep):int(central_peak + n * peak_sep)])

    HOM_ortho_norm = HOM_ortho_norm / HOM_ortho_norm_factor  # normalized to 1
    HOM_para_norm = HOM_para_norm / HOM_para_norm_factor

    cent_para = np.sum(HOM_para_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)])
    err_cent_para = np.sqrt(np.sum(HOM_para[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)]))/peak_para

    cent_ortho = np.sum(HOM_ortho_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)])
    err_cent_ortho = np.sqrt(np.sum(HOM_ortho[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)]))/peak_ortho


    Visi = (cent_ortho - cent_para) / cent_ortho

    err_Visi = (1-Visi)*np.sqrt((err_cent_ortho / cent_ortho)**2 + (err_cent_para / cent_para)**2)


    return [Visi, HOM_ortho_norm, HOM_para_norm, err_Visi]