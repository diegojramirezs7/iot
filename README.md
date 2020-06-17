The purpose of this system is to improve the current method used by researches to study rodent populations. 
It automates the process of data collection by using a variety of sensors. 

The system consists of a harware unit stored within a 12-inch PVC pipe which contains an Arduino and Raspberry Pi along with different sensors and a camera to gather all the required data. 

It can gather both environmental data such as temperature, light intensity and humidity and data about the animals themselves such as weight and a set of pictures showing different angles, which would also show its length. Environmental data is gathered every 5 minutes. For gathering data of the animal, we set up a weight scale in the unit. 

A significant change in weight would trigger the system to start taking pictures and calculate the average weight sampled within a 5 second period. All the data is saved in a csv file for easy analysis.