# BillBored

BillBored is a music quiz website utilizing Flask client/server connection and 
a SQLite database, created from scraping data from Billboard and Tunebat.

Hosted on science.slc.edu/billbored/ using gunicorn.

## Known Bugs

Structure of question loading is not ideal and all metadata on each question
(and all upcoming questions) are visible to someone who knows where to look.
Future version would ideally place question parsing and generation all in 
the server side.
    
Navigation from end page -> home page -> question page causes a 500 internal
error server crash.

Clicking too quickly on a choice results in an artificially high score.

Some answers ("Tonight (I'm Lovin You) by Enrique Iglesias featuring Ludacris
and DJ Frank E", "Party Rock Anthem by Lmfao Featuring Lauren Bennett and 
Goonrock") are too long and overflow out of the button.

## Acknowledgements

Created by Vilem Boddicker, Rachel Williams, and Austin Jones. Special thanks
to Michael Siff for the assignment and helping us through the magic of email. 