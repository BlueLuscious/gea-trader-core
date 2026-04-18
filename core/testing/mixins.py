""" Shared mixins for project tests. """


class LoggedTestMixin:
    """ Print a success log line for each passing test method. """

    _testMethodName: str

    @staticmethod
    def capture_result_counts(result: object) -> dict[str, int]:
        """ Capture relevant counters from a unittest result object.

        Args:
            result: Result object being updated by the runner.

        Returns:
            dict[str, int]: Snapshot of the result counters.
        """
        return {
            "failures": len(getattr(result, "failures", [])),
            "errors": len(getattr(result, "errors", [])),
            "skipped": len(getattr(result, "skipped", [])),
            "expected_failures": len(getattr(result, "expectedFailures", [])),
            "unexpected_successes": len(getattr(result, "unexpectedSuccesses", [])),
        }

    @staticmethod
    def did_test_pass(before: dict[str, int], after: dict[str, int]) -> bool:
        """ Decide whether the current test completed successfully.

        Args:
            before: Counter snapshot before the test run.
            after: Counter snapshot after the test run.

        Returns:
            bool: ``True`` when the test passed without failures, errors or skips.
        """
        return (
            after["failures"] == before["failures"]
            and after["errors"] == before["errors"]
            and after["skipped"] == before["skipped"]
            and after["expected_failures"] == before["expected_failures"]
            and after["unexpected_successes"] == before["unexpected_successes"]
        )

    def build_success_log_message(self) -> str:
        """ Build the formatted success log line for the current test.

        Returns:
            str: Success log line in the agreed format.
        """
        case_name = self.__class__.__name__
        method_name = self._testMethodName
        info_message = self.resolve_info_message()
        return f"TEST | {case_name} | {method_name} | {info_message}"

    def resolve_info_message(self) -> str:
        """ Resolve the log message from the current test method docstring.

        Returns:
            str: Human-readable info message for the test.
        """
        test_method = getattr(self, self._testMethodName)
        docstring = (test_method.__doc__ or "").strip()
        return " ".join(docstring.split()) if docstring else "OK"
