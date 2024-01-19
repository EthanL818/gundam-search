from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from thefuzz import fuzz
import math

# define a simple class to represent Gundam information
class GundamInfo:
    def __init__(self, store, name, price, status, href, image):
        self.store = store
        self.name = name
        self.price = price
        self.status = status
        self.href = href
        self.image = image

# helper function to find the most similar search result to user inputted gundam
def findMostSimilarGundam(searchResults, name, element, elementClass):
    # empty array to store the fuzz library scores of each search result
    scores = []

    # inserts each score into the array
    for item in searchResults:
        item_name = item.find(element, class_=elementClass).text.strip()

        # Using a weighted average of partial_ratio and token_sort_ratio
        partial_ratio_score = fuzz.partial_ratio(name, item_name)
        token_sort_ratio_score = fuzz.token_sort_ratio(name, item_name)

        # Adjust the weights as needed based on your preferences
        total_score = 0.7 * partial_ratio_score + 0.3 * token_sort_ratio_score
        scores.append(total_score)

    if len(scores) != 0:
        # index of the most similar search result in the gundams array
        mostSimilarIndex = scores.index(max(scores))
        return searchResults[mostSimilarIndex]

# helper function to find the most similar search results to the user inputted gundams, based on the numGundams variable
def findMostSimilarGundams(searchResults, name, element, elementClass, numGundams):
    # empty array to store similar gundams
    similarGundams = []

    # finds "numGundams" number of similar search results
    for x in range(numGundams):
         
         # if the most similar gundam exists
         if findMostSimilarGundam(searchResults, name, element, elementClass) != None:
            # add the most similar gundam to the list and remove it from the search results
            similarGundams.append(findMostSimilarGundam(searchResults, name, element, elementClass))
            searchResults.remove(findMostSimilarGundam(searchResults, name, element, elementClass))
         
         # else, add None to the list to indicate it could not be found
         else:
             similarGundams.append(None) 
         
    return similarGundams

# given gundam name, scrapes PandaHobby website for gundam information, returns an array of relevant values
def checkPandaHobby(name, driver, numGundams):

    # converts the given gundam name into something that can be used within a link
    linkName = name.replace(" ", "+")

    # request to driver for the search page of given gundam
    driver.get(f"https://pandahobby.ca/pages/search-results-page?q={linkName}")

    # Now get the HTML and parse it with BeautifulSoup
    pandaHobby = BeautifulSoup(driver.page_source, "lxml")

    # returns all search results
    searchResults = pandaHobby.find_all("li", attrs={"class":"snize-product"})

    # call helper function to find most similar search results
    gundams = findMostSimilarGundams(searchResults, name, "span", "snize-title", numGundams)

    # empty array to hold all information from panda hobby page to return
    pandaHobbyGundams = []

    for gundam in gundams:
        if gundam != None:
            # checks if gundam is out of stock
            outOfStock = gundam.find("span", class_ = "snize-out-of-stock")
            
            # finds gundam's information
            gundamName = gundam.find("span", class_ = "snize-title").text
            gundamPrice = gundam.find("span", class_ = "snize-price").text
            gundamPage = "https://pandahobby.ca/" + gundam.find("a", class_ = "snize-view-link").get('href')
            gundamImage = gundam.find("img", class_ = "snize-item-image").get('src')

            # return gundam's name, price, and stock status
            if outOfStock == None:
                pandaHobbyGundams.append(GundamInfo("Panda Hobby", gundamName, gundamPrice, "In Stock", gundamPage, gundamImage)) 
            elif outOfStock:
                pandaHobbyGundams.append(GundamInfo("Panda Hobby", gundamName, gundamPrice, "Out of Stock", gundamPage, gundamImage)) 

        # else, return default message that gundam could not be found
        else: 
            pandaHobbyGundams.append(GundamInfo("Panda Hobby", "Could Not Be Found", "N/A", "N/A", "N/A", "N/A",)) 

    return pandaHobbyGundams

# given gundam name, scrapes Candian Gundam website for gundam information, returns an array of relevant values
def checkCanadianGundam(name, driver, numGundams):

    # converts the given gundam name into something that can be used within a link
    linkName = name.replace(" ", "+")

    # request to driver for the search page of given gundam
    driver.get(f"https://www.canadiangundam.com/search?controller=search&orderby=position&orderway=desc&search_query={linkName}&submit_search=")

    # Now get the HTML and parse it with BeautifulSoup
    canadianGundam = BeautifulSoup(driver.page_source, "lxml")

    # returns all search results
    searchResults = canadianGundam.find_all("div", class_ = "product-container")

    # call helper function to find most similar search result
    gundams = findMostSimilarGundams(searchResults, name, "a", "product-name", numGundams)

    # empty array to hold all information from panda hobby page to return
    canadianGundams = []

    for gundam in gundams:
        if gundam != None:
            # checks if gundam is out of stock
            outOfStock = gundam.find("span", class_ = "availability").span.text.strip()

            # finds gundam's information
            gundamName = gundam.find("a", class_ = "product-name").text.strip()
            gundamPrice = gundam.find("span", class_ = "product-price").text.strip()
            gundamPage = gundam.find("a", class_ = "button lnk_view btn btn-default").get('href')
            gundamImage = gundam.find("img", class_ = "replace-2x img-responsive").get('src')

            # return gundam's name, price, and stock status
            if outOfStock == "In Stock":
                canadianGundams.append(GundamInfo("Canadian Gundam", gundamName, gundamPrice, "In Stock", gundamPage, gundamImage)) 
            
            elif outOfStock == "Out of stock" :
                canadianGundams.append(GundamInfo("Canadian Gundam", gundamName, gundamPrice, "Out of Stock", gundamPage, gundamImage)) 
            
        # else, return default message that gundam could not be found
        else: 
            canadianGundams.append(GundamInfo("Canadian Gundam", "Could Not Be Found", "N/A", "N/A", "N/A", "N/A")) 

    return canadianGundams

