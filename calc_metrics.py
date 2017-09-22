import json
import numpy as np
from pprint import pprint

processed_file = "processed.json"

### MAIN ###
if __name__ == '__main__':
    #GET THE FEATURE DATA
    try:
        with open(processed_file, 'r') as infile:
            processed_data = json.load(infile)
    except Exception as e:
        print e
        exit()

    takt_distro = {}
    task_list = []
    duration_list = []

    for epic in processed_data:
        ##################################################
        # Get the duration of the epic
        ##################################################
        duration_list.append(sum(epic))

        ##################################################
        # Update the distro of "takt" times
        ##################################################
        for entry in epic:
            task_list.append(entry)
            if entry in takt_distro.keys():
                takt_distro[entry] = takt_distro[entry] + 1
            else:
                takt_distro[entry] = 1

    ##################################################
    # Epic Macro Metrics
    ##################################################
    metric_dict = {}

    #Average (days/item)
    metric_dict['epic_average'] = np.average(duration_list)
    metric_dict['item_average'] = np.average(task_list)

    # Median
    metric_dict['epic_median'] = np.median(duration_list)
    metric_dict['task_median'] = np.median(task_list)

    # Std Deviation
    metric_dict['epic_stddev'] = np.std(duration_list)
    metric_dict['task_stddev'] = np.std(task_list)

    pprint(metric_dict)

    ##################################################
    # TODO Rolling Average (days)
    # NEED TO SORT PROCESSED_DATA BY DELIVERY DATE
    ##################################################
    #pprint(sort_done(processed_data))
    #print moving_average(processed_data)


    ##################################################
    # TODO Running average of # Features in Progress
    ##################################################
