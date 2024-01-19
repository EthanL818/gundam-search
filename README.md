# gundam-search

A web scraping program that checks four local Canadian hobby stores (Panda Hobby, Canadian Gundam, Argama Hobby, and Toronto Gundam) simultaneously and displays their information in an easy to digest format. Let's say you're looking for a deal on the newest Gunpla release, but have no idea which store offers the cheapest option. Well, look no further. Simply enter the name of any item into the search bar, adjust the various filters and settings to your liking, and click the search button. `gundam-search` will scrape the relevant information from the various local hobby stores' websites, and provide that information to you in an easy to read table format.

## To Use

Download the repository zip file and acess the dist folder, then run gui.py to run the program, or open the folder locally on your IDE of choice and run `pip install requirements.txt` to install the required dependencies locally. Once you have the program running, adjust filters as you see fit and enjoy.

## Tips

Try to be as specific as possible when using the search bar. For example, if you are searching for the `MG RX-93 Nu Gundam Ver.Ka 1/100`, inputting `nu gundam` will probably lead to mixed results. Instead, try inputting keywords like the grade of the gundam, the scale, etc. (the more specific the better). If you have been as specific as possible and there are still some outliers appearing in your table, you can mess with the `# of items per store` setting to show multiple items per store. This will increase the likelihood that your desired item will appear.

## Packages Used

`PyQt5` was used for the GUI, `requests`, `beautifulsoup4`, and `selenium` were used for the webscraping, and `thefuzz` was used for fuzzy string comparison logic.
