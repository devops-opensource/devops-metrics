# Gologic-DevOpsMetrics
```mermaid
GRPAH classdiagram;
TicketChangeLog <|-- AveryLongClass : Cool
TicketChangeLog : int id
```

# Usage 
Use `python -m pip install requests` to install the module. <br />
To run the script use the following command: <br />
`python3 -p <projectkey> -t <outputtype> -o <outputfile>` <br />
The output type can be `csv` for a csv file or `json` for a json file. <br />
If you are using Jira Server and not Jira Cloud, use the `-s` or `--server` option.

The project key is the 3 letters associated to a Jira Project. <br />
The output file will be a csv file.

# Config file

Rename config.default.cfg in config.cfg and fill it with your configurations.
