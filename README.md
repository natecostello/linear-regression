This repo is for messing with linear regression.  Not that interesting.

google colab thingy here:
https://colab.research.google.com/drive/1fgjDQ6hCScbsCWsRSOZsg8OWmQuqUCbH#scrollTo=trpdAcsj9ZhR


this is all based on cribbing this:
https://towardsdatascience.com/predicting-house-prices-with-linear-regression-machine-learning-from-scratch-part-ii-47a0238aeac1

TODO:
* migrate colab to gist
* migrate code to script
* incorporate new sold data into existing data without duplicates (and avoid over scrapping - maybe remove pagination)

Note:  When exporting a sitemap, regex patterns have extra '\' inserted such that the regex pattern isn't correct when viewed in the JSON.  However, upon import, these extra '\' are removed, so don't attempt to fix regex in the JSON file.

Note: "zillow-sold.json" includes modifications recommended by webscraper.io to the sold-[town]-sitemap.json files.