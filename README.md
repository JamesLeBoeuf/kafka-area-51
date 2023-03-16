# Apache Kafka and Area 51

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://user-images.githubusercontent.com/7974277/224820642-a64a780e-c7d3-4dd5-a833-3eb64e6a831a.png">
    <img src="https://user-images.githubusercontent.com/7974277/224820642-a64a780e-c7d3-4dd5-a833-3eb64e6a831a.png" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">Kafka & Area 51</h3>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li>
          <a href="#built-with">Built With</a>
        </li>
        <ul>
          <li><a href="#iot-device">IoT Device</a></li>
          <li><a href="#backend-api">Backend API</a></li>
          <li><a href="#mysql">MySQL</a></li>
          <li><a href="#nifi">NiFi</a></li>
        </ul>
      </ul>
    </li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

I’m sure you are probably wondering what Area 51 has to do with Apache Kafka. To be honest, they share nothing in common, except using Apache Kafka to ‘spy’ on Area 51 airspace activity seemed pretty cool. So that’s the basis of this project. To utilize Kafka’s event-streaming platform to provide real-time updates of Area 51’s airspace.

I'd be very foolish to say that all we need is Kafka in this instance. I wish it were that simple. The architecture of this project involves quite a bit of moving parts and other technologies, but the main gist is below:

### Built With
<img width="1657" alt="Screenshot 2023-03-06 at 4 15 16 PM" src="https://user-images.githubusercontent.com/7974277/223253707-4ccf6faf-8d03-4068-bf56-f68466cd2533.png">

Let’s unpack each of the steps in the above diagram and see how it fits into the overall goal of spying on Area 51.

#### IoT Device
* Planes flying throughout the world are constantly sending and receiving data. This data consists of a whole plethora of information, but the most important data that we are worried about in this project is real-time location data (latitude & longitude).
* Accessing this information isn’t quite that difficult, the hard part is finding the best API to use, without having to spend any money.
* Luckily there is a great API called OpenSky Network.

#### Backend API
* OpenSky Network is <i>"a non-profit community-based receiver network which has been continuously collecting air traffic surveillance data since 2013."</i>
* OpenSky provides REST API endpoints for requesting data. The bit we are most interested in is the part about retrieving live airspace information with a bounding box. So if we take a look at one of their examples (i.e. request for bounding box covering Switzerland) ```https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226``` we notice that the result looks something like this...
```
{
    "time": 1678833474,
    "states": [
        [
            "4b1804",
            "SWR     ",
            "Switzerland",
            1678833461,
            1678833471,
            8.5633,
            47.4418,
            434.34,
            true,
            0,
            64.69,
            null,
            null,
            null,
            "2000",
            false,
            0
        ],
        [
            "4b1800",
            "SWR     ",
            "Switzerland",
            1678833468,
            1678833473,
            6.1101,
            46.2356,
            null,
            true,
            0,
            135,
            null,
            null,
            null,
            "2257",
            false,
            0
        ]
    ]
}
 ```
 * Well, the result from the request seems a bit vague but according to their <a href="https://openskynetwork.github.io/opensky-api/rest.html">REST API documentation</a>, it does provide Latitude and Longitude. The only hard part is keeping track of what each column value means, and this will prove to be a bit tricky during the NiFi section. 
 * So now the final step would be to alter the bounding box to center it over Area 51. The result I came up with by altering the lomin, lomax, lamin, lamax is ```https://opensky-network.org/api/states/all?lamin=36.522674&lomin=-117.102884&lamax=37.893228&lomax=-115.283535```. Obviously it's not exact, but it will do.
 * If we make a request, sometimes we will get ```null``` back as results, like so:
```
{
    "time": 1678755837,
    "states": null
}
```
* This is fine, it's just saying that their currently isn't any tracked aircraft flying above Area 51, at the moment.

#### MySQL
Before NiFi is setup, a MySQL database needs to be installed and configured with an additional layer called Debezium to handle CDC (Change Data Capture). In case you might be wondering, Debezium is going to allow us to convert MySQL database information into event streams to be used with Kafka. The formal definition is <i>"Debezium is a distributed platform that converts information from your existing databases into event streams, enabling applications to detect, and immediately respond to row-level changes in the databases."</i>

We're going to install MySQL with the help of Docker. The Docker container command for this is
```docker run -dit --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=debezium -e MYSQL_USER=mysqluser -e MYSQL_PASSWORD=mysqlpw debezium/example-mysql:1.6```
Basically in this command we are building a docker container, in detached & interactive mode with the name mysql, opening port 3306, setting environment mysql variables, from the debezium/example-mysql:1.6 image.

Now, we need to
* ```exec``` into the newly created ```mysql``` docker container using bash
  * ```docker exec -it mysql bash```
* Create a database
  * ```create database flights;```
  * ```use flights;```
* Create a new table.
  * Note that the column names, except for record_id, event_time, and primary key, created in this table are referenced at https://openskynetwork.github.io/opensky-api/rest.html
