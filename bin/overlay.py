#!/usr/bin/env python3

import codecs
import glob
import logging
import os
import sys
from optparse import OptionParser

import folium
import xml.sax, xml.sax.handler
import pandas as pd

logging.basicConfig(level=logging.INFO)

def gpx2pickle(source, dest):

    locations = []

    class Handler(xml.sax.handler.ContentHandler):
        def startElement(self, name, attrs):
            if (name == 'trkpt'):
                locations.append([float(attrs['lat']), float(attrs['lon'])])

    parser = xml.sax.make_parser()
    parser.setContentHandler(Handler())

    with codecs.open(source, 'r', 'utf-8') as io:
        parser.parse(io)

    df = pd.DataFrame(locations)
    df.to_pickle(dest)

    return df

def drawPolyLines(osm, df):
    locations = df.values.tolist()
    c = folium.PolyLine(locations=locations, color=options.color,
                        weight=options.weight, opacity=options.alpha)
    osm.add_child(c)

def buildMap():
    logging.info('mkdir tmp')
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    osm = folium.Map(location=options.location,
                     zoom_start=options.zoom, tiles=options.tiles)

    gpxes = glob.glob(options.activities)
    if not gpxes:
        raise 'GPX activities not found in' + options.activities

    logging.info('converting gpx to pickle ...')
    for gpx in gpxes:
        pick = gpx.replace('activities', 'tmp') + '.pickle'

        if not os.path.exists(pick):
            df = gpx2pickle(gpx, pick)
        else:
            df = pd.read_pickle(pick)

        logging.info(pick)
        drawPolyLines(osm, df)

    osm.save(options.output)
    logging.info(options.output)


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-d', '--activities-dir', dest='activities',
                      help='path to directory contains GPX activities', default='activities/*.gpx')
    parser.add_option('-c', '--line-color', dest='color',
                      help='specify PolyLine color', default='blue')
    parser.add_option('-a', '--line-alpha', dest='alpha',
                      help='specify PolyLine opcacity', default=1)
    parser.add_option('-w', '--line-weight', dest='weight',
                      help='specify PolyLine weight', default=2)
    parser.add_option('-z', '--zoom', dest='zoom',
                      help='specify map zoom level', default=9)
    parser.add_option('-o', '--output', dest='output',
                      help='path to HTML output', default='overlay.html')

    # tiles='Stamen Toner',
    # cartodbpositron
    parser.add_option('-t', '--tile', dest='tiles',
                      help='tile server', default='openstreetmap')

    def location_cb(option, opt_str, value, parser):
        setattr(parser.values, option.dest, value.split(','))

    parser.add_option('-l',
                      '--location',
                      action='callback',
                      dest='location',
                      help='central point (latitude, longitude) of the map',
                      type='string',
                      default=[35.8, 139.5], # Tokyo
                      callback=location_cb)

    options, args = parser.parse_args(sys.argv[1:])
    buildMap()
