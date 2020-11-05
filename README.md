# Wikipedia-Search-Engine

It is a search engine on the Wikipedia Data Dump without using any external index. For this project we use the data dump of size 48 GB. The search results returns in real time supporting both simple and field queries.

## Steps involved in Indexing
+ Parsing 
+ Tokenization
+ Case Folding
+ Stop Words Removal
+ Stemming
+ Inverted Index Creation - Multi-way External sorting on the index files

## Searching:
+ The query given is parsed, processed and given to the respective query handler(simple or field).
+ The documents are ranked on the basis of TF-IDF scores.
+ The title of the documents are extracted using title.txt
+ First 10 matched document titles along with their ID's are stores in output.txt


## How to run:

#### python3 wiki_indexer.py <xml file dump> 
This function takes as input the corpus file and creates the entire index in the index folder and all the titles are stores in the title folder. Size of index is almost 1/4 the size of corpus.

#### python3 wiki_search.py <location(queries.txt)>
This function returns the first 10 matched document titles along with their ID's are stores in output.txt for the indivisual queries.
