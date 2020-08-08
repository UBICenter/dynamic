'''
Example script for setting policy and running OG-USA.
'''

# import modules
import multiprocessing
from distributed import Client
import time
import numpy as np
import os
import taxcalc
from taxcalc import Calculator
from ogusa import output_tables as ot
from ogusa import output_plots as op
from ogusa.execute import runner
from ogusa.constants import REFORM_DIR, BASELINE_DIR
from ogusa.utils import safe_read_pickle


def main():
    # Define parameters to use for multiprocessing
    client = Client()
    num_workers = min(multiprocessing.cpu_count(), 7)
    print('Number of workers = ', num_workers)
    run_start_time = time.time()

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(CUR_DIR, BASELINE_DIR)
    reform_dir = os.path.join(CUR_DIR, REFORM_DIR)

    # Set OG model parameters for a small open economy.
    # This is the same in baseline and reform.
    OG_SPEC = {'start_year': 2021,
               'zeta_D': [0],
               'zeta_K': [1],
               'initial_foreign_debt_ratio': 0,
               # PWBM params.
               'frisch': 0.364,
               'sigma': 1.6
               }

    '''
    ------------------------------------------------------------------------
    Run baseline policy first
    ------------------------------------------------------------------------
    '''
    # tax_func_path = os.path.join(
    #     CUR_DIR, '..', 'ogusa', 'data', 'tax_functions',
    #     'TxFuncEst_baseline_CPS.pkl')  # use cached baseline estimates
    TAX_FUNC_FOLDER = '/home/mghenis/dynamic_micro'
    baseline_tax_func = os.path.join(TAX_FUNC_FOLDER, 'micro_data_baseline.pkl')
    ubi_tax_func = os.path.join(TAX_FUNC_FOLDER, 'micro_data_policy.pkl')


    kwargs = {'output_base': base_dir, 'baseline_dir': base_dir,
              'test': False, 'time_path': False, 'baseline': True,
              'og_spec': OG_SPEC, 'guid': '_example',
              'run_micro': False, 'tax_func_path': baseline_tax_func,
              'data': 'cps', 'client': client, 'num_workers': num_workers}

    start_time = time.time()
    # runner(**kwargs)
    print('run time = ', time.time()-start_time)

    '''
    ------------------------------------------------------------------------
    Run reform policy
    ------------------------------------------------------------------------
    '''
    kwargs = {'output_base': reform_dir, 'baseline_dir': base_dir,
              'test': False, 'time_path': False, 'baseline': False,
              'og_spec': OG_SPEC, 'guid': '_example',
              'run_micro': False, 'tax_func_path': ubi_tax_func,
              'data': 'cps', 'client': client, 'num_workers': num_workers}

    start_time = time.time()
    runner(**kwargs)
    print('run time = ', time.time()-start_time)

    client.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