```
CREATE TABLE flight_status (
    record_id INT NOT NULL AUTO_INCREMENT,
    icao24 VARCHAR(40),
    callsign VARCHAR(40),
    origin_country VARCHAR(60),
    time_position INT,
    last_contact INT,
    longitude REAL,
    latitude REAL,
    baro_altitude VARCHAR(40),
    on_ground BOOLEAN,
    velocity VARCHAR(40),
    true_track REAL,
    vertical_rate VARCHAR(40),
    sensors VARCHAR(40),
    geo_altitude VARCHAR(40),
    squawk VARCHAR(40),
    spi BOOLEAN,
    position_source INT,
    category INT,
    event_time DATETIME DEFAULT NOW(),
    PRIMARY KEY (record_id)
);
```
Now it's time to setup NiFi.

#### NiFi
NiFi is one of the most important pieces in this complex puzzle. It's a drag and drop ETL orchestration tool that is typically used for long-running jobs (perfect for this as sometimes we need to wait for results). It's suitable for both batch and streaming data. Since we are utilising Kafka, which is a major event streaming platform, it makes sense to choose NiFi.

We're going to install NiFi with the help of Docker again. The Docker command for this is:
```docker run --name nifi -p 8080:8080 --link mysql:mysql -d apache/nifi:1.12.0```

Below is a screenshot of the multiple Processor flow of Nifi:

<img width="1680" alt="nifi_overview" src="https://user-images.githubusercontent.com/7974277/223303664-497c4424-16ce-42f6-abc4-b7e541c900af.png">

Step 1: InvokeHTTP
This first Process step is important, because it's where we are setting the Remote URL, basic request authentication information, and the scheduling of how often to make the request.

Step 2: JoltTransformJSON
This is a very handy Processor that NiFi comes with. It's basically going to allow us to transform the request from Step 1 into whatever new JSON structure that we are needing using the Jolt language. <a href="https://community.cloudera.com/t5/Community-Articles/Jolt-quick-reference-for-Nifi-Jolt-Processors/ta-p/244350">More information about NiFi Jolt Processor</a>.

Remember from earlier, the JSON from OpenSky looks like this... It's basically nested arrays with no idea what each value in each array means. Which is not great.
```
{
    "time": 1678833474,
    "states": [
        [
            "4b1804",
            "SWR     ",
            "Switzerland",
            1678833461,
            1678833471,
            8.5633,
            47.4418,
            434.34,
            true,
            0,
            64.69,
            null,
            null,
            null,
            "2000",
            false,
            0
        ],
        [
            "4b1800",
            "SWR     ",
            "Switzerland",
            1678833468,
            1678833473,
            6.1101,
            46.2356,
            null,
            true,
            0,
            135,
            null,
            null,
            null,
            "2257",
            false,
            0
        ]
    ]
}
 ```
We need to transform this request to include column names so it will make life easier when we are saving into the MySQL database.
Expected transformed output:
```
[
  {
    "icao24": "a57b26",
    "callsign": "N452SM  ",
    "origin_country": "United States",
    "time_position": 1675791621,
    "last_contact": 1675791621,
    "long": -105.1168,
    "lat": 39.9103,
    "baro_altitude": null,
    "on_ground": true,
    "velocity": 0,
    "true_track": 90,
    "vertical_rate": null,
    "sensors": null,
    "geo_altitude": null,
    "squawk": null,
    "spi": false,
    "position_source": 0
  },
  {...}
]
```
This is where the power of Jolt Transform happens. It's a bit hard to read but I solved this by doing the following:
```
[
  {
    "operation": "default",
    "spec": {
      "temp": [
        [
          "icao24",
          "callsign",
          "origin_country",
          "time_position",
          "last_contact",
          "long",
          "lat",
          "baro_altitude",
          "on_ground",
          "velocity",
          "true_track",
          "vertical_rate",
          "sensors",
          "geo_altitude",
          "squawk",
          "spi",
          "position_source"
        ]
      ]
    }
  },
  {
    "operation": "shift",
    "spec": {
      "temp": {
        "*": "states[]"
      },
      "states": {
        "*": "states[]"
      }
    }
  },
  {
    "operation": "shift",
    "spec": {
      "states": {
        "*": {
          "*": "[&1].@(2,[0].[&])"
        }
      }
    }
  },
  {
    "operation": "shift",
    "spec": {
      "0": null,
      "*": "[]"
    }
  }
]
```
The final transformation contains the necessary column names and removes the array nesting. Looks as follows:
```
[
  {
    "icao24": "a57b26",
    "callsign": "N452SM  ",
    "origin_country": "United States",
    "time_position": 1675791621,
    "last_contact": 1675791621,
    "long": -105.1168,
    "lat": 39.9103,
    "baro_altitude": null,
    "on_ground": true,
    "velocity": 0,
    "true_track": 90,
    "vertical_rate": null,
    "sensors": null,
    "geo_altitude": null,
    "squawk": null,
    "spi": false,
    "position_source": 0
  },
  {...}
]
```
Now it's ready to save into the MySQL database.
