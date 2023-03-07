# Apache NiFi

Apache NiFi is used to extract data from the OpenSkyNetwork API and send it to the MySQL database, to be used for further consumption. Apache NiFi is used as it is highly scalable, drag and drop engineering orchestration tool that can be considered a 'swiss army knife' for big data integration. It can consume and send data bidirectionally in batches or streams to numerous data sources.

NiFi is deployed via Amazon AWS EC2:
* t2.large
* Storage: 100-200gb
* Image: Amazon Linux

## Install Docker, MySQL, create MySQL database and table
* SSH into EC2
  * ```ssh -i ~/.ssh/your-pem-key.pem ec2-user@'<your_EC2_external_IP>'```
* Update linux and install docker
  * ```sudo yum update -y```
  * ```sudo yum install docker -y```
  * ```sudo service docker start```
  * ```sudo systemctl enable docker```
  * ```sudo usermod -aG docker ec2-user```
* Restart / reboot instance
* Test docker is running without having to run sudo command. Verifies that ec2-user has permissions 
  * ```docker ps -a```
* Install MySQL
  * ```docker run -dit --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=debezium -e MYSQL_USER=mysqluser -e MYSQL_PASSWORD=mysqlpw debezium/example-mysql:1.6```
* Log into mysql instance 
  * ```docker exec -it mysql bash```
  * ```mysql -u root -p```
  * Enter password: ```debezium```
* Create database inside mysql bash
  * ```create database demo;```
  * ```use demo;```
* Create table
  * ```CREATE TABLE flight_status (```
    * ```record_id INT NOT NULL AUTO_INCREMENT,```
    * ```icao24 VARCHAR(40),```
    * ```callsign VARCHAR(40),```
    * ```origin_country VARCHAR(60),```
    * ```time_position INT,```
    * ```last_contact INT,```
    * ```longitude REAL,```
    * ```latitude REAL,```
    * ```baro_altitude VARCHAR(40),```
    * ```on_ground BOOLEAN,```
    * ```velocity VARCHAR(40),```
    * ```true_track REAL,```
    * ```vertical_rate VARCHAR(40),```
    * ```sensors VARCHAR(40),```
    * ```geo_altitude VARCHAR(40),```
    * ```squawk VARCHAR(40),```
    * ```spi BOOLEAN,```
    * ```position_source INT,```
    * ```category INT,```
    * ```event_time DATETIME DEFAULT NOW(),```
    * ```PRIMARY KEY (record_id)```
  * ```);```
* Exit out of mysql, back to ec2 linux cli
  
  
## Setup NiFi
* Run NiFi Docker image
  * ```docker run --name nifi -p 8080:8080 --link mysql:mysql -d apache/nifi:1.12.0```
* Check docker logs of nifi container
  * ```docker logs -f <nifi_docker_container_id>```





STEPS:
1. GET Request to API endpoint
2. Transform response
3. Convert JSON to SQL
4. PutSQL via DBCPConnectionPool

Also inside this folder is the template xml file (flight_status.xml) that you in the image below, which you can use in Nifi.

<img width="1680" alt="nifi_overview" src="https://user-images.githubusercontent.com/7974277/223303664-497c4424-16ce-42f6-abc4-b7e541c900af.png">
