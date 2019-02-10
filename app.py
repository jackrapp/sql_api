# Dependencies
from flask import Flask, jsonify
from datetime import datetime
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# Use this code instead, API causes issues with just one session
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)


#################################################
# Flask Set-up and Routes
#################################################

app = Flask(__name__)

# Home Page
# List all routes that are available.
@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Vacation API!<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"Precipitation data for one year: /api/v1.0/precipitation<br/>"
        f"Observed temperature for one year: /api/v1.0/tobs<br/>"
        f"Vacation temperature ranges: /api/v1.0/<start> or /api/v1.0/<start>/<end>"
    )


# Precipitation data for one year
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Precipitation query
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-23').all()

    # Loop through precip and convert to dicts
    rainfall = []
    for item in query:
        rain_dict = {}
        rain_dict["date"] = item.date
        rain_dict["precipitation"] = item.prcp
        rainfall.append(rain_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(rainfall)


# List of weather stations
@app.route("/api/v1.0/stations")
def stations():
    # Station query
    query = session.query(Station.id, Station.station, Station.name).all()

    # Loop through stations and convert to dicts
    station = []
    for item in query:
        station_dict = {}
        station_dict["id"] = item.id
        station_dict["station"] = item.station
        station_dict['name'] = item.name
        station.append(station_dict)
   
    # Return a JSON list of stations from the dataset.
    return jsonify(station)

# Temperature data for one year
@app.route("/api/v1.0/tobs")
def temperature():
    # query for the dates and temperature observations from a year from the last data point. selected station
    most = session.query(Measurement.station, func.count(Measurement.date).label('count')).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).first()

    query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most.station, Measurement.date>'2016-08-23').all()
    
    # Loop through temps and convert to dicts
    temp = []
    for item in query:
        temp_dict = {}
        temp_dict["date"] = item.date
        temp_dict["temperature"] = item.tobs
        temp.append(temp_dict)
    
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(temp)


# Vacation temperature data
@app.route("/api/v1.0/<start>")
def long_vacation(start):
    try:
        # Test date format
        start = datetime.strptime(str(start), '%Y-%m-%d').strftime('%Y-%m-%d')
        # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

        long_temps = {}
        long_temps['TMIN'] = query[0][0]
        long_temps['TAVG'] = query[0][1]
        long_temps['TMAX'] = query[0][2]

        # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        return jsonify(long_temps)

    except:
        ValueError
        print("Please input dates in format YYYY-MM-DD")

@app.route("/api/v1.0/<start>/<end>")
def vacation(start, end):
    try:
        # Test date format
        start = datetime.strptime(str(start), '%Y-%m-%d').strftime('%Y-%m-%d')
        end = datetime.strptime(str(end), '%Y-%m-%d').strftime('%Y-%m-%d')
        
        # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
        query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        vac_temps = {}
        vac_temps['TMIN'] = query[0][0]
        vac_temps['TAVG'] = query[0][1]
        vac_temps['TMAX'] = query[0][2]
        
        # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        return jsonify(vac_temps)

    except:
        ValueError
        print("Please input dates in format YYYY-MM-DD")


if __name__ == '__main__':
    app.run(debug=True)
