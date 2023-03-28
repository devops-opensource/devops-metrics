from src.transformer.transformer import Transformer
from src.transformer.transform_release_management import TransformReleaseManagement
from src.transformer.transform_status_change import TransformStatusChanges

class ProjectManagementTransformer(Transformer):

    def initialize_data(self, config):
        self.config = config

    def transform_data(self, config, adapted_data):
        df_release_management = TransformReleaseManagement.transform_release_management(
            adapted_data["versions"])
        status_changes_transformer = TransformStatusChanges(
            self.config, df_release_management
        )
        df_status_changes = status_changes_transformer.transform_status_changes(
            adapted_data["status_changes"]
        )
        df_dict = {
            "status_changes": df_status_changes,
            "releases": df_release_management,
        }
        return df_dict
        