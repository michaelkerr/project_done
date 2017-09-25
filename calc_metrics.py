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
    issue_list = []
    duration_list = []
    average_takt_list = []

    for epic in processed_data:
        ##################################################
        # Get the duration of the epic
        ##################################################
        duration_list.append(sum(epic))
        average_takt_list.append(float(sum(epic))/float(len(epic)))

        ##################################################
        # Update the distro of "takt" times
        ##################################################
        for entry in epic:
            issue_list.append(entry)
            if entry in takt_distro.keys():
                takt_distro[entry] = takt_distro[entry] + 1
            else:
                takt_distro[entry] = 1

    ##################################################
    # Epic Macro Metrics
    ##################################################
    metric_dict = {}

    #Average (days/item)
    metric_dict['epic_avg'] = np.average(duration_list)
    metric_dict['takt_avg'] = np.average(issue_list)
    metric_dict['takt_avg2'] = np.average(average_takt_list)

    # Median
    metric_dict['epic_median'] = np.median(duration_list)
    metric_dict['takt_median'] = np.median(issue_list)

    # Std Deviation
    metric_dict['epic_stddev'] = np.std(duration_list)
    metric_dict['takt_stddev'] = np.std(issue_list)

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
