# Gologic-DevOpsMetrics

```mermaid
classDiagram
  class TicketChangeLog
  TicketChangeLog : String TimeStamp
  TicketChangeLog : int Id
  TicketChangeLog : String Key
  TicketChangeLog : int ProjectId
  TicketChangeLog : String ProjectKey
  TicketChangeLog : int ParentId
  TicketChangeLog : String ParentKey
  TicketChangeLog : int IssuetypeId
  TicketChangeLog : String IssuetypeName
  TicketChangeLog : int StatusId
  TicketChangeLog : String StatusName
  TicketChangeLog : int TicketPoint
  class TestCase
  TestCase : int Id
  TestCase : String Key
  TestCase : String Category
  TestCase : String Type
  class TestExecution
  TestExecution : int Id
  TestExecution : String Key
  TestExecution : String TestCaseKey
  TestExecution : double ExecutionTime
```
The goal of this project is to provide script collecting data 
# Config file

Rename config.default.cfg in config.cfg and fill it with your configurations.

# Usage 
Use `python -m pip install requests` to install the module. <br />
To run the script use the following command: <br />
`python3 -p <projectkey> -t <outputtype> -o <outputfile>` <br />
The output type can be `csv` for a csv file or `json` for a json file. <br />
If you are using Jira Server and not Jira Cloud, use the `-s` or `--server` option.

The project key is the 3 letters associated to a Jira Project. <br />
The output file will be a csv file.


