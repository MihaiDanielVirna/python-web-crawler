# Python multi threaded web crawler

Simple web crawler created for a take home test. Outputs a file with the specified valid asset criteria and a sitemap file. Files can be omitted for testing, by running the crawler with `start(write_files = False)`. Debug mode which prints details can be toggled on by passing `debug = true` to `Crawler` constructor.

### Example usage as module:

```
import crawler

c = crawler.Crawler(your_website, list_of_allowed_tag_attribute_pairs)
c.start()

```
### Example usage from command line:

```
python crawler.py --website http://anywebsite.com -v "img src,a href" -p -d
```
### Script parameters:
--website or -w to specify the starting page <br />
--valid_assets or v to pass the valid tag+attribute pairs valid as an asset in a page. Passed in as comma separated list of pairs. <br />
--profile or -p to run the code with cProfile <br />
--debug or -d to turn debug on
