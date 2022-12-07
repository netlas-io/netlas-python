## Changelog
#### v0.4.0 (2022-12-07)
------------------------

##### Added
- Whois-ip and whois-domain datatypes in `download` method.
- Whois-ip and whois-domain datatypes in `count` method.

##### Changed
- Rename `query` to `search`


#### v0.3.0 (2022-11-11)
------------------------

##### Added
- Include/exclude fields for `query`, `download` and `host`
- Whois-domain search.

##### Changed
- Migrate whois searches in query function.
- Download to stdout by default.

##### Removed
- '-s' server flag.


#### v0.1.6 (2021-08-05)
------------------------

##### Added
- New command `stat` - generate data statistics.


#### v0.1.5 (2021-08-05)
------------------------

##### Changed
- Updated interraction with the `host` API.


#### v0.1.4 (2021-06-18)
------------------------

##### Added
- Pagination in query search.
- Sphinx documentation configs.
- Specify data index for search, count, etc.
- Function and cli-command to retrieve available data indexes.

##### Changed
- Raw stream downloading.
- Migrate API key from GET parameter to HEADER.
- Colored APIError exceptions.

##### Fix
- Downloading via python lib.
- Downloading by given query.
- Updated profile endpoint.
- Commit fix.
- Bump2version config auto commit.


