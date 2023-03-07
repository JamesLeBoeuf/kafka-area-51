# NIFI Readme

Below is an overview of the flow of Nifi.

STEPS:
1. GET Request to API endpoint
2. Transform response
3. Convert JSON to SQL
4. PutSQL via DBCPConnectionPool

Also inside this folder is the template xml file (flight_status.xml) that you in the image below, which you can use in Nifi.

<img width="1680" alt="nifi_overview" src="https://user-images.githubusercontent.com/7974277/223303664-497c4424-16ce-42f6-abc4-b7e541c900af.png">
