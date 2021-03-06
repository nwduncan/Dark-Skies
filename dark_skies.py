# a basic program that determines the best nights for stargazing based on the
# moon's phase and rise/set times
import ephem
import os
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageDraw
import math
import dark_calendar
from random import randint
import uuid

# # location parameters
name = "Albury"
lat = -36.07
lon = 146.91
timezone = "Australia/Sydney"
timezone = "Europe/London"
observer = ephem.Observer()
observer.name = name
observer.lat = str(lat)
observer.lon = str(lon)
start_date = datetime(2018,1,1)
end_date = datetime(2018,12,31)
# location parameters
# name = "Albury"
# lat = 0
# lon = 0
# timezone = "America/Anchorage"
# elev = 160

# observer initialisation
# observer = ephem.Observer()
# observer.name = name
# observer.lat = str(lat)
# observer.lon = str(lon)
# start_date = datetime(2018,1,1)
# end_date = datetime(2018,12,31)

def moon_phases(dates):

    # define location parameters
    observer = ephem.Observer()
    observer.name = name
    observer.lat = str(lat)
    observer.lon = str(lon)
    # set the horizon to 18 degrees below 0 to simulate astronomical twilight
    # observer.horizon = "-18"

    for date in dates:

        observer.date = date[0]
        moon = ephem.Moon()
        event = observer.next_rising(moon, use_center=False)
        event_utc = ephem.Date(event)
        event_local = event_utc.datetime() + date[1]
        illum = int(round(moon.phase/5.0))
        phase = chr(219)*illum+chr(176)*(20-illum)
        day = date[0].strftime("%Y-%m-%d")
        diff = event_local-date[0]
        next_rising = event_local.strftime("%Y-%m-%d %H:%M:%S")+" +1" if diff.days == 1 else event_local.strftime("%Y-%m-%d %H:%M:%S")+"   "
        print "{} Next rising: {} {} {}%".format(day, next_rising, phase, int(round(moon.phase)))


