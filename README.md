# DevOps-Metrics
This project aim at providing maximum flexibility for **aggregating data from multiple source in a single target to calculate metrics related to DevOps**. The vision of this project is to **break silos between those systems** and enable cross-platform metrics to get an overview of the whole development process.

We are using a traditional ETL process to extract data from the source, transform it and load it into a target. There is multiple source and targets supported. With the transformer, we make sure to transform the data no matter the source to the same target format.

## Extractors

### Jira Cloud 
The Jira Cloud extractor connects to your Jira instance via the REST API to extract data for DevOps metrics analysis. It requires a Jira Cloud URL, user email, and API token for authentication.

#### Data Extracted
The extractor pulls two primary datasets:

1. **Pivot Data** - Configurable to extract either:
   - **Versions (Releases)**: Captures release data including release dates, names, and descriptions
   - **Epics**: Gathers epic-level information including creation dates, resolution dates, and status

2. **Status Changes** - Tracks the complete workflow history of issues:
   - Captures all status transitions for stories
   - Records timestamps for each transition
   - Links issues to their parent epics
   - Associates issues with fix versions

### Repository Management (GitHub and GitLab)
Both GitHub and GitLab extractors connect to repositories via REST APIs to extract pull request/merge request data for comprehensive DevOps metrics analysis.

#### GitHub Data Extracted
The GitHub extractor requires a GitHub URL, username, organization name, repository list, and authentication token and pulls three primary datasets:

1. **Pull Requests** - Captures detailed information about closed pull requests:
   - Pull request metadata (title, description, creation date)
   - Merge status and timestamps
   - Author information
   - Branch details

2. **Commits** - Collects all commits associated with pull requests:
   - Commit messages and timestamps
   - Author and committer information
   - Code changes metadata
   - Links to parent pull requests

3. **Reviews** - Gathers code review data for pull requests:
   - Review comments and feedback
   - Review state (approved, changes requested, etc.)
   - Reviewer information
   - Review timestamps

#### GitLab Data Extracted
The GitLab extractor requires a GitLab URL, username, organization name, repository list, and authentication token and pulls three similar datasets:

1. **Merge Requests** - Captures detailed information about merged merge requests:
   - Merge request metadata (title, description, creation date)
   - Merge status and timestamps
   - Author information
   - Branch details

2. **Commits** - Collects all commits associated with merge requests:
   - Commit messages and timestamps
   - Author information
   - Code changes metadata
   - Links to parent merge requests

3. **Reviews** - Gathers approval data for merge requests:
   - Approval notes and feedback
   - Reviewer information
   - Review timestamps
   - Only captures notes containing "approved"

### GitHub Copilot
The GitHub Copilot extractor connects to your GitHub organization via the REST API to extract Copilot usage data for detailed AI pair programming metrics analysis. It requires a GitHub URL, organization name, and authentication token.

#### Data Extracted
The extractor pulls three primary datasets:

1. **Team-specific Metrics** - Captures Copilot usage data for each team in the organization:
   - Chat interactions with Copilot
   - Code completion acceptance rates
   - Language-specific usage patterns
   - Editor-specific utilization

2. **Organization-wide Metrics** - Collects aggregated Copilot metrics across the organization:
   - Active and engaged users
   - Chat usage statistics across different editors and models
   - Code completion statistics including lines suggested and accepted
   - Language-specific performance metrics

3. **Billing Information** - Gathers seat utilization and subscription data:
   - Total seats allocated
   - Active and inactive seats
   - New seats added in current billing cycle
   - Utilization rates

## Transformations
The transformers standardize data from any source into consistent formats to enable uniform metrics calculation regardless of origin platform:

### Project Management Data Transformation
- **Release Management Metrics**: Transforms release data into standardized formats enabling:
  - Deployment frequency analysis
  - Release cycle time calculations
  - Version tracking and comparison

- **Status Change Metrics**: Transforms work item transitions to measure:
  - Lead time (time from creation to deployment)
  - Cycle time (time from development start to deployment)
  - Value stream mapping (time spent in each workflow state)
  - Release tracking (work items in specific releases)

### Version Control Data Transformation
- **Code Change Metrics**: Standardized metrics regardless of version control system:
  - Pull/merge request lifecycle metrics
  - Time to complete code reviews
  - Code change frequency and distribution
  - Development flow efficiency
  
- **Review Activity Metrics**: Unified metrics for code review processes:
  - Review response times
  - Approval cycles and reviewer engagement
  - Team collaboration patterns
  - Code quality indicators

### AI-Assisted Development Transformation
- **User Adoption Metrics**: Tracks usage patterns of AI-assisted tools:
  - Active and engaged users over time
  - Resource utilization statistics

- **Interaction Metrics**: Measures effectiveness of AI interactions:
  - AI chat activity and acceptance rates
  - Language-specific AI assistance patterns
  - Team and organization-level usage comparison

- **Productivity Metrics**: Quantifies productivity impact:
  - Code suggestion acceptance rates
  - Developer efficiency gains
  - Cost-effectiveness analysis

These transformations abstract away the differences between source systems, creating uniform metrics that enable cross-platform analysis regardless of the tools used in your development process.

### Loader

# Installation(Linux environment)
## Create a virtual environment
``` bash
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate
```

You should see in your terminal (.env) from the moment you use the command source

## Install dependencies in your virtual environmment
``` bash
python3 -m pip install -r  requirements/dev_requirements.txt
git submodule update --init
python3 -m pip install _submodules/splunk
```

# Execute the script
## Fill the configuration file
Rename config.default.cfg in config.cfg and fill it with your configurations. 
The config.local.cfg provide an example with a configuration for jira cloud and mysql.

## Usage 
To run the script use the following command:

```bash
python3 main.py config_file_path.cfg Exporter Loader
```

Where:
- `config_file_path.cfg` - Path to your configuration file
- `Exporter` - Type of exporter to use (e.g., GitHub, Jira, GitLab, GitHubCopilot)
- `Loader` - Type of loader to use (e.g., CSV, MYSQL)

Example usage:
```bash
python3 main.py config.cfg GitHub MYSQL
python3 main.py config.local.cfg Jira CSV
```

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
## Sign in to Grafana
Then, in a browser window, open the following url localhost:3000 and use the following credentials:
- username: admin 
- password: admin

You will be redirected to the DevOps Metrics dashboard.

The dashboard has two parts. The first part contains global metrics based on a mean of the different version contained in the data. The second part contains the detail for each different version of the dataset.
![complete](/docs/images/demo-6-grafana-complete.png)

Have fun playing with the data!

