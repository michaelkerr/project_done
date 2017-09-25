from bokeh.charts import Bar, output_file, show
import json
import numpy as np
import pandas as pd
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
    # Plot the histogram
    ##################################################

    #
    bins = []
    takt  = []
    data = {}

    current = 0
    for key, value in takt_distro.iteritems():
        while current <= key:
            if current == int(key):
                bins.append(key)
                takt.append(value)
            else:
                bins.append(current)
                takt.append(0)
            current = current + 1
    data = {
        'days': bins,
        'time': takt
        }
    pprint(data)

    '''
    df = pd.DataFrame(data)
    hist = Bar(df, 'days', values='time', title="test chart")

    output_file("project_done.html")
    show(hist)
    '''

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

    #pprint(metric_dict)
    #print issue_list
    #pprint(takt_distro)
    ##################################################
    # TODO Rolling Average (days)
    # NEED TO SORT PROCESSED_DATA BY DELIVERY DATE
    ##################################################
    #pprint(sort_done(processed_data))
    #print moving_average(processed_data)


    ##################################################
    # TODO Running average of # Features in Progress
    ##################################################

    
