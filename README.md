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
          <a href="#iot-device">IoT Device</a>
        </ul>
      </ul>
    </li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

I’m sure you are probably wondering what Area 51 has to do with Apache Kafka. To be honest, they share nothing in common, except using Apache Kafka to ‘spy’ on Area 51 airspace activity seemed pretty cool. So that’s the basis of this project. To utilize Kafka’s event-streaming platform to provide real-time updates of Area 51’s airspace.

### Built With
The architecture of this project involves quite a bit of moving parts and other technologies, but the main gist is as follows:

<img width="1657" alt="Screenshot 2023-03-06 at 4 15 16 PM" src="https://user-images.githubusercontent.com/7974277/223253707-4ccf6faf-8d03-4068-bf56-f68466cd2533.png">

Let’s unpack each of the steps in the above diagram and see how it fits into the overall goal of spying on Area 51.

#### IoT Device
* Planes flying throughout the world are constantly sending and receiving data. This data consists of a whole plethora of information, but the most important data that we are worried about in this project is real-time location data (latitude & longitude).

