import unittest

class DependenciesTestCase(unittest.TestCase):
    def test_mako_templates(self):
        from mako.template import Template
        from mako.lookup import TemplateLookup

        self.assert_( Template )

    def test_sqlalchemy(self):
        import sqlalchemy

        self.assert_( sqlalchemy )

    def test_unittest(self):
        self.assert_( unittest )
