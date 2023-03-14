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
    "time": 1678745539,
    "states": [
        [
            "4b1804",
            "SWR890M ",
            "Switzerland",
            1678745434,
            1678745510,
            8.5649,
            47.442,
            null,
            true,
            0.06,
            143.44,
            null,
            null,
            null,
            "2000",
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

#### NiFi
NiFi is one of the most important pieces in this complex puzzle. It's a drag and drop ETL orchestration tool that is typically used for long-running jobs (perfect for this as sometimes we need to wait for results). It's suitable for both batch and streaming data. Since we are utilising Kafka, which is a major event streaming platform, it makes sense to choose NiFi.

