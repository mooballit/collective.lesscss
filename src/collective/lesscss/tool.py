from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.ResourceRegistries.tools.CSSRegistry import CSSRegistryTool
from Products.ResourceRegistries.tools.CSSRegistry import Stylesheet
from collective.lesscss.interface import ILESSRegistry
from Products.ResourceRegistries import permissions


class LESSStyleSheet(Stylesheet):
    # Overrides to set default Caching to False
    def getCacheable(self):
        return self._data.get('cacheable', False)

    def getCookable(self):
        return self._data.get('cookable', False)

class LESSRegistryTool(CSSRegistryTool):
    """A Plone registry for managing the linking to css files."""
    security = ClassSecurityInfo()

    id = 'portal_less'
    meta_type = 'LESS Stylesheets Registry'
    title = 'LESS Registry'

    implements(ILESSRegistry)

    #
    # ZMI stuff
    #

    manage_cssForm = PageTemplateFile('www/lessconfig', globals())

    filename_base = 'ploneLESSStyles'
    filename_appendix = '.less'
    merged_output_prefix = u''
    cache_duration = 7
    resource_class = LESSStyleSheet

    security.declareProtected(permissions.ManagePortal, 'getRenderingOptions')
    def getRenderingOptions(self):
        """Rendering methods for use in ZMI forms."""
        return ('link', )

    # Overrides to set default Caching to False
    def manage_addStylesheet(self, id, expression='', media='screen',
                             rel='stylesheet', title='', rendering='link',
                             enabled=False, cookable=True, compression='safe',
                             cacheable=False, REQUEST=None,
                             conditionalcomment='', authenticated=False,
                             applyPrefix=False, bundle='default'):
        """Register a stylesheet from a TTW request."""
        self.registerStylesheet(id, expression, media, rel, title,
                                rendering, enabled, cookable, compression,
                                cacheable, conditionalcomment, authenticated,
                                applyPrefix=applyPrefix, bundle=bundle)
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def manage_saveStylesheets(self, REQUEST=None):
        """Save stylesheets from the ZMI.

        Updates the whole sequence. For editing and reordering.
        """
        debugmode = REQUEST.get('debugmode', False)
        self.setDebugMode(debugmode)
        records = REQUEST.get('stylesheets', [])
        records.sort(lambda a, b: a.sort - b.sort)
        self.resources = ()
        stylesheets = []
        for r in records:
            stylesheet = self.resource_class(
                                    r.get('id'),
                                    expression=r.get('expression', ''),
                                    media=r.get('media', 'screen'),
                                    rel=r.get('rel', 'stylesheet'),
                                    title=r.get('title', ''),
                                    rendering=r.get('rendering', 'link'),
                                    enabled=r.get('enabled', True),
                                    cookable=r.get('cookable', False),
                                    cacheable=r.get('cacheable', False),
                                    compression=r.get('compression', 'safe'),
                                    conditionalcomment=r.get('conditionalcomment',''),
                                    authenticated=r.get('authenticated', False),
                                    applyPrefix=r.get('applyPrefix', False),
                                    bundle=r.get('bundle', 'default'))
            stylesheets.append(stylesheet)
        self.resources = tuple(stylesheets)
        self.cookResources()
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def registerStylesheet(self, id, expression='', media='screen',
                           rel='stylesheet', title='', rendering='link',
                           enabled=1, cookable=True, compression='safe',
                           cacheable=False, conditionalcomment='',
                           authenticated=False, skipCooking=False,
                           applyPrefix=False, bundle='default'):
        """Register a stylesheet."""
        
        if not id:
            raise ValueError("id is required")
        
        stylesheet = self.resource_class(
                                id,
                                expression=expression,
                                media=media,
                                rel=rel,
                                title=title,
                                rendering=rendering,
                                enabled=enabled,
                                cookable=cookable,
                                compression=compression,
                                cacheable=cacheable,
                                conditionalcomment=conditionalcomment,
                                authenticated=authenticated,
                                applyPrefix=applyPrefix,
                                bundle=bundle)
        self.storeResource(stylesheet, skipCooking=skipCooking)


