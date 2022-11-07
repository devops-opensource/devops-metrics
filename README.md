# DevOps-Metrics
This project aim at providing maximum flexibility for aggregating data from multiple source in a single target to calculate 
metrics related to DevOps. The vision of this project is to break silos between those systems and enable cross-platform metrics to get an overview of the whole development process.

The repository contains actually extractor from jira on-premise and jira cloud. The actual targets are mysql and also Splunk. 

We are working on a new extractor(GitHub) and we will provide at the same time a flexible architecture that will allow the community to create new extractors and targets.

## Data models
### Release management
This type of data is intended to calculate the frequency of release. 
```json 
{
  name: string
  release_date: string
	description: string 
	start_date: timestamp
	event_type: string 
	project_key: string
	control_date: timestamp 
}
```

### Status change
Status change contains the history of transitions between status in project management systems. 
There is two status created by the tool:
- A status when the item is created in the backlog
- A status when the item is published( Trigger is publication of a version)

Those data can be used to measure lead time, cycle time and metrics around value streams.

```json 
{
  from_status: string
  to_status: string
  key: string
  to_date: timestamp
	issue_type: string
	project_key: string
	parent_key: string 
	version: string
	from_date: timestamp
	event_type: string
	release_version: string
	control_date: timestamp
}
```
# Contributing (Coming soon)

# Dependencies
| Name                                                 | Version  |
|------------------------------------------------------|----------|
| Python                                               | 3.10     |
| requests                                             | 3.10     |
| pandas                                               | 1.4.42   |
| mysql                                                | 0.0.3    |

# Local demo with docker-compose (Tested in a linux environment)
## context
The repository contains a docker-compose that will create a mariadb instance,
a grafana instance, a adminer instance and also run the tools with the config.local.cfg
configuration file.

This will populate the database with data from the DAOS jira, a open-source project maintained by dell.
Here the steps to connect the database to grafana and add a simple example dashboard to vizualize the data.

## Login to Jira
To access the data from the DAOS jira, you need to associate your Attlassian account with the instance. You can ether create 
a new account or link your existing account

We then need to create a token in the jira instance of DAOS to connect from the api. Here some documentation 
that explain how to create a token: https://www.testingdocs.com/create-jira-api-token/

You will finally add in the config.local.cfg file at the root of the repository your email address and the token created.

## Create our local environment (Linux)
Run the following command and wait for about 15 seconds: 

```bash
docker-compose up -d 
```
## Configure grafana
Then, in a browser window, open the following url localhost:3000 and use the following credentials:
- username: admin 
- password: admin

The first step is to link our database as a data source in grafana. To do so open the menu in the screenshot below:
![data-source](/docs/images/demo-1-grafana-data-source.png)

Then you need to choose mysql as type: 

![data-source](/docs/images/demo-2-grafana-type.png)

To finalize the connection, you need to enter the connection information as following and click on the **Save & Test** button below: 
![data-source](/docs/images/demo-3-grafana-connection.png)
* The password is: example

The second part consist to import a dashboard that give your a sneakpeek of what you can measure with the data. Start by
opening the import menu as following: 
![import](/docs/images/demo-4-grafana-import-menu.png)

Choose upload json and import the following file 'dashboards/grafana-sql.json' as below:
![dashboard](/docs/images/demo-5-granafa-dashboard.png)

**Make sure to choose the datasource created previously before saving**

The dashboard has two parts. The first part contains global metrics based on a mean of the different version contained in the data. The second part contains the detail for each different version of the dataset.
![complete](/docs/images/demo-6-grafana-complete.png)

Have fun playing with the data!

# Installation(Linux environment)
## Create a virtual environment
``` bash
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate
```

You should see in your terminal (.env) from the moment you use the command source

## Install dependencies in your virtuel environmment
``` bash
python3 -m pip install -r  requirements/dev_requirements.txt
git submodules update --init
python3 -m pip install _submodules/splunk
```
# Execute the script
## Fill the configuration file
Rename config.default.cfg in config.cfg and fill it with your configurations. 
The config.local.cfg provide an example with a configuration for jira cloud and mysql.

## Usage 
To run the script use the following command and replace config_file_path with the path to the configuration file:

```bash
python3 main.py config_file_path.cgf
```

