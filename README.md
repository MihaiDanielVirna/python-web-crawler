# Python multi threaded web crawler

Simple web crawler created for a take home test. Can be used as a script or module. Outputs a file with the specified valid asset criteria and a sitemap file.

### Example usage as module:

```
import crawler

c = crawler.Crawler(list_of_allowed_tag_attribute_pairs,your_website)
c.start()

```
