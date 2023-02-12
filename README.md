This script is used to extract selection pool data into an Excel file

## **Install requirements**

To use this script you need to have python3 installed, to install the script requirements use this command `pip install -r requirements`

## **set variables:**

Before you run the script, you have to set certain variables in the `config.py` file

### **token**

You should generate the token from your gitea in the link `https://[center link]/git/user/settings/applications`

### **chool_link**

This is the center link, it should be full link `https://learn.example.com`

### **piscine_object_name**

This is the object associated with the targeted piscine events

## **run the script:**

Run the script using python3  `python3 data_extractor.py` . It will show you a list of events in this format.

```
0- id: 78
        start:2022-11-02T10:00:00.371122+00:00
        end:2022-11-27T22:00:00+00:00

1- id: 90
        start:2022-11-29T10:00:00.556994+00:00
        end:2022-12-23T18:30:00+00:00

2- id: 130
        start:2023-01-10T10:00:00.49146+00:00
        end:2023-02-04T18:00:00+00:00

what piscine index you want to get data from:

```

You have to enter the index of the desired piscine you want to extract data from. For example, you want to extract the data from the first piscine with the id 78 you have to enter the index 0

## **output**

Running the script will output an Excel file similar to this image

![image](./images/excel%20example%20output.jpg)
