from src import jirascript as jira_importer
from src import splunkscript as splunk_importer
import configparser, argparse

########### Arguments ############
parser = argparse.ArgumentParser(description="Permet d'envoyer un rapport d'exécution de tests ainsi que ses captures d'écran dans Xray")
parser.add_argument("exporter", help="Clé du projet JIRA")
parser.add_argument("importer", help="Clé du plan de test JIRA")
parser.add_argument("-e","--epicKey", help="Clé du plan de test JIRA")
parser.add_argument('-d', '--debug', action='store_true',  help="shows output")
args = parser.parse_args()

if __name__ == "__main__":  # pragma: no cover
    config = configparser.ConfigParser()
    config.read('config.cfg')

    isJiraServer = "server" if args.exporter == "jira_server" else ""
    epicKey = args.epicKey if args.epicKey else ""

    jira_exporter = jira_importer.JiraExporter(config, isJiraServer ,epicKey)
    logs = jira_exporter.run()

    splunk_importer.export_log(logs,config)