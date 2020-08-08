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

    # Create UBI reform
    IIT_REFORM = {
        'FICA_mc_trt': {2021: 0.039}  # Baseline plus 1pp.
    }

    # Directories to save data
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(CUR_DIR, BASELINE_DIR)
    reform_dir = os.path.join(CUR_DIR, REFORM_DIR)

    # Set OG model parameters for a small open economy.
    # This is the same in baseline and reform.
    OG_SPEC = {'start_year': 2021,
               'zeta_D': [0],
               'zeta_K': [1],
               'initial_foreign_debt_ratio': 0
               }

    '''
    ------------------------------------------------------------------------
    Run baseline policy first
    ------------------------------------------------------------------------
    '''
    # tax_func_path = os.path.join(
    #     CUR_DIR, '..', 'ogusa', 'data', 'tax_functions',
    #     'TxFuncEst_baseline_CPS.pkl')  # use cached baseline estimates
    kwargs = {'output_base': base_dir, 'baseline_dir': base_dir,
              'test': False, 'time_path': True, 'baseline': True,
              'og_spec': OG_SPEC, 'guid': '_example',
              'run_micro': False, # 'tax_func_path': tax_func_path,
              'data': 'cps', 'client': client,
              'num_workers': num_workers}

    start_time = time.time()
    runner(**kwargs)
    print('run time = ', time.time()-start_time)

    '''
    ------------------------------------------------------------------------
    Run reform policy
    ------------------------------------------------------------------------
    '''
    kwargs = {'output_base': reform_dir, 'baseline_dir': base_dir,
              'test': False, 'time_path': True, 'baseline': False,
              'og_spec': OG_SPEC, 'guid': '_example',
              'iit_reform': IIT_REFORM, 'run_micro': True, 'data': 'cps',
              'client': client, 'num_workers': num_workers}

    start_time = time.time()
    runner(**kwargs)
    print('run time = ', time.time()-start_time)

    # return ans - the percentage changes in macro aggregates and prices
    # due to policy changes from the baseline to the reform
    base_tpi = safe_read_pickle(
        os.path.join(base_dir, 'TPI', 'TPI_vars.pkl'))
    base_params = safe_read_pickle(
        os.path.join(base_dir, 'model_params.pkl'))
    reform_tpi = safe_read_pickle(
        os.path.join(reform_dir, 'TPI', 'TPI_vars.pkl'))
    reform_params = safe_read_pickle(
        os.path.join(reform_dir, 'model_params.pkl'))
    ans = ot.macro_table(
        base_tpi, base_params, reform_tpi=reform_tpi,
        reform_params=reform_params,
        var_list=['Y', 'C', 'K', 'L', 'r', 'w'], output_type='pct_diff',
        num_years=10, start_year=OG_SPEC['start_year'])

    # create plots of output
    op.plot_all(base_dir, reform_dir,
                os.path.join(CUR_DIR, 'run_example_plots'))

    print("total time was ", (time.time() - run_start_time))
    print('Percentage changes in aggregates:', ans)
    # save percentage change output to csv file
    ans.to_csv('ogusa_example_output.csv')
    client.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
