# note: this is just where I keep track of future features for the config

## config
 + typeFilters - an array containing valid incident types. If it contains a "\*", then this list is a blacklist. Otherwise, it is treated as a whitelist.


## locations
 + regex - a regex expression to use for the comparison instead of the `match` property
 + days - a day list string, something like "WEEK" or "WEEKEND" or "M, T, TH, F, SAT". only monitor on these days
 + time - a time range filter string, something like "10AM-11PM", or "3:45PM-4:00PM, 6PM-9AM". 

time and days probably won't come until I make my highly versatile configuration framework.

