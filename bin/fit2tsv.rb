#!/usr/bin/env ruby

require 'time'
require 'fit'

path = ARGV[0]

warn "reading: #{path}"
fit_file = Fit.load_file(path)
records  = fit_file.records.select{ |r| r.content.record_type != :definition }.map{ |r| r.content }

record    = records.find { |r| r[:raw_timestamp] }
timestmap = Time.new(1989, 12, 31, 0, 0, 0) + record[:raw_timestamp].to_i
date      = Time.at(timestmap).strftime("%Y-%m-%d-%H:%M:00")

output = File.dirname(path) + "/" + date + ".tsv"
warn "writing: #{output}"

File.open(output, "w") { |io|
  records.map { |r|
    lon = r[:raw_position_long]
    lat = r[:raw_position_lat]

    if lon && lat
      lon = lon * 180.0 / 2 ** 31
      lat = lat * 180.0 / 2 ** 31
      io.printf "%s\t%s\n", lat, lon
    end
  }
}
