A Memory Based Iterative Local Search Topic Crawler Algo-rithm for Tunnel Crossing
==================================================================================

Files:
------
spidey.py: Main program entry

resources: Corpus and related documents
readme.txt: This file
explain.txt: Documentation for the important Classes and functions, along with assumptions, known bugs/missing features and using model
requirements.txt: Third party dependency libraries
geckodriver.exe: Necessary drivers for running selenium

Program Input:
--------------
The program will ask for the following inputs:
1. The query: The search string (default: '世界杯')
2. The number of start pages: The number of start pages to be retrieved from the initial Baidu search (default: 10)
3. The number of pages to be returned: The max. number of pages to be crawled (minimum: 10, default: 1000)
4. The corpus file. file of corpus to train semantic analysis model (default: './resources/世界杯.txt')
5. The lowest relevance: Threshold for determining whether a webpage is topic-related


Expected Output:
----------------
crawler_log file with crawl parameters, details about the crawled links, harvest rate, time elapsed and errors encountered 