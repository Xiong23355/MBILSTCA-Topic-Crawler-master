# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 09:59:56 2023

@author: Xiong
"""
import collections
import start_page
import doc2vec_gensim
import train_doc2vec_model
import Regressor
import time
from selenium import webdriver
import requests,re
import random
from bs4 import BeautifulSoup
class PriorityQueue:
    
    def __init__(self):
        self.queue = []
    
    def clean(self):
        while self.queue:
            del self.queue[0]
            
    def calculate_index(self, item, start, end):
        if len(self.queue) > 0:
            if start < end:
                index = int((start + end) / 2)
                if item[0] == self.queue[index][0]:
                    return index
                elif item[0] > self.queue[index][0]:
                    return self.calculate_index(item, start, index - 1)
                elif item[0] < self.queue[index][0]:
                    return self.calculate_index(item, index + 1, end)
            elif start == end:
                if end != len(self.queue):
                    if item[0] > self.queue[start][0]:
                        return start
                    else:
                        return start + 1
                else:
                    if item[0] < self.queue[end - 1][0]:
                        return end
                    else:
                        return end - 1
            else:
                return start
        else:
            return start
    
    # display the contents of the queue.
    def display_queue(self):
        print("Queue:")
        for item in self.queue:
            print(item)

    # add an item to the queue
    def enqueue(self, item):

        if item not in self.queue:
            index = self.calculate_index(item, 0, len(self.queue))  # calculate index for new element
            self.queue.insert(index, item)  # insert element at index

    # pop an item from the queue
    def dequeue(self):

        # while len(self.queue) <= 0:
        #     continue

        item = self.queue[0]  # item with highest promise
        del self.queue[0]  # remove item from the queue
        return item
    
    # Returns the size of the queue
    def get_size(self):
        return len(self.queue)

    # delete the item from the queue
    def delete(self, index):
        item = self.queue[index]
        del self.queue[index]  # delete item at index
        return item

    # find a url in the queue
    def find(self, url):
        i = -1

        for index in range(len(self.queue)):
            if self.queue[index][1] == url:
                i = index
        return i
            
    def Roulette(self):
        re = random.choices(self.queue, weights = [item[0] for item in self.queue])
        index = self.find(re[-1])
        re = self.delete(index)
        return re
    
    # update the promise of a url if it is found while parsing another page
    def update_queue(self, url, parent_relevance):
        index = self.find(url)
        if index != -1:
            item = self.queue[index]
            del self.queue[index]  # remove item from queue
            item[0] += 0.25 * parent_relevance  # update promise
            self.enqueue(item)  # recompute the index (using the updated promise) and insert item at index

class PastQueue:
    
    def __init__(self):
        self.queue = []      
    
    def enqueue(self, url):
        if url not in self.queue:
            self.queue.append(url)

    # pop an item from the queue
    def dequeue(self,url):

        # while len(self.queue) <= 0:
        #     continue
        index = self.find(self, url)
        item = self.queue[index]  # item with highest promise
        del self.queue[0]  # remove item from the queue
        return item
    
    # Returns the size of the queue
    def get_size(self):
        return len(self.queue)

    # delete the item from the queue
    def delete(self, index):
        item = self.queue[index]
        del self.queue[index]  # delete item at index
        return item

    # find a url in the queue
    def find(self, url):
        i = -1

        for index in range(len(self.queue)):
            if self.queue[index] == url:
                i = index
                break
        return i
    def repeated(self,url):
        tag = False
        for item in self.queue:
            if url == item:
                tag = True
                break
        return tag

# class to remember the order in which URLs (keys) were added            
class Memory: 
    
    def __init__(self):
        self.parsed_urls = collections.OrderedDict()  

    def add_item(self, url, TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child): 
        self.parsed_urls[url] = [TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child, 0, 0] 
    
    def add_score(self,url,RS_score, CS_score):
        url = self.find(self, url)
        if sum(self.parsed_urls[url][-2:-1]) == 0:
            self.parsed_urls[url][-2] = RS_score
            self.parsed_urls[url][-1] = CS_score
        else:
            print('Feature extraction has already been done')
            
    def find(self, url):  # check if item already exists
        return url in self.parsed_urls

    def display(self):  # display URLs in dictionary i.e. the keys
        print(self.parsed_urls.keys())

    def get_values(self):  # return all the keys of the dictionary
        return self.parsed_urls.values()

    def get_item(self, url):  # return the data of parsed url
        return self.parsed_urls[url]
    
    
    def Feature_extraction(self, url, url_back, url_front):
        RS_score,CS_score = 0,0
        c = (1+len(url_front))*len(url_front)/2/10
        for index in range(1,len(url_front)+1):
            history = self.get_item(self, url_front[index-1])
            w = (len(url_front)-index)/len(url_front)
            RS_score += w*(0.6*history[0]+0.4*history[6]*int(history[5]))/c
            CS_score += w*(0.6*int(history[2])+0.4*history[6])/c        
        RS_score,CS_score = 0.6*RS_score,0.6*CS_score
        c = (1+len(url_back))*len(url_back)/2/10
        for index in range(1,len(url_back)+1):
            history = self.get_item(self, url_back[index-1])
            w = (len(url_back)-index)/len(url_back)
            RS_score += 0.4*w*history[-2]/c
            CS_score += 0.4*w*history[-1]/c
        self.add_score(self,url,RS_score, CS_score)
        
# class to keep track of page count i.e. number of pages crawled
class PageCount:
    
    def __init__(self):
        self.page_num = 0

    def increment(self):
        self.page_num += 1

    def get_page_num(self):
        return self.page_num

page_count = PageCount()        
errors = []
# class to remember the crawled data    
class parsed_data:
    
    def __init__(self):
        self.parsed_urls = collections.OrderedDict()  


    def add_item(self, url, content, child_content):  # add an item into the dictionary
        self.parsed_urls[url] = [content, child_content]


    def find(self, url):  # check if item already exists
        return url in self.parsed_urls


    def get_keys(self):  # return all the keys of the dictionary
        return self.parsed_urls.keys()


    def get_item(self, url):  # return the data of parsed url
        return self.parsed_urls[url]
    
class strategy_selection:
    
    def __init__(self):
        self.history = []
       
        
    def add_history(self,stategy):
        self.history.append(stategy)
        
        
    def Initialized_scenario(self,RS_score,CS_score):
        if not self.history[-1] or self.history[-1] == 'reboot':
            if RS_score < 0.5 and CS_score < 0.5:
                mode = 'reboot'
            elif (RS_score-CS_score)>0.2 and RS_score>0.5:
                mode = 'radical'
            elif (CS_score-RS_score)>0.2 and CS_score>0.5:
                mode = 'conservative'
            else:
                mode = random.choices(['conservative','radical'],weights=([RS_score,CS_score]))
            score = RS_score if mode == 'conservative' else CS_score
            self.add_history(mode)
            return mode,score
        else:
            self.Continuous_scenario(RS_score, CS_score)
        
            
    def Continuous_scenario(self,RS_score,CS_score):
        if self.history[-1] and self.history[-1] != 'reboot':
            if self.history[-1] == 'conservative':
                if RS_score < 0.4 and CS_score < 0.4:
                    mode = 'reboot'
                elif (CS_score-RS_score)>0.2 and CS_score>0.4:
                    mode = 'conservative'
                else:
                    mode = 'radical'
                score = RS_score if mode == 'conservative' else CS_score
                self.add_history(mode)
                return mode,score
            elif self.history[-1] == 'radical':
                if RS_score < 0.4 and CS_score < 0.4:
                    mode = 'reboot'
                elif (RS_score-CS_score)>0.2 and RS_score>0.4:
                    mode = 'radical'
                else:
                    mode = 'conservative'
                score = RS_score if mode == 'conservative' else CS_score
                self.add_history(mode)
                return mode,score
            else:
                self.Initialized_scenario(RS_score, CS_score) 
        else:
            self.Initialized_scenario(RS_score, CS_score)
         
            
    def restart(self,data_list,memory_list):
        random_point = random.choices(memory_list.keys(),weights=([item[0] for item in memory_list.values()]))
        random_child = data_list[random_point][1]
        reboot_url = random.choices(random_child[0],weights=(random_child[1]))
        return reboot_url
    
    
    def move(self,data_list,memory_list,strategy,score,child_content):
        #child_content = [child_url,child_pr,child_tr,child_pr+child_tr]
        if strategy == 'reboot':
            self.restart(data_list, memory_list)
        elif strategy == 'conservative':
            if score > 0.8:
                return child_content[-1][0]
            elif score > 0.6:
                return random.choices([i[0] for i in child_content[-10:]],weights=([i[1] for i in child_content[-10:]]))
            else:
                return random.choices([i[0] for i in child_content[-10:]],weights=([i[3] for i in child_content[-10:]]))
        elif strategy == 'radical':
            if score > 0.8:
                return child_content[-1][0]
            elif score > 0.6:
                return random.choices([i[0] for i in child_content[-10:]],weights=([i[2] for i in child_content[-10:]]))
            else:
                return random.choices([i[0] for i in child_content[-10:]],weights=([i[3] for i in child_content[-10:]]))
      
            
def get_input():

    query = input('Enter your query (default: "世界杯"): ').strip()
    num_start_pages = input("Enter the number of start pages (default: 10): ").strip()
    n = input("Enter the number of pages to be returned (at least 10, default: 1000): ").strip()
    page_link_limit = input("Enter the max. no. of links to be fetched from each page (at least 10, default: 25): ").strip()
    corpus = input('Enter your corpus (default: "./resources/世界杯.txt"): ').strip()
    low_relevance = input('Enter your relevance (default: "0.6"): ').strip()
    print('\nObtaining start pages...\n')
    # checking if values are input correctly, otherwise use defaults
    if len(query) == 0:
        query = '世界杯'

    if len(num_start_pages) == 0 or int(num_start_pages) <= 0:
        num_start_pages = 10

    if len(n) == 0 or int(n) < 10:
        n = 1000

    if len(page_link_limit) == 0 or int(page_link_limit) < 10:
        page_link_limit = 25

    if len(corpus) == 0:
        corpus = './resources/世界杯.txt'
        
    if len(low_relevance) == 0:
        low_relevance = 0.6
        
    return query, int(num_start_pages), int(n), int(page_link_limit), corpus, low_relevance

def validate_link(url):
    """ checks if website is crawlable (status code 200) and if its robots.txt allows crawling
    also checks for the MIME type returned in the response header """

    # checking if the url returns a status code 200
    
    global errors
    try:
        r = requests.get(url)
        if r.status_code == 200:
            pass  # website returns status code 200, so check for robots.txt
        else:
            print(url, r.status_code, 'failed')
            errors.append(r.status_code)
            return False
    except:
        print(url, 'request failed')  # request failed
        errors.append('Request Failed')
        return False

    # checking if the website has a robots.txt, and then checking if I am allowed to crawl it
    #domain = urlparse(url).scheme + '://' + urlparse(url).netloc

    #try:
    #    rp = urllib.robotparser.RobotFileParser()
    #    rp.set_url(domain + '/robots.txt')
    #    rp.read()
    #    if not rp.can_fetch('*', url):  # robots.txt mentions that the link should not be parsed
    #        print('robots.txt does not allow to crawl', url)
    #        errors.append('Robots Exclusion')
    #        return False
    #except:
    #    return False

    # checking the MIME type returned in the response header
    try:
        if 'text/html' not in r.headers['Content-Type']:
            errors.append('Invalid MIME type')
            return False
    except:
        errors.append('Request Failed')
        return False
    return True


def get_pr(url):
    base='http://www.521php.com/api/pr/?url='
    header={'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
    A = requests.Session()
    A.headers = header
    resp=A.get(base+url,allow_redirects=True)
    m = re.findall(r"\b\d+\b", resp.text)
    a=sum(int(i) for i in m)/len(m)
    return a/10        


def get_data(response):
    soup = BeautifulSoup(response, 'lxml')
    content = soup.strings
    child_content = []
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        text = link.string
        child_content.append([href,text])

    return content,child_content


def local_search(current_url,data_list,memory_list,model_dm,low_relevance):
    current = data_list.get_item(current_url)
    TR = doc2vec_gensim.caculate_relavance(current[1], model_dm)
    PR = get_pr(current[0])
    RC = True if abs(TR-memory_list.get_item(current_url)[0])>0.4 else False
    TR_parent = memory_list.get_item(current_url)[0]
    m=1
    while memory_list.parsed_urls[-m][0]<low_relevance:
        m += 1
    Distance_mini = m
    Repeated_link = True if current[0] in [item[0] for item in data_list] else False
    TR_child = sum([doc2vec_gensim.caculate_relavance(item[1], model_dm) for item in current[2]])/len(current[2])
    PR_child = sum([get_pr(item[0]) for item in current[2]])/len(current[2])
    return TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child


def get_harvest_rate(links_parsed,memory,low_relevance):
    """ return harvest rate i.e. # relevant links/# total links parsed """

    total_parsed = links_parsed.get_size()
    total_relevant = 0

    for link in links_parsed.queue:
        if memory.get_item(link)[1] >= low_relevance:
            total_relevant += 1

    harvest_rate = total_relevant/total_parsed

    return harvest_rate