def dark_skies(start_date=start_date, end_date=end_date, lat=lat, lon=lon, time_adjust=12):
    id = str(uuid.uuid4())
    os.mkdir(os.path.join(os.getcwd(), 'static', 'images', id))

    if type(time_adjust) != timedelta:
        time_adjust = timedelta(hours=time_adjust)

    # output = open('page.html', 'w')
    output = []

    # name = "Albury"
    # lat2 = -36.07
    # lon2 = 146.91
    # print lat, type(lat), lat2, type(lat2)
    # print lon, type(lon), lon2, type(lon2)

    timezone = "Australia/Sydney"
    observer = ephem.Observer()
    # observer.name = name
    # start_date = datetime(2018,1,1)
    # end_date = datetime(2018,12,31)

    # build our date objects
    observer = ephem.Observer()
    observer.lat = str(float(lat))
    observer.lon = str(float(lon))
    # observer.lat = str(lat)
    # observer.lon = str(lon)
    calendar = dark_calendar.Calendar(start_date, end_date, time_adjust, observer, timezone)
    calendar.build_range()
    calendar.compute_sun()
    calendar.compute_moon()

    # image variables
    img_width = 768
    img_height = 20

    twilight_rgb = {'day': (255, 142, 94),
                    'civil': (255, 38, 34),
                    'nautical': (150, 0, 49),
                    'astronomical':(66, 1, 57),
                    'night': (12, 1, 38) }


    # twilight_rgb = {'day': (245, 192, 143),
    #                 'civil': (220, 135, 91),
    #                 'nautical': (155, 84, 81),
    #                 'astronomical':(69, 36, 82),
    #                 'night': (9, 4, 21) }
    #
    # twilight_rgb = {'day': (142, 203, 238),
    #                 'civil': (110, 157, 184),
    #                 'nautical': (78, 112, 131),
    #                 'astronomical':(46, 66, 78) ,
    #                 'night': (6, 6, 6) }

    # twilight_rgb = {'day': (255, 240, 231),
    #                 'civil': (252, 167, 123),
    #                 'nautical': (196, 111, 76),
    #                 'astronomical':(113, 61, 51) ,
    #                 'night': (24, 9, 29) }

    # twilight_rgb = {'day': (204, 39, 73),
    #                 'civil': (155, 45, 71),
    #                 'nautical': (101, 51, 76),
    #                 'astronomical':(51, 56, 76) ,
    #                 'night': (2, 61, 79) }

    # twilight_rgb = {'day': (216, 229, 248),
    #                 'civil': (165, 177, 193),
    #                 'nautical': (115, 126, 139),
    #                 'astronomical':(65, 75, 85) ,
    #                 'night': (17, 27, 34) }


    def stars(img_width, img_height):
        transp_limits = (10, 100)
        stars_per_pixel = 0.005
        pixels = img_height * img_width
        overlay = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        for x in range(0, int(pixels*stars_per_pixel)):
            rand_x = randint(0, img_width-1)
            rand_y = randint(0, img_height-1)
            draw_overlay.rectangle((rand_x, rand_y, rand_x, rand_y), (255, 255, 255, randint(transp_limits[0], transp_limits[1])))
        return overlay

    # # header image
    # header = Image.new('RGB', (img_width, img_height), (0, 0, 0))
    # for x in range(0,img_width,(img_width/24)):
    #     draw_header = ImageDraw.Draw(header)
    #     draw_header.rectangle((x, 0, x, img_height), fill=(33,33,33))
    #     path = os.path.join('static', 'images', id, 'header.png')
    #     header.save(path)
    # output.append(os.path.join(id, 'header.png'))


    for date in calendar.dates:
        # master image
        filename = str(date.date.date())+'.png'
        path = os.path.join('static', 'images', id, filename)
        image = Image.new('RGB', (img_width, img_height), (255, 255, 255))
        image = image.convert('RGBA')
        draw = ImageDraw.Draw(image)

        # draw sun events over master image
        length_count = 0
        for instr in date.sun_instructions:
            length = int(round(instr[0]/86400*img_width, 0))
            colour = twilight_rgb[instr[1]]
            draw.rectangle((length_count, 0, length+length_count, img_height), colour)
            length_count += length

        # create moon overlay
        length_count = 0
        moon = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw_moon = ImageDraw.Draw(moon)
        # print date.date, date.moon_instructions, [str(d)+" "+a for d, a in date.moon_events ]
        for instr in date.moon_instructions:
            length = int(round(instr[0]/86400*img_width, 0))
            opacity = int(round((80*date.moon_illum)+20, 0)) if instr[1] else 0
            draw_moon.rectangle((length_count, 0, length+length_count, img_height), (255, 255, 255, opacity))
            length_count += length
        image = Image.alpha_composite(image, moon)
        #
        # grid = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        # draw_grid = ImageDraw.Draw(grid)
        # for x in range(0,img_width,(img_width/24)):
        #
        #     draw_grid.rectangle((x, 0, x, img_height), fill=(255,255,255,25))
        # image = Image.alpha_composite(image, grid)

        overlay = stars(img_width, img_height)
        image = Image.alpha_composite(image, overlay)
        overlay = Image.new('RGBA', image.size, (0,0,0,0))
        draw_temp = ImageDraw.Draw(overlay)
        draw_temp.rectangle((0, img_height-1, img_width, img_height), fill=(255,255,255,18))
        image = Image.alpha_composite(image, overlay)
        image.save(path)
        output.append([os.path.join(id, filename), date])
        # output.write('<img src="images\{}">{} - {}<br/>'.format(filename, date.date.date(), date.moon_phase))
        # print to_print

    return output

## notes
# refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for possible tz variables
# moon_phase method instead of phase method when returning current moon illumination
# body.separation method provides angle between two positions on sphere
# from ephem import cities >> albury = cities.lookup('Albury, Australia') returns lat lon for Albury
# when sun/moon(?) never rise/set at the poles an ephem.CircumpolarError error will be thrown for next_xxx() methods which needs to be taken in to account


## resources
# Moon illumination and resulting skyglow relationship
# http://www.skyandtelescope.com/astronomy-resources/astronomy-questions-answers/how-does-the-moons-phase-affect-the-skyglow-of-any-given-location-and-how-many-days-before-or-after-a-new-moon-is-a-dark-site-not-compromised/
