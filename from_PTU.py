# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the histogram as an array from a PTU file.
Input: .PTU using Mode 2 on ch 1 and 2. Either path OR file from streamlit

Output: Returns the histogram

"""

from readPTU import PTUfile, PTUmeasurement
import os

def get_ptu_frompath(path):

    with PTUfile(path) as ptu_file:

        ptu_meas = PTUmeasurement(ptu_file)
        g2_resolution = ptu_file.tags['MeasDesc_Resolution']['value']
        g2_window = g2_resolution * 65536
        hist_x, hist_y = ptu_meas.calculate_g2(g2_window,
                                               g2_resolution,
                                               channel_start=1,
                                               channel_stop=2,
                                               post_selec_ranges=None,
                                               n_threads=4,
                                               mode='symmetric')

    return hist_x, hist_y

def get_ptu_fromfile(streamlit_file):
    directory = os.getcwd()
    # file is a file that has been uploaded using streamlit
    if streamlit_file is not None:
        local_path = directory + os.sep + "temporaryfile.ptu"
        with open(local_path, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(streamlit_file.read())

            hist_x, hist_y = get_ptu_frompath(local_path)

            os.remove(local_path)

            return hist_x, hist_y
