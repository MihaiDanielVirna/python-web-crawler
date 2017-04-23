# Python multi threaded web crawler

Simple web crawler created for a take home test. Outputs a file with the specified valid asset criteria and a sitemap file. Files can be omitted for testing, by running the crawler with `start(write_files = False)`.

### Example usage as module:

```
import crawler

c = crawler.Crawler(list_of_allowed_tag_attribute_pairs,your_website)
c.start()

```
### Example usage by running main.py from command line:

```
python main.py --website http://anywebsite.com -v "img src,a href" -p
```
### Script parameters:
--website or -w to specify the starting page <br />
--valid_assets or v to pass the valid tag+attribute pairs valid as an asset in a page. Passed in as comma separated list of pairs. <br />
--profile or -p to run the code with cProfile 
