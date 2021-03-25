import re
import csv
import logging
import numpy as np
from pathlib import Path
from typing import Union
from collections import defaultdict

from scipy.io import savemat

from utils.file_io import glob_file
from utils._version import __version__

logger = logging.getLogger(__name__)

# [TODO]
# Find a better way handle the log parsing and writing
# Current version is hard to maintain.
def summarize_one_setup(log_dir: Union[str, Path], color: int = 0) -> None:
    """Summarize the evaluation results for an experimental setup. Store
    raw data into .csv file and summarize the avg., stdev., max., and 
    min. into .log file.
    
    Parameters
    ----------
    log_dir : `Union[str, Path]`
        The directory of the evaluation log files.
    color : `int`, optional
        1 for dataset with color, 0 otherwise. Defaults to 0.
    """
    log_files = glob_file(log_dir, '**/*.log', fullpath=True)

    chosen_metrics_text = {
        'encT':        'Encoding time (s)           : ',
        'decT':        'Decoding time (s)           : ',
        'bpp':         'bpp (bits per point)        : ',
        'acd12_p2pt':  'Asym. Chamfer dist. (1->2) p2pt: ',
        'acd21_p2pt':  'Asym. Chamfer dist. (2->1) p2pt: ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR (dB)               p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'acd12_p2pl':  'Asym. Chamfer dist. (1->2) p2pl: ',
        'acd21_p2pl':  'Asym. Chamfer dist. (2->1) p2pl: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR (dB)               p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
    }
    if color == 1:
        chosen_metrics_text.update({
            'y_cpsnr':     'Y-CPSNR (dB)                   : ',
            'u_cpsnr':     'U-CPSNR (dB)                   : ',
            'v_cpsnr':     'V-CPSNR (dB)                   : ',
            'hybrid':      'Hybrid geo-color               : ',
        })

    # escape special characters
    chosen_metrics = {
        key: re.escape(pattern) for key, pattern in chosen_metrics_text.items()
    }

    found_val = {key: [] for key in chosen_metrics.keys()}

    # Parsing data from each log file
    for log in log_files:
        with open(log, 'r') as f:
            for metric, pattern in chosen_metrics.items():
                isfound = False
                for line in f:
                    m = re.search(f'(?<={pattern}).*', line)
                    if m:
                        if m.group() == 'inf':
                            found_val[metric].append(np.inf)
                        elif m.group() == 'nan':
                            found_val[metric].append(np.nan)
                        else:
                            found_val[metric].append(float(m.group()))
                        isfound = True
                        break
                if not isfound:
                    # Not found that metric result
                    found_val[metric].append(None)

    # Save raw data (with None and np.inf) into .csv file
    alg_name = Path(log_dir).parents[2].stem
    ds_name = Path(log_dir).parents[1].stem
    rate = Path(log_dir).parents[0].stem

    summary_csv = (
        Path(log_dir).parent
        .joinpath(f'{alg_name}_{ds_name}_{rate}_summary.csv')
    )
    
    with open(summary_csv, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        # write header
        header = [metric_name for metric_name in chosen_metrics.keys()]
        csvwriter.writerow(header)
        # write results
        rows = zip(*[list_ for list_ in found_val.values()])
        for row in rows:
            csvwriter.writerow(row)

    # Summarize the results and save them into the .log file
    summary_log = summary_csv.with_suffix('.log')
    
    with open(summary_log, 'w') as f:
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"Summary of the log directory: {log_dir}"
            "\n",
        ]
        
        statistics = {
            'Avg.': np.nanmean,
            'Stdev.': np.nanstd,
            'Max.': np.nanmax,
            'Min.': np.nanmin,
        }
        
        for stat, op in statistics.items():
            tmp_lines = [f"***** {stat} *****"]
            for key, pattern in chosen_metrics_text.items():
                tmp_nparray = np.array(found_val[key], dtype=np.float)
                tmp_lines.append(f"{stat} {pattern}{op(tmp_nparray)}")
            
            tmp_lines.insert(1, "========== Time & Binary Size ==========")
            tmp_lines.insert(5, "\n")
            tmp_lines.insert(6, "========== Objective Quality ===========")
            tmp_lines.insert(12, "----------------------------------------")
            if color == 1:
                tmp_lines.insert(18, "----------------------------------------")
                tmp_lines.insert(22, "\n")
                tmp_lines.insert(23, "============== QoE Metric ==============")
                tmp_lines.insert(25, "\n")
            
            tmp_lines.append("\n")
            lines += tmp_lines

        f.writelines('\n'.join(lines))

    return

