# Gologic-DevOpsMetrics
The current verison of the script gather logs from a Jira Instance and store it into a csv file. For now, we only store logs about ticket status changes.

# Usage 
You need the `requests` module in order to run the script. Use `pip install requests` to install the module. <br />
To run the script use the following commande: <br />
`python3 -p <projectkey> -o <outputfile>`

The project key is the 3 letters associated to a Jira Project. <br />
The output file will be a csv file, you have to specify the extension manually.

# Config file

Rename config.default.cfg in config.cfg and fill it with your parameters.
