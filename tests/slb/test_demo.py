import pytest
import allure
import time
from infrastructure.base.abstract_test_base import AbstractTestBase


class TestSUM(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "testcase 1": {
                "test_function_name": cls.test_sum,
                "description": "Jamie self test about slb ip",
                # https://google.com
            },
        }

    def setup(self):
        self.logger.info("----setup----")

    def teardown(self):
        self.logger.info("----teardown----")

    @pytest.mark.no_setup
    @allure.description("fjeifjie")
    def test_sum(self):
        x = 1 + 2
        assert x == 3

    @pytest.mark.no_setup
    @pytest.mark.no_teardown
    @allure.description("jfieifeoijeoi")
    def test_string(self):
        x = "jfeijfoejfoei"
        assert x == "jfeijfoejfoei"

    @allure.description("kofekckoko")
    def test_minus(self):
        with allure.step("step1 blablabla"):
            self.logger.info("x = 5")
            x = 5
            time.sleep(1)

        with allure.step("step2 blablbablablalba"):
            self.logger.info("y = 2")
            y = 2
            time.sleep(1)

        with allure.step("step3 kofekosk;"):
            self.logger.info("z = x - y")
            z = x - y
            time.sleep(1)

        assert z == 3

    @allure.description("kfoekfoko")
    def test_string2(self):
        with allure.step("step1 kodwkdowkwkdo"):
            self.logger.info("x = dddddf")
            x = "ddddf"
            time.sleep(1)

        with allure.step("step2 kodwkdowkwkdo"):
            self.logger.info("y = ddddd")
            y = "dddd"
            time.sleep(1)

        with allure.step("step3 compare"):
            self.logger.info("x = y")
            self.assertion.assert_equal(x, y, "x is not equal to y")
            time.sleep(1)

    def test_assert_equal_pass(self):
        self.assertion.assert_equal(5, 5)

    def test_assert_equal_fail(self):
        self.assertion.assert_equal(5, 10)

    def test_assert_not_equal_pass(self):
        self.assertion.assert_not_equal("foo", "bar")

    def test_assert_not_equal_fail(self):
        self.assertion.assert_not_equal("same", "same")

    def test_assert_true_pass(self):
        self.assertion.assert_true(1 == 1)

    def test_assert_true_fail(self):
        self.assertion.assert_true(False)

    @allure.description("jkfeifjie")
    def test_run_command_success_string(self):
        """Test a successful command execution with string command."""
        command = "echo hello world"
        result = self.cli.run_command(command)
        self.assertion.assert_equal(result.returncode, 0)
        self.assertion.assert_in("hello world", result.stdout)
        assert "hello world" in result.stdout
        self.assertion.assert_equal(result.stderr, "")
        assert result.stderr == ""

    def test_run_command_success_list(self):
        """Test a successful command execution with list command."""
        command = ["echo", "hello", "world"]
        result = self.cli.run_command(command)
        assert result.returncode == 0
        assert "hello world" in result.stdout
        assert result.stderr == ""

    def test_run_command_success_no_output_capture(self):
        """Test successful command execution without capturing output."""
        command = "echo should not be captured"
        result = self.cli.run_command(command, capture_output=False)
        assert result.returncode == 0
        assert result.stdout == None
        assert result.stderr == None

    def test_run_command_success_shell_mode(self):
        """Test a successful command execution in shell mode."""
        command = "ls -l /tmp/ | grep tmp"
        result = self.cli.run_command(command, shell=True)
        assert result.returncode == 0
        assert "tmp" in result.stdout
        assert result.stderr == ""
