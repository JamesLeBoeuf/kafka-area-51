# Apache NiFi

Apache NiFi is used to extract data from the OpenSkyNetwork API and send it to the MySQL database, to be used for further consumption. Apache NiFi is used as it is highly scalable, drag and drop engineering orchestration tool that can be considered a 'swiss army knife' for big data integration. It can consume and send data bidirectionally in batches or streams to numerous data sources.

NiFi is deployed via Amazon AWS EC2:
* t2.large
* Storage: 100-200gb
* Image: Amazon Linux

## Install Docker, MySQL - Debezium (CDC)
Before we deploy Apache NiFi we need to set up a MySQL database with an extra layer called Debezium for CDC.

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
* When MySQL starts running, we need to exec into the MySQL container and create a new database with a new table. The data from OpenSky Flight API will be stored in the MySQL table by using Nifi. This process mimics real business scenario when data in SQL database constantly gets updated and we need to capture this data for further downstream processes. When you log into MySQL you would need to enter the password you defined in docker run command (debezium).
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
* Check docker logs of nifi container to verify completion and diagnose any potential errors
  * ```docker logs -f nifi```
  * Ctrl-C to exit out of logs
* Configure security group in AWS ec2 instance to allow for all traffic from local IP address
  * Add this rule 
    * Type: All Traffic
    * Source: My IP
    * xx.xxx.xx.xxx/32
    * Save rules
* Copy public DNS from AWS
  * Go to web browser and connect to nifi running on ec2 instance
  * ```http://ec2-xxx-xxx-xxx-xxx.compute-1.amazonaws.com:8080/nifi```

### Adding NiFi Processors & JDBC jar
All of the NiFi processors and that were used are available via the NiFi template that I have included (flight_status.xml). The image below shows the connected processors along with any LogAttributes.

Note: A JDBC jar will need to be installed.
* ```docker exec -it nifi bash```
* ```mkdir custom-jars```
* ```cd custom-jars```
* ```wget http://java2s.com/Code/JarDownload/mysql/mysql-connector-java-5.1.17-bin.jar.zip```
* ```unzip mysql-connector-java-5.1.17-bin.jar.zip```
* So the final location of your jar file will be...
  * ```/opt/nifi/nifi-current/custom-jars/mysql-connector-java-5.1.17-bin.jar```
* Enter jar location into NiFi ConvertJSONtoSQL processor - JDBC Connection Pool
* Activate Connection

More information coming...

<img width="1680" alt="nifi_overview" src="https://user-images.githubusercontent.com/7974277/223303664-497c4424-16ce-42f6-abc4-b7e541c900af.png">
