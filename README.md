# collegescweb

## Description

The collegescweb repo contains two distinct projects:

* A RESTful web service that exposes resources from the College Scorecard database created in the [College Scorecard Visualizer](https://github.com/sacline/collegescvis) project. An API is defined that returns JSON data for college and data type resources. This web service is built with the Python microframework Flask.

* A web app to search for colleges that meet user-specified criteria. This uses the web service's API to generate a form where users can choose the specific data types to use in the search. Additional API calls are made during the search, and a list of results are displayed to the user in a table. The web app is built using [AngularJS](https://angularjs.org) with [Bootstrap](https://getbootstrap.com).

### Current features
* Fully functioning web service with REST API returning data for colleges and data types defined in the College Scorecard.

* Web client in which users can search for colleges based on multiple (less than, greater than, or equal to) criteria. Results are displayed in a table featuring the college name as well as the actual values of each category specified in the search.

### Future improvements
* Improve error messages on invalid API calls.

* Add sorting of results table by the different criteria.

* Add files to config for client and server config so the source does not have to be modified to update web addresses, etc.

## Requirements
* Python 3.4+
* Flask 0.12+
* Browser compatible with AngularJS 1.x and Bootstrap 3.x

Please let me know if you have any trouble running the program, as well as the version of the above packages you are using.

## How to run
* To run the web server, the database from [College Scorecard Visualizer](https://github.com/sacline/collegescvis) must be placed in the rest-server/data/database/ directory with a filename matching what is specified in server.py. Then running server.py will start up the web server locally.

* To run the web client, the web server must first be running. By default the server is expected to be running locally on http://localhost:5000. If it is running at another location, the API addresses in rest-client/cscexplorer.js must be updated to reflect the true location.
