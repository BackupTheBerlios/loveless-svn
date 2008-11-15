import time, sys
import unittest
from mako.template import Template
from mako.lookup import TemplateLookup
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relation, backref, mapper

_engine   = create_engine('sqlite:///:memory:', echo=True)
_metadata = MetaData()
_tlookup  = TemplateLookup(directories=['./mako/tests/'])
_verbose  = 2
Session   = sessionmaker(bind=_engine)
Base      = declarative_base()

testresult_table = Table('testresults', _metadata,
        Column('name', String, primary_key=True),
        Column('report', String),
        Column('success', Integer) )

class DBTestResult(unittest.TestResult):
    def __init__(self):
        self.name = None
        self.success = None
        self.report = None
        self.clone = None
        self.session = Session()

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.name = str(test)
        self.clone = self.session.query(DBTestResult).filter("name=%s" % ( self.name )).one() or None
        if not self.clone:
            self.clone = self
            self.session.add(self.clone)

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.clone.success = 0

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.clone.success = 1
        self.clone.report = self._exc_info_to_string(err, test)

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.clone.success = 2
        self.clone.report = self._exc_info_to_string(err, test)

    def stopTest(self, test):
        unittest.TestResult.stopTest(self, test)
        self.session.commit()


mapper(DBTestResult, testresult_table)

class DBTestRunner:
    def __init__(self):
        pass
    
    def _makeResult(self):
        return DBTestResult()

    def run(self, test):
        result = self._makeResult()
        stime = time.time()
        test(result)
        etime = time.time()

class TestApplication:
    def __init__(self, environ, start_response,
            module='__main__', defaultTest=None, defaultRunner=DBTestRunner,
            defaultLoader=unittest.TestLoader):
        if type(module) is type(''):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)
        else:
            self.module = module
        self.environ = environ
        self.start = start_response
        self.defaultTest = defaultTest
        self.defaultRunner = defaultRunner
        self.defaultLoader = defaultLoader

    def getTests(self):
        return self.defaultLoader().loadTestsFromModule(self.module)

    def runTests(self):
        testRunner = self.defaultRunner()
        testRunner.run(self.getTests())

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        self.start(status, response_headers)
        self.runTests()

        session = Session()
        testsRun = session.query(DBTestResult).all()
        testpage = _tlookup.get_template('/tests.7')

        yield testpage.render( tests=testsRun )

_metadata.create_all(_engine)
test_gateway = TestApplication
