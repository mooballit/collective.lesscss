from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class CollectiveLesscss(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.lesscss
        xmlconfig.file('configure.zcml',
                       collective.lesscss,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.lesscss:default')

COLLECTIVE_LESSCSS_FIXTURE = CollectiveLesscss()
COLLECTIVE_LESSCSS_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(COLLECTIVE_LESSCSS_FIXTURE, ),
                       name="CollectiveLesscss:Integration")