def create_log(links_parsed, query, num_crawled, memory_list, harvest_rate, total_time):
    """ creates a log file for the crawler """
    global errors
    
    file = open('crawler_log.txt', 'w')

    file.write('Query: ' + query + '\n')
    file.write('Number of URLs should be Crawled: ' + str(num_crawled) + '\n')

    file.write('\n')
    file.write('Number of URLs Crawled: ' + str(links_parsed.get_size()) + '\n')

    file.write('Total Time Elapsed: ' + str(total_time) + ' sec\n')


    file.write('Harvest Rate: ' + str(harvest_rate) + '\n')

    unique_errors = list(set(errors))
    file.write('\nErrors: \n')
    file.write('-------\n')
    for e in unique_errors:
        file.write(str(e) + ': ' + str(errors.count(e)) + '\n')
    file.write('\nURLs Crawled:\n')
    file.write('-------------\n\n')

    counter = 0
    for url in links_parsed.queue:
        file.write(str(counter+1) + '. \n')
        file.write('URL:' + url + '\n')
        TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child, RS_score, CS_score = memory_list.get_item(url)

        file.write('Topic Relevance:' + str(TR) + '\n')
        file.write('Page Authority Value:' + str(PR) + '\n')
        file.write('Relevance Change: ' + str(RC) + '\n')
        file.write('Parent Pages’ Average Topic Relevancee: ' + str(TR_parent) + '\n')
        file.write('Minimum Distance from Topic Related Parent Page: ' + str(Distance_mini) + '\n')
        file.write('Repeated Link Existence:' + str(Repeated_link) + '\n')
        file.write('Subpages’ Topic Relevance Predictive Value: ' + str(TR_child) + '\n')
        file.write('Subpages’ Authority Value: ' + str(PR_child) + '\n')
        file.write('Radical Strategy Acceptance Calculation Score: ' + str(RS_score) + '\n')
        file.write('Conservative Strategy Acceptance Calculation Score:' + str(CS_score) + '\n')       
        
        file.write('\n\n')
        counter += 1
        
