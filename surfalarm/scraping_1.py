import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import pandas as pd

def region_spot(region):
    url = f"https://www.surf-report.com/meteo-surf/france/{region.lower()}"
    response = requests.get(url)
    return response.text

def spots_2_search(region):
    # Get the HTML with the previous function
    html = region_spot(region)
    
    # Start the seach
    soup = BeautifulSoup(html, "html.parser")
    spots= []
    for spot in soup.find_all("div", class_ ="card forecast list"):
        
        #get the spot town
        spot_town = spot.find("b").string
        
        #get the spot name
        if spot.find("br"):
            spot_name = spot.br.next_sibling
        else:
            spot_name = "No spot name"
        
        #get the URL
        url_end = spot.find("a")["href"]
        url = "https://www.surf-report.com/meteo-surf" + url_end
        
        spots.append([spot_name, spot_town, region, url])
        
    return spots

def spot_to_html(spot_url):
    response = requests.get(spot_url)
    return response.text

def spot_data(spot_url):
    ### This function will look if a spot has more than 10 stars in 1 day in the next 3 days
    
    # Getting the HTML of the spot with previous function
    spot_html = spot_to_html(spot_url)
    soup = BeautifulSoup(spot_html, "html.parser")
    
    today = date.today()
    
    for day in soup.find_all("div", class_="forecast-tab"):
        
        # Count the number of stars for a day
        stars = len(day.find_all("i", class_="fa fa-star"))
        
        # Look at the forecast of the next 3 days only
        if stars > 10:
            wave = day.find("b").string
            day_date_string = day.find("b").string
            day_date = douille_datetime(day_date_string)
            jour = (day_date - today).days
            
            # for today's waves:
            #if jour < 1:
            
            # for the next 3 days only:
            if jour > 0 and jour < 4:
                
                return [spot_url, stars, day_date_string]
            pass
        pass
    pass

def douille_datetime(day):
    output = "2021-"
    
    # deleting the alphabetical version of day
    
    day = day[5:]
    for char in day:
        if not char.isnumeric():
            day = day[1:]
        else :
            break
    
    # changing the month to a number
    month = day[2:]
    for char in month:
        if not char.isalpha():
            month = month[1:]
        else :
            break
            
    if month == "Janvier":
        month = "01"
    elif month== "Fevrier":
        month = "02"
    elif month== "Mars":
        month = "03"
    elif month== "Avril":
        month = "04"
    elif month == "Mai":
        month = "05"
    elif month== "Juin":
        month = "06"
    elif month== "Juillet":
        month = "07"
    elif month== "Aout":
        month = "08"
    elif month== "Septemre":
        month = "09"
    elif month== "Octobre":
        month = "10"
    elif month== "Novembre":
        month = "11"
    elif month== "Décembre":
        month = "12"

    # 0 padding the day of the date
    day = ''.join(ch for ch in day if ch.isnumeric())
    if len(day) == 1:
        day = "0" + day
    pass

    output = output + month + "-" +  day
    
    #return output
    return date.fromisoformat(output)

def region_spots_data(region_liste):
    
    ### Gives all the *spots* AND the soon-exceptional spots for a given list of region(s)
    ### Input must be a list -> ['Bretagne'] or ['bretagne', 'nord']
    
    best_liste = []
    spot_liste = []
    
    for region in region_liste:
        region_spot_liste = spots_2_search(region)
        
        for spot in region_spot_liste:
            spot_liste.append(spot)
            good_spot = spot_data(spot[3])
            if good_spot:
                best_liste.append(good_spot)
    
    spots_df = pd.DataFrame(spot_liste, columns=['spot', 'ville', 'region', 'url'])
    best_spots_df = pd.DataFrame(best_liste, columns=['url', 'stars', 'date'])
    
    
    return spots_df, best_spots_df

all_regions = ["Nord", "Manche", "Bretagne", "loire-atlantique",
               "Vendee", "charente-maritime", "Gironde", "Landes",
               "pays-basque", "golfe-lion", "cote-dazur", "corse"]
france_spot, france_best = region_spots_data(all_regions)
df = france_best.join(france_spot.set_index('url'), on='url')

today = date.today()
df.to_csv(f'data/{str(today)}.csv', index=False, sep=",")

print(f'{df.shape[0]} good surf spots on {today.strftime("%A %d %B %Y")}')
