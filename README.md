
# thegame.report data

An attempt to organise, standardise, and share the data of our league.

### Update 2019-11-21

In 1-2 weeks data will become available on a browsable website and potentially through a JSON or CSV API.

The raw input data is already available under `raw_data/`, but if you are looking to process it programmatically
you'll probably find the extracts available under `skdb/` more handy. These denormalised CSV files are used 
to populate the new **Stats Keyboard Database** (skdb) which is what the browsable website will expose.

Data under `raw_data/` is what we have gathered originally from different stats tracking apps (for season 24),
and for season 25 it is what we are extracting from the **Stats Keyboard** app. The format of the raw data is
an internal implementation detail and expect it to change and break any integrations.
