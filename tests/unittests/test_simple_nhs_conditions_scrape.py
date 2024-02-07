import doctest
import src.data_ingestion.simple_nhs_conditions_scrape as simple_nhs_conditions_scrape


def load_tests(loader, tests, ignore):  # pylint: disable=unused-argument
    """This creates a unittest.TestCase from the doctests described in the
    module
    """
    tests.addTests(doctest.DocTestSuite(simple_nhs_conditions_scrape))
    return tests