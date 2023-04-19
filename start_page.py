# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 10:26:42 2023

@author: Xiong
"""

from bs4 import BeautifulSoup
from urllib.parse import quote
from url_normalize import url_normalize
import string
from selenium import webdriver

errors = []
num_start_pages = 10
def pre_validate_link(url):
    """ only checks if the link contains excluded words and/or types """

    excluded_words = ['download', 'upload', 'javascript', 'cgi', 'file']
    excluded_types = [".asx", ".avi", ".bmp", ".css", ".doc", ".docx",
                      ".flv", ".gif", ".jpeg", ".jpg", ".mid", ".mov",
                      ".mp3", ".ogg", ".pdf", ".png", ".ppt", ".ra",
                      ".ram", ".rm", ".swf", ".txt ", ".wav", ".wma",
                      ".wmv", ".xml", ".zip", ".m4a", ".m4v", ".mov",
                      ".mp4", ".m4b", ".cgi", ".svg", ".ogv", ".dmg", ".tar", ".gz"]

    for ex_word in excluded_words:
        if ex_word in url.lower():
            errors.append('Link contains excluded terms')
            return False

    for ex_type in excluded_types:
        if ex_type in url.lower():
            errors.append('Link contains excluded type')
            return False
    return True

def get_href(res):
    initial_links = []
    count = 0
    soup = BeautifulSoup(res, 'lxml')
    links = soup.find_all('h3')
    for link in links:
        href = link.a.get('href')
        anchor_content = link.a.string
        #if "url?q=" in href and "webcache" not in href:
           # l_new = href.split("?q=")[1].split("&sa=U")[0]
        if pre_validate_link(url_normalize(href)) and 'http' in url_normalize(href):  # pre-validating link before enqueue, but validate upon dequeue
            count += 1
            if count <= num_start_pages:
                initial_links.append([url_normalize(href),anchor_content])
            else:
                break
    return initial_links

def main(query):
    profile=webdriver.FirefoxOptions()
    profile.add_argument('-headless') #设置无头模式
    driver=webdriver.Firefox(options=profile)
    driver.set_page_load_timeout(40)
    domain = 'https://www.baidu.com'
    url = domain + '/s?wd=' + query +'&ie=utf-8'
    s = quote(url, safe=string.printable)
    driver.get(s)
    res=driver.page_source
    initial_links = get_href(res)
    driver.quit()
    return initial_links