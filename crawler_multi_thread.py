import queue
import multiprocessing
import sys
import traceback
import getopt

from threading import Thread
from urllib import parse
from urllib.parse import urlparse
from urllib.request import urlopen
from html.parser import HTMLParser
from collections import defaultdict

class CustomParser(HTMLParser): #inherit from HTMLParser
    
    #Could have also used BeautifulSoup to find objects with the specified tags
    def __init__(self, accepted_tag_attribs):
        super(CustomParser, self).__init__()
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
                    #check if relative link 
                    if urlparse(v).netloc and self.domain in urlparse(v).hostname :
                        self.urls.add(v)
                    elif not urlparse(v).netloc \
                            and urlparse(full_url).netloc \
                            and self.domain in str(urlparse(full_url).hostname):
                        self.urls.add(full_url)
                    
class Crawler(object):
    
    def __init__(self,accepted_tag_attrib_pairs, root):
        s = urlopen(root)
        self.crawl_queue = queue.Queue()
        self.crawl_queue.put(root)
        self.assets = defaultdict(set)
        self.accepted = accepted_tag_attrib_pairs
        self.domain =  urlparse(root).hostname
        self.visited = set()


    def start(self, write_files = True):
        self.create_threads()
        self.crawl_queue.join()

        if write_files:
            assets_file = open('assets.out','w',encoding = 'utf-8', errors = 'replace')
            for page, assets in self.assets.items():
                assets_file.write('Assets on '+str(page)+ ' \n')
                for asset in assets:
                    assets_file.write('\t' + str(asset) + '\n')
                assets_file.write('\n')
            assets_file.close()

            sitemap = open('sitemap.out','w',encoding = 'utf-8', errors = 'replace')
            for site in self.visited:
                sitemap.write(str(site) + '\n')
            sitemap.close()
        return 'Finished!'

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
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                log_file = open('log.out','a')
                log_file.write(str(exc_value) + ' When crawling :' + str(item) + '\n')
                log_file.close()
                self.crawl_queue.task_done()
                
if __name__ == '__main__':

    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'w:v:p', ['website=','valid_assets=', 'profile='])
        print (options)
        if not options:
            raise getopt.GetoptError('Arguments not specified')
    except getopt.GetoptError as err:
        print(err)
        print('\n')
        print('Example usage : python crawler_multi_thread.py'+\
              ' --website=http://github.com --valid_assets="a href" -p \n')
        print('Note : -p is used to profile the code\n')
        sys.exit(2)
    
    import sys
    import cProfile

    website = ''
    valid_asset_list = []
    profile = False
    for opts, arg in options:
        if opts in ('-w','--website'):
            website = arg
        if opts in ('-v','--valid_assets'):
            valid_asset_list = arg.split(',')
        if opts in ('-p','--profile'):
            profile = True
    crawler = Crawler((valid_asset_list),website)

    if profile:
        cProfile.run('crawler.start()')
    else:
        crawler.start()
    
