import ckan.lib.base as base
import ckan.lib.helpers as h
from ckan.common import request, c
from ckanext.clamdscanner import helpers
from ckan.controllers.package import PackageController
import ckan.lib.navl.dictization_functions as dict_fns


import ckan.model as model
import ckan.logic as logic

redirect = base.redirect
clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params


class ScanController(PackageController):
    def scan(self, id, data=None, errors=None, error_summary=None):
        """
            Intermediary action between pressing "submit" and the submission
            happening. Send the file to be scanned. Then if the file is OK,
            The process continues as previously, otherwise alert the user
            about the file not passing the scan.

            TODO:
                * Implement scan here
                * How to connect this back the HTML page for the async modal?
                * something else?
        """

        data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
        # we don't want to include save as it is part of the form
        del data['save']
        resource_id = data['id']
        del data['id']

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        r = helpers.file_scan(data['upload'])

        clean = r[0]
        cause = r[1]

        # After scan go back to old process for new resources
        if clean:
            self.new_resource(id, data, errors, error_summary)
        else:
            h.flash_error("Scan failed. Cause '{}'".format(cause))
            redirect(h.url_for(controller='package',
                               action='new_resource',
                               id=id))


