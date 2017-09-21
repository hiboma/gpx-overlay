#!/usr/bin/env python3

import codecs
import glob
import logging
import os
import sys
from optparse import OptionParser

import json
import folium
import xml.sax, xml.sax.handler
import pandas as pd

from folium import plugins

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

def drawHeatMap(osm, df, style):
    locations = df.values.tolist()

    c = folium.plugins.HeatMap(locations,
                        radius=style['radius'],
                        blur=style['blur'],
                        gradient=style['gradient'],
                        min_opacity=0.5)
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

    records = pd.DataFrame([])
    for gpx in gpxes:
        pick = gpx.replace('activities', 'tmp') + '.pickle'

        if not os.path.exists(pick):
            df = gpx2pickle(gpx, pick)
        else:
            df = pd.read_pickle(pick)

        logging.info(pick)
        records = records.append(df)

    heatmap_style = {
        'radius': options.radius,
        'blur': options.blur,
        'gradient': options.gradient,
    }
    drawHeatMap(osm, records, heatmap_style)

    if options.tiles:
        logging.info(options.tiles)
        folium.TileLayer(options.tiles).add_to(osm)
    else:
        folium.TileLayer('cartodbdark_matter').add_to(osm)
        folium.TileLayer('cartodbpositron').add_to(osm)
        folium.TileLayer('openstreetmap').add_to(osm)

    folium.LayerControl().add_to(osm)
    osm.save(options.output)
    logging.info(options.output)

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-d', '--activities-dir', dest='activities',
                      help='path to directory contains GPX activities', default='activities/*.gpx')
    parser.add_option('-z', '--zoom', dest='zoom',
                      help='specify map zoom level', default=9)
    parser.add_option('-o', '--output', dest='output',
                      help='path to HTML output', default='heatmap.html')
    parser.add_option('-t', '--tile', dest='tiles',
                      help='tile server', default=False)
    parser.add_option('-b', '--blur', dest='blur',
                      help='specify heatmap blur', default=3)
    parser.add_option('-r', '--radius', dest='radius',
                      help='specify heatmap radius', default=4)

    def gradient_cb(option, opt_str, value, parser):
        setattr(parser.values, option.dest, json.loads(value))

    parser.add_option('-g',
                      '--gradient',
                      action='callback',
                      dest='gradient',
                      type='string',
                      help='specify heatmap color gradient',
                      default={0.4:"blue",0.65:"lime",1:"red"},
                      callback=gradient_cb)

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
