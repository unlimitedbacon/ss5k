#!flask/bin/python

import os
import re
import time
from bs4 import BeautifulSoup
from datetime import date, datetime
from urllib.request import urlopen

from app import db, logdir
from config import SCAN_DELAY
from .models import User, Junkyard, Car, WantedCar
from .email import send_notification

test = True

def junkscraper(yard, make, model, color):
    # Clean up strings
    if make is None:
        make = ''
    if model is None:
        model = ''
    if color is None:
        color = ''

    # Create URL
    store = str(yard.code)
    search = "+".join([make,model,color]).replace(' ','+')

    #url = site + path + '?store=' + store + '&page=' + page + '&filter=' + sfilter + '&sp=' + special + '&cl=' + classics + '&carbuyYardCode=' + carbuyYardCode + '&pageSize=' + pageSize + '&language=' + language + '&thumbQ=' + thumbQ + '&fullQ=' + fullQ
    url = "https://www.lkqpickyourpart.com/locations/somewhere-" + store + "/recents/?search=" + search

    # Fetch Data
    # Commented out lines are for storing and reading data for debugging
    #data = open('testdata/%s.html' % sfilter, 'r').read()
    data = urlopen(url).read().decode('utf-8')

    #f = open('testdata/%s.html' % sfilter, 'w')
    #f.write(data)
    #f.close()

    # Parse Data
    soup = BeautifulSoup(data, 'html.parser')

    cars = []

    for row in soup.findAll('div', attrs={'class': 'pypvi_resultRow'}):
        c = Car(yard)
        # Get a picture of the car if it has one, or insert the placeholder if it doesn't
        try:
            c.image = row.find(attrs={'class': 'pypvi_image'}).img.get('src')
            c.imglink = row.find(attrs={'class': 'pypvi_image'}).get('href')
        except AttributeError:
            c.image = 'https://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/Images/pypvi_placeholder.png'
            c.imglink = ''
        ymm = row.find(attrs={'class': 'pypvi_ymm'}).get_text().split(' ', 2)
        #c.make = list( row.find(attrs={'class': 'pypvi_make'}).strings )[0]
        #c.model = row.find(attrs={'class': 'pypvi_model'}).get_text()
        #c.year = row.find(attrs={'class': 'pypvi_year'}).get_text()
        c.year = ymm[0]
        c.make = ymm[1]
        c.model = ymm[2]
        #c.notes = row.find(attrs={'class': 'pypvi_notes'}).get_text('\n')
        c.notes = ''
        for n in row.find_all(attrs={'class': 'pypvi_detailItem'}):
            c.notes += n.get_text()
            c.notes += '\n'

        #datestr = row.find(attrs={'class': 'pypvi_date'}).get_text()
        datestr = row.find('time').get_text()
        month,day,year = datestr.split('/')
        c.arrival_date = date(int(year),int(month),int(day))

        #c.uid = c.image.split('/')[5].split('.')[0]
        c.uid = row['id']     # Other possibility
        c.last_seen = datetime.now()

        cars.append(c)

    return cars

def scan():
    junkyards = db.session.query(Junkyard)

    then = datetime.now()
    searchcount = 0
    newcount = 0
    emailcount = 0

    for yard in junkyards:
        searched = []
        print(':: Scanning Junkyard', yard.code, ':', yard.name, yard.city, yard.state)
        for wantedcar in yard.wanted_cars:
            if not wantedcar in searched:
                # Check for any other wanted cars with matching make/model
                group = yard.match_searches(wantedcar)
                print("   %i people looking for %s %s %s" % (len(group),wantedcar.make,wantedcar.model,wantedcar.color))
                # Query junkyard api for make/model
                cars = junkscraper(yard,wantedcar.make,wantedcar.model,wantedcar.color)
                numfound = len(cars)
                searchcount += 1
                # For each car found, check if it is already in the db. If so, forget about it.
                for c in reversed(cars):
                    dbcar = Car.query.filter_by(uid=c.uid).first()
                    if dbcar is not None:
                        dbcar.last_seen = c.last_seen
                        cars.remove(c)
                print("      %i cars found, %i not already in database" % (numfound,len(cars)))
                newcount += len(cars)
                # For each of the wanted cars, check list from junkyard to see if any match year
                numsent = 0
                for g in group:
                    user = User.query.get(g.user_id)
                    years = g.years.split(', ')
                    for c in cars:
                        if c.year in years or years == []:
                            # For each that match, send email
                            send_notification(user, c, yard)
                            numsent += 1
                            emailcount += 1
                print("      %i Emails sent" % (numsent))
                # Mark wanted cars as already searched
                searched += group
                # Add cars to db
                for c in cars:
                    db.session.add(c)
                db.session.commit()
                # Be nice to the servers
                time.sleep(SCAN_DELAY)

    # Log some statistics
    now = datetime.now()
    duration = now - then
    date = then.ctime()
    usercount = db.session.query(User).count()
    wantedcount = db.session.query(WantedCar).count()
    carcount = db.session.query(Car).count()
    stats = "Users: %i Wanted Cars: %i Cars in DB: %i Searches Made: %i New Cars: %i Emails sent: %i Scan Time: %f" % (usercount, wantedcount, carcount, searchcount, newcount, emailcount, duration.total_seconds())
    print(stats)
    log = open(os.path.join(logdir,'daemon.log'), 'a')
    print("%s: %s" % (date, stats), file=log)
