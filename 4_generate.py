# -*- coding: utf-8 -*-
from datetime import datetime
import json
import numpy as np
from pprint import pprint

#from bokeh.charts import Bar, output_file, show
import pandas as pd

#in_file = "processed.json"
in_file = "data_3.json"
out_file = "data_4.json"
metric_file = "data_metrics.json"
trials = 50000
num_items = 4
averages = []
probabilities = []

### MAIN ###
if __name__ == '__main__':
    #GET THE DATA
    try:
        with open(in_file, 'r') as infile:
            data = json.load(infile)
    except Exception as e:
        print e
        exit()

    for trial in range(trials):
        for item in range(num_items):
            # Select an item from the sample data
            draw = np.random.choice(data['days'], p=data['p(t)'])
            averages.append(np.average(draw))

    ##################################################
    # Method 1
    # Monte Carlo Selecxtion with Replacement
    ##################################################
    for day in averages:
        prob = float(day) / float(len(averages))
        probabilities.append(prob)

    meta_dict = {}
    meta_dict['work_items'] = num_items
    meta_dict['meta_median'] = np.median(averages)
    meta_average = np.average(averages)
    meta_dict['meta_average'] = meta_average
    meta_dict['meta_std'] = np.std(averages)
    meta_dict['meta_85th'] = np.percentile(averages, 85)
    meta_dict['meta_95th'] = np.percentile(averages, 95)

    i = 0
    max = 0
    for entry in data['p(t)']:
        if entry > max:
            max = i
        i = i + 1

    meta_dict['meta_mode'] = data['days'][max]

    pprint(meta_dict)
    # Write to file
    with open(metric_file, 'w') as outfile:
        json.dump(meta_dict, outfile)

    print 'Average Story Takt Time: %s Days' % (meta_average)
    print 'Estimated Epic/Feature Delivery Time: %s Days' % (meta_average * num_items)

    '''
    df = pd.DataFrame(data)
    hist = Bar(df, 'days', values='time', title="test chart")

    output_file("project_done.html")
    show(hist)
    '''

    ##################################################
    # TODO Z Curve
    ##################################################
    #np.percentile(probabilities, 85)

    # Write to file
    with open(out_file, 'w') as outfile:
        json.dump(data, outfile)



'''
Input format:
{
	"p(t)": [0.12396694214876033, 0.256198347107438, 0.1115702479338843, ...0.008264462809917356],
	"days": [0, 1, 2, ...131],
	"time": [30, 62, 27, ...2]
}

Output Format:
S/A For now......

'''
