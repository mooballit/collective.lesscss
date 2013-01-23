import os
import tempfile
import subprocess
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.resource.interfaces import IResourceDirectory
from zope.component import getUtility
from plone.memoize import ram
import logging
import re


def path_diff( frompath, topath ):
    '''
        Returns the relative path to get from frompath to topath
        ie. 
        path_diff( '/home/user/some/dir', '/home/user/some_other/dir' )
        returns '../../some_other/dir'
    '''
    frompath = frompath.split( os.sep )
    topath = topath.split( os.sep )
    
    for i, pathi in enumerate( frompath ):
        if pathi != topath[ i ]:
            break
    
    return os.path.join( *( [ '..' ] * len( frompath[ i: ] ) + topath[ i: ] ) )

def render_cachekey(method, self, lessc_command_line, resource_path, resource_file_name):
    """Cache by resource_path and resource_file_name"""
    return (resource_path, resource_file_name)


class compiledCSSView(BrowserView):
    """ View for server-side compiling of the LESS resources in portal_less
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('collective.lesscss')

    def __call__(self):
        portal_less = getToolByName(self.context, 'portal_less')
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        if not os.path.exists(lessc_command_line):
            self.logger.error("A valid lessc executable cannot be found."
                         "We are assumming that it has been provided by buildout"
                         "and placed in the buildout bin directory."
                         "If not, you should provide one (e.g. symbolic link) and place it there.")

        less_resources = portal_less.getEvaluatedResources(self.context)
        regex = r'^(\+\+[\w_-]+\+\+[\w_-]+)\/(.*)$'

        results = []

        for less_resource in less_resources:
            res_id = less_resource.getId()
            find = re.search(regex, res_id)

            # Just make sure that is a plone.resource object
            if find:
                # Extract its resource directory type and name
                resource_directory_type, resource_file_name = find.groups()

                # Get its directoryResource object and extract the full path
                resource_path = getUtility(IResourceDirectory, name=resource_directory_type).directory

                results.append('/*    %s    */\n' % res_id)

                results.append(self.renderLESS(lessc_command_line, resource_path, resource_file_name))

                results.append('\n/*    End  %s    */\n' % res_id)
            else:
                self.logger.warning("The resource %s is not a valid plone.resource asset, and cannot be server-side compiled." % res_id)

        self.request.response.setHeader('Content-Type', 'text/css')
        return ''.join(results)

    @ram.cache(render_cachekey)
    def renderLESS(self, lessc_command_line, resource_path, resource_file_name):
        # Allow use of ++[name]++ resource paths, e.g. ++theme++less/bootstrap.less
        regex = r'@import\s+"(\+\+[\w_-]+\+\+[\w_-]+)\/([^"]*)";'
        main_file = file( os.path.join( resource_path, resource_file_name ) ).read()

        def expand_resource(match):
            resource_directory_type, resource_file_name = match.groups()
            respath = getUtility(IResourceDirectory, name = resource_directory_type).directory
            return '@import "%s/%s";' % (path_diff(resource_path, respath), resource_file_name)

        main_file = re.sub(regex, expand_resource, main_file)

        self.logger.info("The resource %s has been server-side compiled (with expanded resource paths)." % resource_file_name)

        tmp = tempfile.NamedTemporaryFile(dir = resource_path, delete = False)
        tmp.write(main_file)
        tmp.close()

        # Call the LESSC executable
        process = subprocess.Popen([lessc_command_line, tmp.name],
                           stdout = subprocess.PIPE)
        output, errors = process.communicate()

        os.remove(tmp.name)

        # Return the command output
        return output
