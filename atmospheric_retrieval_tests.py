#! /usr/bin/env python

"""
"""

import shutil

import numpy as np
from platon.constants import R_sun, R_jup, M_jup

from exoctk.atmospheric_retrievals.aws_tools import get_config
from exoctk.atmospheric_retrievals.examples import get_example_data
from exoctk.atmospheric_retrievals.platon_wrapper import PlatonWrapper

PARAMS_DICT = {}
PARAMS_DICT['hd209458b'] = {
    'params': {'Rs': 1.19, 'Mp': 0.73, 'Rp': 1.39, 'T': 1476.81, 'logZ': 0, 'CO_ratio': 0.53, 'log_cloudtop_P': 4, 'log_scatt_factor': 0, 'scatt_slope': 4, 'error_multiple': 1, 'log_cloudtop_P': 4},
    'R_guess': 1.39 * R_jup,
    'T_guess': 1476.81}
PARAMS_DICT['wasp-19b'] = {
    'params': {'Rs': 1.000, 'Mp': 1.069, 'Rp': 1.392, 'T': 2100.42, 'logZ': 0, 'CO_ratio': 0.53, 'log_cloudtop_P': 4, 'log_scatt_factor': 0, 'scatt_slope': 4, 'error_multiple': 1, 'log_cloudtop_P': 4},
    'R_guess': 1.392 * R_jup,
    'T_guess': 2100.42}
PARAMS_DICT['hat-p-1b'] = {
    'params': {'Rs': 1.17, 'Mp': 0.525, 'Rp': 1.319, 'T': 1322.67, 'logZ': 0, 'CO_ratio': 0.53, 'log_cloudtop_P': 4, 'log_scatt_factor': 0, 'scatt_slope': 4, 'error_multiple': 1, 'log_cloudtop_P': 4},
    'R_guess': 1.319 * R_jup,
    'T_guess': 1322.67}
PARAMS_DICT['hat-p-12b'] = {
    'params': {'Rs': 0.7, 'Mp': 0.211, 'Rp': 0.959, 'T': 957.35, 'logZ': 0, 'CO_ratio': 0.53, 'log_cloudtop_P': 4, 'log_scatt_factor': 0, 'scatt_slope': 4, 'error_multiple': 1, 'log_cloudtop_P': 4},
    'R_guess': 0.959 * R_jup,
    'T_guess': 957.35}


def process_data(method, target, iteration):
    """Performs a run of the ``emcee`` or `multinest`` retrievals using
    AWS.

    Parameters
    ----------
    method : str
        The method to use to perform the atmopsheric retrieval; can
        either be ``multinest`` or ``emcee``
    target : str
        The target to process (e.g. ``wasp-19b``)
    iteration : str
        The number of the iteration (e.g. ``1``, ``2``, etc.)
    """

    ssh_file = get_config()['ssh_file']
    ec2_id = get_config()['ec2_id']

    params = PARAMS_DICT[target]['params']
    R_guess = PARAMS_DICT[target]['R_guess']
    T_guess = PARAMS_DICT[target]['T_guess']

    # Initialize the object, set parameters, and perform retreival
    pw = PlatonWrapper()
    pw.set_parameters(params)

    if method == 'multinest':
        pw.fit_info.add_gaussian_fit_param('Rs', 0.02*R_sun)
        pw.fit_info.add_gaussian_fit_param('Mp', 0.04*M_jup)
        pw.fit_info.add_uniform_fit_param('Rp', 0.9*R_guess, 1.1*R_guess)
        pw.fit_info.add_uniform_fit_param('T', 300, 3000)
        pw.fit_info.add_uniform_fit_param("log_scatt_factor", 0, 2)
        pw.fit_info.add_uniform_fit_param("logZ", -1, 3)
        pw.fit_info.add_uniform_fit_param("log_cloudtop_P", -0.99, 7)
        pw.fit_info.add_uniform_fit_param("error_multiple", 0.5, 5)
    elif method == 'emcee':
        pw.fit_info.add_gaussian_fit_param('Rs', 0.02*R_sun)
        pw.fit_info.add_gaussian_fit_param('Mp', 0.04*M_jup)
        pw.fit_info.add_uniform_fit_param('Rp', 0, np.inf, 0.9*R_guess, 1.1*R_guess)
        pw.fit_info.add_uniform_fit_param('T', 300, 3000, 0.5*T_guess, 1.5*T_guess)
        pw.fit_info.add_uniform_fit_param("log_scatt_factor", 0, 5, 0, 3)
        pw.fit_info.add_uniform_fit_param("logZ", -1, 3)
        pw.fit_info.add_uniform_fit_param("log_cloudtop_P", -0.99, 8)
        pw.fit_info.add_uniform_fit_param("error_multiple", 0, np.inf, 0.5, 5)

    # Get bins, depths, and errors
    bins, depths, errors = get_example_data(target)
    pw.bins = bins
    pw.depths = depths
    pw.errors = errors

    # Set use for AWS and perform retreival
    # pw.use_aws(ssh_file, ec2_id)
    pw.retrieve(method)
    pw.save_results()
    pw.make_plot()

    # Save results
    shutil.copyfile('{}_corner.png'.format(method), 'results/{}_corner_{}_iter{}.png'.format(method, target, iteration))


if __name__ == '__main__':

    # methods = ['multinest'] * 20
    # targets = ['hd209458b'] * 5
    # targets.extend(['wasp-19b'] * 5)
    # targets.extend(['hat-p-1b'] * 5)
    # targets.extend(['hat-p-12b'] * 5)
    # iterations = ['1', '2', '3', '4', '5'] * 5

    # for method, target, iteration in zip(methods, targets, iterations):

    #     try:
    #         process_data(method, target, iteration)
    #     except:
    #         print('Unable to process: {} {} {}'.format(method, target, iteration))

    process_data('multinest', 'hd209458b', '1')
