# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create an engine to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reference the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session (link) from Python to the DB
session = Session(engine)

def get_db_session():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = get_db_session()
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()
    
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = get_db_session()
    results = session.query(Station.station).all()
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = get_db_session()
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()
    
    tobs_data = [{'date': date, 'temperature': tobs} for date, tobs in results]
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_summary(start, end=None):
    session = get_db_session()
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
    temp_summary = {
        'start_date': start,
        'end_date': end,
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }
    return jsonify(temp_summary)


if __name__ == "__main__":
    app.run(debug=True)
