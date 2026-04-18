""" Shared base test classes built on top of reusable testing mixins. """

from unittest import TestResult
from django.test import SimpleTestCase, TestCase, TransactionTestCase
from core.testing.mixins import LoggedTestMixin


class LoggedTestCase(LoggedTestMixin, TestCase):
    """ Django database test case with automatic success logging. """

    def run(self, result: TestResult | None = None) -> TestResult | None:
        """ Run the test and print a formatted success log when it passes.

        Args:
            result: Optional unittest result collector.

        Returns:
            TestResult | None: The result returned by the parent test runner.
        """
        active_result = result or self.defaultTestResult()
        before = self.capture_result_counts(active_result)
        final_result = super().run(active_result)
        after = self.capture_result_counts(active_result)

        if self.did_test_pass(before, after):
            print(f"\n{self.build_success_log_message()}")

        return final_result


class LoggedSimpleTestCase(LoggedTestMixin, SimpleTestCase):
    """ Django simple test case with automatic success logging. """

    def run(self, result: TestResult | None = None) -> TestResult | None:
        """ Run the test and print a formatted success log when it passes.

        Args:
            result: Optional unittest result collector.

        Returns:
            TestResult | None: The result returned by the parent test runner.
        """
        active_result = result or self.defaultTestResult()
        before = self.capture_result_counts(active_result)
        final_result = super().run(active_result)
        after = self.capture_result_counts(active_result)

        if self.did_test_pass(before, after):
            print(f"\n{self.build_success_log_message()}")

        return final_result


class LoggedTransactionTestCase(LoggedTestMixin, TransactionTestCase):
    """ Django transaction test case with automatic success logging. """

    def run(self, result: TestResult | None = None) -> TestResult | None:
        """ Run the test and print a formatted success log when it passes.

        Args:
            result: Optional unittest result collector.

        Returns:
            TestResult | None: The result returned by the parent test runner.
        """
        active_result = result or self.defaultTestResult()
        before = self.capture_result_counts(active_result)
        final_result = super().run(active_result)
        after = self.capture_result_counts(active_result)

        if self.did_test_pass(before, after):
            print(f"\n{self.build_success_log_message()}")

        return final_result
