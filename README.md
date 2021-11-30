# concurrent-web-crawler
Web crawler and indexer using parallel processing.

Three crawlers having different functioning have been analysed for the project. The most optimised version is a hybrid of the other two crawlers. The configurations are as follows:

1. Serial Crawler and Indexer - SCSI - serial_crawler.py
2. Concurrent Crawler and Indexer - CCCI - concurrent_crawler.py
3. Concurrent Crawler with Serial Indexer - CCSI - hybrid_crawler.py

The third version - "Concurrent Crawler with serial Indexer", shows the most optimum results when tested.

![image](https://user-images.githubusercontent.com/59339769/144087763-eca3aebd-c54d-44aa-86ce-6d88ec014a1c.png)
![image](https://user-images.githubusercontent.com/59339769/144087811-72a5e013-0741-47b5-94f7-91b82a77ea05.png)

For the above results, URL used was
urlinput = https://en.wikipedia.org/wiki/Black_hole
base = https://en.wikipedia.org/wiki/