def main():
    '''INITIALIZATION'''
    #Initialize basic parameter from input
    query, num_start_pages, n, page_link_limit, corpus, low_relevance = get_input()
    start_time = time.time()
    
    #Initialize headless webdriver
    profile=webdriver.FirefoxOptions()
    profile.add_argument('-headless')
    driver=webdriver.Firefox(options=profile)
    driver.set_page_load_timeout(10)
    
    #Initialize sematic module
    model_dm = train_doc2vec_model(corpus)
    
    #Initialize start queue
    start_pages = start_page.main(query)
    links_to_parse = PriorityQueue()
    links_parsed = PastQueue()
    data = parsed_data()
    memory = Memory()
    
    for item in start_pages:
        PR_child = get_pr(item[0])
        TR_child = doc2vec_gensim.caculate_relavance(item[1], model_dm)
        links_to_parse.enqueue([PR_child+TR_child,item[0]])
        
    '''STAGE 1: Rand choice stage'''    
    while len(links_parsed.queue) < 0.1*n:
        current_url = links_to_parse.Roulette()
        if validate_link(current_url) and not links_parsed.repeated(current_url):
            try:
                driver.get(current_url)
                res=driver.page_source
                content,child_content = get_data(res)
                links_parsed.enqueue(current_url)
                data.add_item(current_url, content, child_content)
                TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child = local_search(
                    current_url,data.parsed_urls, memory.parsed_urls, model_dm, low_relevance)
                memory.add_item(current_url, TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child)
            except:
                continue
        else:
            continue
        if len(links_parsed.queue)%10==0 and len(links_parsed.queue)>10:
            cal_list = links_parsed.queue[-20:-11]
            for item in cal_list:
                index = links_parsed.find(item)
                url_back = links_parsed[index-10:index-1]
                url_front = links_parsed[index+1:index+10]
                memory.Feature_extraction(item, url_back, url_front)
        links_to_parse.clean()
        for item in child_content:
            PR_child = get_pr(item[0])
            TR_child = doc2vec_gensim.caculate_relavance(item[1], model_dm)
            links_to_parse.enqueue([PR_child+TR_child,item[0]])
    
    '''One fit'''
    data = [item[1:] for item in memory.get_values() if sum(item[-2:-1])]
    Regressor.ones_fit(data)
    model_file = 'model.dat'
    
    '''STAGE 2: With Network'''
    batch = 0
    while len(links_parsed.queue) < n:
        TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child = local_search(
            current_url,data.parsed_urls, memory.parsed_urls, model_dm, low_relevance)
        
        RS_score,CS_score = Regressor.acceptance_caculate(
            model_file, [TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child])
        
        mode,score = strategy_selection.Continuous_scenario(RS_score, CS_score)
        current_url = strategy_selection.move(data.parsed_urls, memory.parsed_urls, mode, score, child_content)
        if validate_link(current_url) and not links_parsed.repeated(current_url):
            try:
                driver.get(current_url)
                res=driver.page_source
                content,child_content = get_data(res)
                links_parsed.enqueue(current_url)
                data.add_item(current_url, content, child_content)
                
                TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child = local_search(
                    current_url,data.parsed_urls, memory.parsed_urls, model_dm, low_relevance)
                memory.add_item(current_url, TR, PR, RC, TR_parent, Distance_mini, Repeated_link, TR_child, PR_child)
            except:
                continue
        else:
            continue
        if len(links_parsed.queue)%10==0 and len(links_parsed.queue)>10:
            cal_list = links_parsed.queue[-20:-11]
            for item in cal_list:
                index = links_parsed.find(item)
                url_back = links_parsed[index-10:index-1]
                url_front = links_parsed[index+1:index+10]
                memory.Feature_extraction(item, url_back, url_front)
        if batch//50:
            try:
                data = [memory.get_item(url) for url in links_parsed[-50:] if sum(memory.get_item(url)[-2:])]
                Regressor.part_fit(model_file, data)
                batch = 0
            except:
                continue
        else:
            batch += 1
    end_time = time.time()
    
    '''Program Exit and Create Log'''
    total_time = end_time - start_time
    harvest_rate = get_harvest_rate(links_parsed, memory, low_relevance)
    driver.quit()
    create_log(links_parsed, query, n, memory, harvest_rate, total_time)
        
if __name__ == "__main__":
    main()     
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        