def summarize_all_to_csv(exp_dir):
    # [TODO]
    # Unfinished
    summary_log_files = sorted(
        glob_file(exp_dir, '*_summary.log', fullpath=True)
    )
    csvfile = Path(exp_dir).joinpath('summary.csv')
    
    chosen_metrics = [
        'encT',
        'decT',
        'bpp',
        'acd12_p2pt',
        'acd21_p2pt',
        'cd_p2pt',
        'cdpsnr_p2pt',
        'h_p2pt',
        'acd12_p2pl',
        'acd21_p2pl',
        'cd_p2pl',
        'cdpsnr_p2pl',
        'h_p2pl',
        'y_cpsnr',
        'u_cpsnr',
        'v_cpsnr',
        'hybrid'
    ]
    
    patterns = {
        'encT':        'Encoding time (s)           : ',
        'decT':        'Decoding time (s)           : ',
        'bpp':         'bpp (bits per point)        : ',
        'acd12_p2pt':  'Asym. Chamfer dist. (1->2) p2pt: ',
        'acd21_p2pt':  'Asym. Chamfer dist. (2->1) p2pt: ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR (dB)               p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'acd12_p2pl':  'Asym. Chamfer dist. (1->2) p2pl: ',
        'acd21_p2pl':  'Asym. Chamfer dist. (2->1) p2pl: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR (dB)               p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
        'y_cpsnr':     'Y-CPSNR (dB)                   : ',
        'u_cpsnr':     'U-CPSNR (dB)                   : ',
        'v_cpsnr':     'V-CPSNR (dB)                   : ',
        'hybrid':      'Hybrid geo-color               : ',
    }
    # escape special characters
    for key in patterns:
        patterns[key] = re.escape(patterns[key])

    with open(csvfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        header = [
            'PCC_algs',
            'Datasets',
            'Rate',
            'Avg. Encoding Time',
            'Avg. Decoding Time',
            'Avg. bpp',
            'Avg. Asym. Chamfer Distance 1->2 (p2pt)',
            'Avg. Asym. Chamfer Distance 2->1 (p2pt)',
            'Avg. Chamfer Distance (p2pt)',
            'Avg. CD-PSNR (p2pt)',
            'Avg. Hausdorff Distance (p2pt)',
            'Avg. Asym. Chamfer Distance 1->2 (p2pl)',
            'Avg. Asym. Chamfer Distance 2->1 (p2pl)',
            'Avg. Chamfer Distance (p2pl)',
            'Avg. CD-PSNR (p2pl)',
            'Avg. Hausdorff Distance (p2pl)',
            'Avg. Y-CPSNR',
            'Avg. U-CPSNR',
            'Avg. V-CPSNR',
            'Avg. Hybrid Geo-Color',
            'Stdev. Encoding Time',
            'Stdev. Decoding Time',
            'Stdev. bpp',
            'Stdev. Asym. Chamfer Distance 1->2 (p2pt)',
            'Stdev. Asym. Chamfer Distance 2->1 (p2pt)',
            'Stdev. Chamfer Distance (p2pt)',
            'Stdev. CD-PSNR (p2pt)',
            'Stdev. Hausdorff Distance (p2pt)',
            'Stdev. Asym. Chamfer Distance 1->2 (p2pl)',
            'Stdev. Asym. Chamfer Distance 2->1 (p2pl)',
            'Stdev. Chamfer Distance (p2pl)',
            'Stdev. CD-PSNR (p2pl)',
            'Stdev. Hausdorff Distance (p2pl)',
            'Stdev. Y-CPSNR',
            'Stdev. U-CPSNR',
            'Stdev. V-CPSNR',
            'Stdev. Hybrid Geo-Color',
            'Max. Encoding Time',
            'Max. Decoding Time',
            'Max. bpp',
            'Max. Asym. Chamfer Distance 1->2 (p2pt)',
            'Max. Asym. Chamfer Distance 2->1 (p2pt)',
            'Max. Chamfer Distance (p2pt)',
            'Max. CD-PSNR (p2pt)',
            'Max. Hausdorff Distance (p2pt)',
            'Max. Asym. Chamfer Distance 1->2 (p2pl)',
            'Max. Asym. Chamfer Distance 2->1 (p2pl)',
            'Max. Chamfer Distance (p2pl)',
            'Max. CD-PSNR (p2pl)',
            'Max. Hausdorff Distance (p2pl)',
            'Max. Y-CPSNR',
            'Max. U-CPSNR',
            'Max. V-CPSNR',
            'Max. Hybrid Geo-Color',
            'Min. Encoding Time',
            'Min. Decoding Time',
            'Min. bpp',
            'Min. Asym. Chamfer Distance 1->2 (p2pt)',
            'Min. Asym. Chamfer Distance 2->1 (p2pt)',
            'Min. Chamfer Distance (p2pt)',
            'Min. CD-PSNR (p2pt)',
            'Min. Hausdorff Distance (p2pt)',
            'Min. Asym. Chamfer Distance 1->2 (p2pl)',
            'Min. Asym. Chamfer Distance 2->1 (p2pl)',
            'Min. Chamfer Distance (p2pl)',
            'Min. CD-PSNR (p2pl)',
            'Min. Hausdorff Distance (p2pl)',
            'Min. Y-CPSNR',
            'Min. U-CPSNR',
            'Min. V-CPSNR',
            'Min. Hybrid Geo-Color',
        ]
        csvwriter.writerow(header)
        for log in summary_log_files:
            alg_name = Path(log).parents[2].stem
            ds_name = Path(log).parents[1].stem
            rate = Path(log).parents[0].stem
            
            with open(log, 'r') as f:
                row = [alg_name, ds_name, rate]
                for line in f:
                    for metric in chosen_metrics:
                        m = re.search(f'(?<={patterns[metric]}).*', line)
                        if m:
                            row.append(m.group())
            csvwriter.writerow(row)

def summarize_all_to_mat(exp_dir):
    summary_log_files = glob_file(exp_dir, '*_summary.log', fullpath=True)
    ret = nested_dict()
    matfile = Path(exp_dir).joinpath('summary.mat')
    
    chosen_metrics = [
        'encT',
        'decT',
        'bpp',
        'cd_p2pt',
        'cdpsnr_p2pt',
        'h_p2pt',
        'cd_p2pl',
        'cdpsnr_p2pl',
        'h_p2pl',
        'y_cpsnr',
        'u_cpsnr',
        'v_cpsnr',
        'hybrid'
    ]
    
    patterns = {
        'encT':        'Encoding time (s)           : ',
        'decT':        'Decoding time (s)           : ',
        'bpp':         'bpp (bits per point)        : ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR (dB)               p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR (dB)               p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
        'y_cpsnr':     'Y-CPSNR (dB)                   : ',
        'u_cpsnr':     'U-CPSNR (dB)                   : ',
        'v_cpsnr':     'V-CPSNR (dB)                   : ',
        'hybrid':      'Hybrid geo-color               : ',
    }
    # escape special characters
    for key in patterns:
        patterns[key] = re.escape(patterns[key])

    for log in summary_log_files:
        alg_name = Path(log).parents[2].stem
        ds_name = Path(log).parents[1].stem
        rate = Path(log).parents[0].stem

        with open(log, 'r') as f:
            for line in f:
                for metric in chosen_metrics:
                    m = re.search(f'(?<={patterns[metric]}).*', line)
                    if m:
                        if m.group() == 'nan':
                            break
                        else:
                            # search for ["avg", "stdev", "max", and "min"]
                            statistic = re.search(f'.*(?=. {patterns[metric]})', line).group()
                            val = float(m.group())
                            # ret[alg_name][ds_name][rate][metric][statistic] = val
                            ret[statistic][metric][ds_name][alg_name][rate] = val
    savemat(matfile, ret)

def nested_dict():
    # https://stackoverflow.com/a/652226
    return defaultdict(nested_dict)