# given gundam name, scrapes Argama Hobby website for gundam information, returns an array of relevant values
def checkArgamaHobby(name, driver, numGundams):

    # converts the given gundam name into something that can be used within a link
    linkName = name.replace(" ", "+")

    # request to driver for the search page of given gundam
    driver.get(f"https://argamahobby.com/search?type=article%2Cpage%2Cproduct&q={linkName}")

    # parses HTML of Argama Hobby website
    argamaHobby = BeautifulSoup(driver.page_source, "lxml")

    # returns all search results
    searchResults = argamaHobby.find_all("div", class_ = "productitem")

    # call helper function to find most similar search result
    gundams = findMostSimilarGundams(searchResults, name, "h2", "productitem--title", numGundams)

    # empty array to store argama hobby gundam information
    argamaHobbyGundams = []

    for gundam in gundams:
        if gundam != None:
            # checks if gundam is out of stock
            outOfStock = gundam.find("span", class_ = "productitem__badge productitem__badge--soldout")

            # finds gundam's name and price
            gundamName = gundam.find("h2", class_ = "productitem--title").a.text.strip()
            gundamPrice = gundam.find("span", class_ = "money price__compare-at--min").text.strip()
            gundamPage = "https://argamahobby.com" + gundam.find("a", class_ = "productitem--image-link").get('href')
            gundamImage = "https:" + gundam.find("img", class_= "productitem--image-primary").get('src')

            # return gundam's name, price, and stock status
            if outOfStock == None:
                argamaHobbyGundams.append(GundamInfo("Argama Hobby",gundamName, gundamPrice, "In Stock", gundamPage, gundamImage)) 
            elif outOfStock:
                argamaHobbyGundams.append(GundamInfo("Argama Hobby", gundamName, gundamPrice, "Out Of Stock", gundamPage, gundamImage)) 
        
        # else, return default message that gundam could not be found
        else: 
            argamaHobbyGundams.append(GundamInfo("Argama Hobby", "Could Not Be Found", "N/A", "N/A", "N/A", "N/A")) 

    return argamaHobbyGundams

# given gundam name, scrapes Toronto Gundam website for gundam information, returns an array of relevant values
def checkTorontoGundam(name, driver, numGundams):

    # converts the given gundam name into something that can be used within a link
    linkName = name.replace(" ", "+")

    # request to driver for the search page of given gundam
    driver.get(f"https://www.torontogundam.ca/search?q={linkName}&type=product")

    # parses HTML of Toronto Gundam website
    torontoGundam = BeautifulSoup(driver.page_source, "lxml")

    # returns all search results
    searchResults = torontoGundam.find_all("div", class_ = "respimgsize tt-product product-parent options-js thumbprod-center")

    # call helper function to find most similar search result
    gundams = findMostSimilarGundams(searchResults, name, "h2", "tt-title prod-thumb-title-color", numGundams)

    # empty array to store Toronto Gundam gundam information
    argamaHobbyGundams = []

    for gundam in gundams:
        if gundam != None:
            # checks if gundam is out of stock
            outOfStock = gundam.find("span", class_ = "tt-label-our-stock")

            # finds gundam's name and price
            gundamName = gundam.find("h2", class_ = "tt-title prod-thumb-title-color").text.strip()
            gundamPrice = gundam.find("div", class_ = "tt-price").span.text.strip()
            gundamPage = "https://www.torontogundam.ca" + gundam.find("a", class_ = "tt-img-parent").get('href')
            gundamImage = "https:" + gundam.find("img", class_= "lazyload").get('srcset')

            # return gundam's name, price, and stock status
            if outOfStock == None:
                argamaHobbyGundams.append(GundamInfo("Toronto Gundam",gundamName, gundamPrice, "In Stock", gundamPage, gundamImage)) 
            elif outOfStock:
                argamaHobbyGundams.append(GundamInfo("Toronto Gundam", gundamName, gundamPrice, "Out Of Stock", gundamPage, gundamImage)) 
        
        # else, return default message that gundam could not be found
        else: 
            argamaHobbyGundams.append(GundamInfo("Toronto Gundam", "Could Not Be Found", "N/A", "N/A", "N/A", "N/A")) 

    return argamaHobbyGundams

# function takes in gundam's name and grade as input, outputs a comparison of prices across retailers
def find_gundam(gundamName, numGundams, progress_callback, hobbyStores):
    # create a headless chrome web driver to access website information
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    progressIncrement = math.ceil(100/len(hobbyStores))
    runningTotal = 0
    data = []

    for hobbyStore in hobbyStores:
        if hobbyStore == "Panda Hobby":
            data.append(checkPandaHobby(gundamName, driver, numGundams))
            runningTotal += progressIncrement
            progress_callback.updateProgress.emit(runningTotal)
        
        elif hobbyStore == "Canadian Gundam":
            data.append(checkCanadianGundam(gundamName, driver, numGundams))
            runningTotal += progressIncrement
            progress_callback.updateProgress.emit(runningTotal)
        
        elif hobbyStore == "Argama Hobby":
            data.append(checkArgamaHobby(gundamName, driver, numGundams))
            runningTotal += progressIncrement
            progress_callback.updateProgress.emit(runningTotal)

        elif hobbyStore == "Toronto Gundam":
            data.append(checkTorontoGundam(gundamName, driver, numGundams))
            runningTotal += progressIncrement
            progress_callback.updateProgress.emit(runningTotal)


    return data

# TODO: add more information window