import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckanext.clamdscanner import helpers


class ClamdscannerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, 'templates')
        tk.add_resource('fanstatic', 'scanner')


    def get_helpers(self):
        return {
                    'file_scan': helpers.file_scan,
                    'test': helpers.test,
                }


    def get_actions(self):
        return {
            'scan': helpers.file_scan,
        }


    def before_map(self, map):
        map.connect('scan', '/scan/{id}',
            controller="ckanext.clamdscanner.controller:ScanController",
            action="scan")

        return map
