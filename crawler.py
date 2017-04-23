import queue
import multiprocessing
import sys
import traceback

from threading import Thread
from urllib import parse
from urllib.parse import urlparse
from urllib.request import urlopen
from html.parser import HTMLParser
from collections import defaultdict

class CustomParser(HTMLParser): #inherit from HTMLParser
    
    #Could have also used BeautifulSoup to find objects with the specified tags
    def __init__(self, accepted_tag_attribs = ['a href']):
        super(CustomParser, self).__init__()
        if not accepted_tag_attribs:
            print('No assets will be saved, just links')
        self.accepted = accepted_tag_attribs
        self.url = None
        self.domain = None
        self.assets = defaultdict(set)
        self.urls = set()
        
    def reset_data(self):
        self.assets = defaultdict(set)
        self.urls = set()
        
    def handle_starttag(self, tag, attrs):
        for (k, v) in attrs:
            if tag + ' ' + k in self.accepted:
                full_url = parse.urljoin(self.url,v)
                self.assets[self.url].add(full_url)
                if tag == 'a' and k =='href':
                    #pass if anchor
                    if v.startswith('#'):
                        continue
                    #check if relative link
                    if urlparse(v).netloc and self.domain in urlparse(v).hostname :
                        self.urls.add(v.rstrip('/'))
                    elif not urlparse(v).netloc \
                            and urlparse(full_url).netloc \
                            and self.domain in str(urlparse(full_url).hostname):
                        self.urls.add(full_url.rstrip('/'))
                    
class Crawler(object):
    
    def __init__(self,accepted_tag_attrib_pairs, root):
        s = urlopen(root)
        self.crawl_queue = queue.Queue()
        self.crawl_queue.put(root)
        self.assets = defaultdict(set)
        self.accepted = accepted_tag_attrib_pairs
        self.domain =  urlparse(root).hostname
        self.visited = set()
        self.not_valid_sites = set()

    # Create threads equal to cpu count
    def start(self, write_files = True):
        self.create_threads()

        #wait for all threads to consume the queue
        self.crawl_queue.join()
        
        self.visited = self.visited.difference(self.not_valid_sites)
        visited_sorted = sorted(self.visited)
        if write_files:
            assets_file = open('assets.out','w',encoding = 'utf-8', errors = 'replace')
            for page, assets in self.assets.items():
                assets_file.write('Assets on '+str(page)+ ' \n')
                for asset in assets:
                    assets_file.write('\t' + str(asset) + '\n')
                assets_file.write('\n')
            assets_file.close()

            sitemap = open('sitemap.out','w',encoding = 'utf-8', errors = 'replace')
            for site in visited_sorted:
                sitemap.write(str(site) + '\n')
            sitemap.close()
        print 'Finished!'

    def create_threads(self):
        for i in range(multiprocessing.cpu_count()):
            t = Thread(target = self.crawl, args = (self.accepted,))
            t.daemon = True
            t.start()
        
    
    def crawl(self, accepted_tag):
        parser = CustomParser(accepted_tag)
        parser.domain = self.domain
        while True:
            try:
                item = self.crawl_queue.get()
                parser.url = item
                response = urlopen(item)
                content = response.read().decode('utf-8')
                response.close()
                parser.feed(content)
                assets, urls = parser.assets, parser.urls

                for page, asset in assets.items():
                    self.assets[page].update(asset)
                
                lst = [self.crawl_queue.put(next_url) for next_url in urls\
                   if next_url not in self.visited]

                self.visited.update(urls)
                self.crawl_queue.task_done()
                parser.reset_data()
                print(len(self.crawl_queue.queue))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log_file = open('log.out','a')
                log_file.write(str(exc_value) + ' When crawling :' + str(item) + '\n')
                log_file.close()
                self.not_valid_sites.add(item)
                self.crawl_queue.task_done()
