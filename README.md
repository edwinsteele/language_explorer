# Language Explorer

A data analysis tool to help identify language groups in particular need of
bible translation based on various data sources and linguistic databases.

**This is a proof of concept**

As a proof-of-concept, the focus has been on the integration of discrete
data sources, and while care has been taken to identify errors during the
data import, it would be inappropriate to consider this as a tool to drive
decision making without review of the aggregation process and scrutiny of
the data itself.

# Focus on Aboriginal Australian Languages and Bible Translation

This proof-of-concept focuses on the languages of Aboriginal Australia - I love
our Aboriginal people, and want to see them have access to the bible, preferably
in their native tongue.

# Data sources

* [Joshua Project](http://www.joshuaproject.net) - Import of Harvest database
* [WALS](http://wals.info) - Import of WALS 2013 database
* [Australian Census 2011](http://www.abs.gov.au/websitedbs/censushome.nsf/home/census) - Import of custom table data
* [SIL](http://www-01.sil.org/iso639-3/) - Import of ISO 639-3 retired code elements mappings
* [Find A Bible](http://findabible.net) - Web scrape of relevant Australian Aboriginal bible translation data
* [Austlang](http://austlang.aiatsis.gov.au/php/public/public_home.php) - Web scrape of Australian Aboriginal language data

Some more information is available in the DataSources.md file in the docs
directory.

# A live instance of this tool

I have deployed a live instance of this tool at https://language-explorer.wordspeak.org.
The purpose of this deployment is only casual review of the output of the
aggregation engine and to show what is possible with this style of aggregation and analysis.

I have not attempted to licence the data that is imported into the database and
subsequently displayed in the tool so **if you are from an organisation whose
data I am using, and I am violating your licence agreement by displaying it in
this proof-of-concept instance, please contact me at <edwin@wordspeak.org>**.
I don't wish to cause problems with this tool.

# Deployment

Should you wish to deploy this yourself, it's not going to be a smooth process.
It is repeatable for me, and there is some documentation in the DataSources.md
and install.md documents in the "docs" directory. Contact me if you have any
problems - I'm happy to help.


-- Edwin Steele <edwin@wordspeak.org>

