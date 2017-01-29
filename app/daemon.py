#!flask/bin/python

from bs4 import BeautifulSoup
from datetime import date
from urllib.request import urlopen

from app import db
from .models import User, Junkyard, Car
from .email import send_notification

def junkscraper(yard, make, model):
    store = str(yard.code)
    sfilter = "+".join([make,model]).replace(' ','+')
    page = "0"
    special = ""
    classics = ""
    carbuyYardCode = '1'+store
    pageSize = "100"
    language = "en-US"
    thumbQ = "60"
    fullQ = "70"

    site = "https://www.lkqpickyourpart.com"
    path = "/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx"

    url = site + path + '?store=' + store + '&page=' + page + '&filter=' + sfilter + '&sp=' + special + '&cl=' + classics + '&carbuyYardCode=' + carbuyYardCode + '&pageSize=' + pageSize + '&language=' + language + '&thumbQ=' + thumbQ + '&fullQ=' + fullQ

    #data = urlopen(url).read().decode('utf-8')
    data = open('%s.html' % sfilter, 'r').read()

    #f = open('%s.html' % sfilter, 'w')
    #f.write(data)
    #f.close()

    soup = BeautifulSoup(data, 'html.parser')

    cars = []

    for row in soup.findAll('tr', attrs={'class': 'pypvi_resultRow'}):
        c = Car(yard)
        c.image = row.find(attrs={'class': 'pypvi_image'}).img.get('src')
        c.imglink = row.find(attrs={'class': 'pypvi_image'}).a.get('href')
        c.make = list( row.find(attrs={'class': 'pypvi_make'}).strings )[0]
        c.model = row.find(attrs={'class': 'pypvi_model'}).get_text()
        c.year = row.find(attrs={'class': 'pypvi_year'}).get_text()
        #c.notes = row.find(attrs={'class': 'pypvi_notes'})
        c.notes = "TEST"

        datestr = row.find(attrs={'class': 'pypvi_date'}).get_text()
        month,day,year = datestr.split('/')
        c.arrival_date = date(int(year),int(month),int(day))

        c.uid = c.image.split('/')[5].split('.')[0]

        cars.append(c)
        print(c)
        print(c.uid)

    return cars

def scan():
    junkyards = db.session.query(Junkyard)

    for yard in junkyards:
        searched = []
        print(yard)
        for wantedcar in yard.wanted_cars:
            if not wantedcar in searched:
                print(yard,wantedcar)
                # Check for any other wanted cars with matching make/model
                group = yard.match_searches(wantedcar)
                print(group)
                # Query junkyard api for make/model
                cars = junkscraper(yard,wantedcar.make,wantedcar.model)
                # For each car found, check if it is already in the db. If so, forget about it.
                print(len(cars))
                for c in reversed(cars):
                    dbcar = Car.query.filter_by(uid=c.uid).first()
                    if dbcar is not None:
                        cars.remove(c)
                print(len(cars))
                # For each of the wanted cars, check list from junkyard to see if any match year
                for g in group:
                    user = User.query.get(g.user_id)
                    years = g.years.split(', ')
                    for c in cars:
                        if c.year in years:
                            # For each that match, send email
                            send_notification(user, c)
                # Mark wanted cars as already searched
                searched += group
                # Add cars to db
                for c in cars:
                    db.session.add(c)
                db.session.commit()
