
# How to use

First of all, set the mongodb credentials in the `danish_cbr_spider/settings.py`

Then run `scrapy crawl companies`

This should scrape the data into the mongodb database

# How I did it 

## CVR generation

The companies in the registry are identified using CVR numbers.

I found the specs for the CVR number verification algorithm (along with implementation using ruby) and wrote an algorithm that generates them ([spec](https://web.archive.org/web/20160410033847/https://erhvervsstyrelsen.dk/modulus-11-kontrol), [ruby impl](https://gist.github.com/henrik/daf364fb7e22b3b10cad))

It can be found in `danish_cbr_spider/cvr.py`

It seems that success rate (probability of the generated CVR being assigned to any company) is around 80% 

The code was tested using `pytest` (run `pytest danish_cbr_spider/cvr.py`)

## The scraper

Currently, the scraper goes over randomly generated 2000 cvr numbers (not all generated CVRs have companies associated with them so a bit more is generated)

This results in 1,578 company entries

## Using JSON data

Even though the website uses web technologies to display the data, it appears to be fetching the actual data from the API located at `https://datacvr.virk.dk/gateway/virksomhed/hentVirksomhed?cvrnummer={cvr_number}&locale=en`.

The data seems to be a well-structured JSON, so I decided not to parse any HTML and use the JSON

## Data Exploration

Before writing most of the conversion code and designing schema I desided to look at the data itself

First I scraped the raw data

```bash
scrapy crawl companies -O anal/raw_companies.json
```

(disabling all the pipelines in `settings.py`)

Then I loaded it into the jupyter notebook and started exploring (see `anal/schema_devel.ipynb`)

## Json Key Translation

First of all, it seems that most of the json keys are in danish which I don't really understand.

Many of them are domain-specific and not easy to translate.

So the most of the notebook is concerned by this task.

It appears that the website loads some translations from the following URL: https://datacvr.virk.dk/gateway/tekst

I saved it to `anal/raw_translations.json`

Overall, my process for finding a good translation of the JSON consisted of search through en_translations.txt, raw_companies.json, using Google Translate and, sometimes, google to try to understand the meanings of the fields

Currently, the translations are not complete, but it is quite straightforward to implement all of them

See the notebook for more info

## Json schema generation

After translation of the JSON keys I decided to generate JSON schema to understand the format of the data & satisfy the "stongly-typed" requirement

I used [genson](https://github.com/wolverdude/genson) project, which allows to partially automate the process

The schema can potentially be refined using [SchemaStrategy](https://github.com/wolverdude/genson/#schemastrategy-api). It can add more storing types like defining enums in places where currently there are just strings

The resulting schema is saved to `anal/schema.json`

See the notebook for more info

## Person search

The data on persons connected to the company does not seem to include much

There seems to be some kind of ID field, but it seems that it is internal to the service

The only "global" ids available seem to be the name of the person and their address

Both would require some kind of fuzzy matching, which usually requires a specialized database (not a one like mongodb) to handle the load

To facilitate queries like "which companies is this person affiliated with?" one could build a person-centric view of the data

It would store the person as the document and list the companies they are affiliated with

For this one can crawl `https://datacvr.virk.dk/enhed/person/{id}/deltager` pages, which seems to contain such information. Though, if a complete data set is collected, I believe it would not be necessary

One can build this view having only the companies' data.

## Maintenance

In case the structure of the JSON would change one can use the generated JSON schema to detect such a change and use the jupyter notebook to find the translations for the new keys & re-generate the schema
