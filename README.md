# chipotme

### Analytics for your chipotle consumption

This app was built over the course of a week to learn how to make reactive web dashboards using Dash. 

Features:
* reactive front end components
* reactive graphs
* extensive use of `pandas` for data munging and outputting graph values
* smart logging of Store Number search returns (unrecognized store numbers in user uploads will trigger a `GET` request to search jobs.chipotle.com for the store number and parse its location (couldn't find a better way). Each store will only have to be searched for once as it updates a local record upon discovery
* simple univariate linear regression trained in real time on provided data to generate a forecasting trend line
* Option to allow me to save transaction data for future population analysis
* All sorts of Dash and Plotly components

![output](https://i.imgur.com/lLkiTT3.png)
