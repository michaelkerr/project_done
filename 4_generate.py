# -*- coding: utf-8 -*-
import json
import numpy as np
from pprint import pprint

#from bokeh.charts import Bar, output_file, show
import pandas as pd

in_file = "in_file.json"
trials = 10000
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
    #meta_mode['meta_mode'] =
    pprint(meta_dict)
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
