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
          <li><a href="#kafka">Kafka</a></li>
          <li><a href="#spark-streaming">Spark Streaming</a></li>
          <li><a href="#hudi-table">Hudi Table</a></li>
        </ul>
      </ul>
    </li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

I’m sure you are probably wondering what Area 51 has to do with Apache Kafka. To be honest, they share nothing in common, except using Apache Kafka to ‘spy’ on Area 51 airspace activity seemed pretty cool. So that’s the basis of this project. To utilize Kafka’s event-streaming platform to provide real-time updates of Area 51’s airspace.

I'd be very foolish to say that all that was needed is Kafka in this instance. I wish it were that simple. The architecture of this project involves quite a bit of moving parts and other technologies, but the main gist is below:

### Built With
<img width="1657" alt="Screenshot 2023-03-06 at 4 15 16 PM" src="https://user-images.githubusercontent.com/7974277/223253707-4ccf6faf-8d03-4068-bf56-f68466cd2533.png">

Let’s unpack each of the steps in the above diagram and see how it fits into the overall goal of spying on Area 51.

#### IoT Device
* Planes flying throughout the world are constantly sending and receiving data. This data consists of a whole plethora of information, but the most important data concerning this project is real-time location data (latitude & longitude).
* Accessing this information isn’t quite that difficult, the hard part is finding the best API to use, without having to spend any money.
* Luckily there is a great API called OpenSky Network.

#### Backend API
* OpenSky Network is <i>"a non-profit community-based receiver network which has been continuously collecting air traffic surveillance data since 2013."</i>
* OpenSky provides REST API endpoints for requesting data. The bit that is most interesting in is the part about retrieving live airspace information with a bounding box. So taking a look at one of their examples (i.e. request for bounding box covering Switzerland) ```https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226``` it's noticable that the result looks something like this...
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
 * In the request, sometimes it will contain ```null``` as a result, like so:
```
{
    "time": 1678755837,
    "states": null
}
```
* This is fine, it's just saying that their currently isn't any tracked aircraft flying above Area 51, at the moment.

#### MySQL
Before NiFi is setup, a MySQL database needs to be installed and configured with an additional layer called Debezium to handle CDC (Change Data Capture). In case you might be wondering, Debezium is going to convert MySQL database information into event streams to be used with Kafka. The formal definition is <i>"Debezium is a distributed platform that turns your existing databases into event streams, so applications can quickly react to each row-level change in the databases. Debezium is built on top of Kafka and provides Kafka Connect compatible connectors that monitor specific database management systems. Debezium records the history of data changes in Kafka logs, so your application can be stopped and restarted at any time and can easily consume all of the events it missed while it was not running, ensuring that all events are processed correctly and completely."</i>

#### NiFi
NiFi is one of the most important pieces in this complex puzzle. It's a drag and drop ETL orchestration tool that is typically used for long-running jobs (perfect for this as sometimes results take time). It's suitable for both batch and streaming data. Since Kafka is being utilized, which is a major event streaming platform, it makes sense to choose NiFi.

Below is a screenshot of the multiple Processor flow of Nifi:

<img width="1680" alt="nifi_overview" src="https://user-images.githubusercontent.com/7974277/223303664-497c4424-16ce-42f6-abc4-b7e541c900af.png">

Step 1: InvokeHTTP
This first Process step is important, because it's setting the Remote URL, basic request authentication information, and the scheduling of how often to make the request.

Step 2: JoltTransformJSON
This is a very handy Processor that NiFi comes with. It's basically going to allow to transform the request from Step 1 into whatever new JSON structure that's needed using the Jolt language. <a href="https://community.cloudera.com/t5/Community-Articles/Jolt-quick-reference-for-Nifi-Jolt-Processors/ta-p/244350">More information about NiFi Jolt Processor</a>.

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
It's important to transform this request to include column names so it will make life easier when saving it into the MySQL database.
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

Step 3: ConvertJSONToSQL. This processor is going to allow us to communicate with the MySQL database, convert our JSON response from step 2 to SQL, and process SQL statements. In order to achieve this, JDBC pool connection needs to be set up.

Step 4: PutSQL. This is where NiFi executes a SQL INSERT command. The most important part of this Processor is setting the correct DB connection, which is the DBCPConnectionPool that was configured in Step 3.

The flow of these 4 steps are all connected to LogAttributes so that they can be used for logging and debugging purposes.

#### Kafka
Since Area 51's airspace will always have activity, it makes sense to look at this as an inifite amount of data being handled and processed. Another way to look at this infinite amount of data being recorded spread out over time, is a stream of data. The stream of flight data keeps arriving, so a tool is needed to handle this. So it makes sense to choose a data-streaming tool like Kafka.

I opted to configure this section to connect with Amazon MSK. In case you are wondering, <i>"Amazon MSK allows you to use open-source versions of Apache Kafka while the service manages the setup, provisioning, AWS integrations, and on-going maintenance of Apache Kafka clusters."</i> This will allow for more robust durability and handle a lot of the overhead that Kafka tends to have.

#### Spark Streaming
An Amazon EMR (Elastic Map Reduce) cluster was created here to handle the data-stream processing. It utilizes two main files located in https://github.com/JamesLeBoeuf/wcd_de_final/tree/main/pyspark. Both the spark-submit shell script and the python file that sits in an s3 bucket are used when a new flight record is recieved by EMR.

#### Hudi Table
