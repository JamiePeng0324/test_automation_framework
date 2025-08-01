import allure
import time
import pytest
from pathlib import Path
from infrastructure.base.abstract_test_base import AbstractTestBase
from tests.config.settings import (
    APV_SERVER_CONFIG,
    SERVER_ONE_CONFIG,
    SERVER_TWO_CONFIG,
    CLIENT_ONE_CONFIG,
)


TEST_VIRTUAL_IP = "192.168.56.70"
TEST_VIRTUAL_PORT = 8000

@pytest.mark.parametrize("baseline_fixture", ["slb"], indirect=True)
@pytest.mark.usefixtures("baseline_fixture")
class TestSlb(AbstractTestBase):

    @classmethod
    def get_test_case_catalog(cls):
        return {
            "APV_SLB_01": {
                "test_function_name": cls.test_slb_ip_configuration_and_the_performance_of_function,
                "description": "Confirm slb ip configuration and the performance of function.",
                # https://www.notion.so/Test-slb-ip-configuration-and-the-performance-of-function-23e090e008db80118a6ee241bd490b05?source=copy_link
            },
            "APV_SLB_02": {
                "test_function_name": cls.test_slb_ip_configuration_and_the_performance_of_function_in_fail_situation,
                "description": "Confirm slb ip configuration and the performance of function in fail situation.",
                # https://www.notion.so/Test-slb-ip-configuration-and-the-performance-of-function-in-fail-situation-23e090e008db80559696fe9967d14461?source=copy_link
            },
            "APV_SLB_03": {
                "test_function_name": cls.test_slb_ip_configuration_and_the_performance_of_function_in_fail_situation_2,
                "description": "Confirm slb ip configuration and the performance of function in fail situation 2.",
                # https://www.notion.so/Test-slb-ip-configuration-and-the-performance-of-function-in-fail-situation-2-23e090e008db8017a63dd1527ce82b59?source=copy_link
            }
        }

    def setup(self):
        with self.allure.step_with_log("Setup : Setup the test environment"):
            self.logger.info("----setup----")
            self.curl_results = []

    def teardown(self):
        with self.allure.step_with_log("Teardown : Clean the test environment"):
            self.logger.info("----teardown----")
            self.ssh.connect_shell_via_jump(
                hostname=APV_SERVER_CONFIG.server.host,
                username=APV_SERVER_CONFIG.server.username,
                password=APV_SERVER_CONFIG.server.password,
                port=APV_SERVER_CONFIG.server.port,
            )
            self.apv.enable_mode()
            self.apv.config_terminal_mode(is_force=True)
            self.ssh.send_command_in_shell("clear slb all")
            self.apv.write_memory()
            self.ssh.disconnect()

    @allure.description(
        "Confirm slb ip configuration and the performance of function."
    )
    def test_slb_ip_configuration_and_the_performance_of_function(self):
        with self.allure.step_with_log(
            "Step1 : Connect to server1 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step2 : Connect to server2 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step3 : Connect to APV shell and open config terminal mode."
        ):
            self.ssh.connect_shell_via_jump(
                hostname=APV_SERVER_CONFIG.server.host,
                username=APV_SERVER_CONFIG.server.username,
                password=APV_SERVER_CONFIG.server.password,
                port=APV_SERVER_CONFIG.server.port,
            )
            self.apv.enable_mode()
            self.apv.config_terminal_mode()

        with self.allure.step_with_log(
            "Step4 : Add 1st server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_1 {SERVER_ONE_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step5 : Add 2nd server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_2 {SERVER_TWO_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step6 : Create a group and choose rr pattern"
        ):
            self.ssh.send_command_in_shell("slb group method slb_servers rr")

        with self.allure.step_with_log("Step7 : Add server1 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_1"
            )

        with self.allure.step_with_log("Step8 : Add server2 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_2"
            )

        with self.allure.step_with_log("Step9 : Enable server group."):
            self.ssh.send_command_in_shell("slb group enable slb_servers")

        with self.allure.step_with_log(
            "Step10 : Create a virtual ip service."
        ):
            self.ssh.send_command_in_shell(
                f"slb virtual ip ip_services {TEST_VIRTUAL_IP}"
            )

        with self.allure.step_with_log("Step11 : Enable virtual ip service."):
            self.ssh.send_command_in_shell("slb virtual enable ip_services")

        with self.allure.step_with_log(
            "Step12 : Map virtual service and group."
        ):
            self.ssh.send_command_in_shell(
                "slb policy default ip_services slb_servers"
            )

        with self.allure.step_with_log(
            "Step13 : Write memory and check setting info."
        ):
            self.apv.write_memory()
            self.ssh.send_command_in_shell("show slb all")
            self.apv.config_terminal_mode(mode=False)
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step14 : Connect to client1 and curl VIP 10 times"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=CLIENT_ONE_CONFIG.server.host,
                username=CLIENT_ONE_CONFIG.server.username,
                password=CLIENT_ONE_CONFIG.server.password,
                port=CLIENT_ONE_CONFIG.server.port,
            )
            for _ in range(10):
                test_cmd = (
                    f"curl -s http://{TEST_VIRTUAL_IP}:{TEST_VIRTUAL_PORT}/"
                )
                res = self.ssh.send_command_in_shell(test_cmd)
                self.curl_results.append(res)
                time.sleep(1)
            self.ssh.disconnect()

        with self.allure.step_with_log("Step15 : Analyse the results"):
            server1_count = sum("Hello from server1" in r for r in self.curl_results)
            server2_count = sum("Hello from server2" in r for r in self.curl_results)
            total = len(self.curl_results)
            self.assertion.assert_equal(total, 10, "Somethings wrong when using curl.")

            self.logger.info(f"Total test times: {total}")
            self.logger.info(
                f"Server1 count: {server1_count} ({server1_count/total:.1%})"
            )
            self.logger.info(
                f"Server2 count: {server2_count} ({server2_count/total:.1%})"
            )

            is_evenly_distributed = abs(server1_count - server2_count) <= 1
            if is_evenly_distributed:
                self.logger.info(
                    "Round-robin appears to distribute traffic evenly."
                )
            else:
                self.logger.warning("Round-robin distribution is imbalanced.")
            self.assertion.assert_true(
                is_evenly_distributed,
                "Round-robin distribution failed: server counts are imbalanced.",
            )

        with self.allure.step_with_log("Step16 : Get server1's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_ONE_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step17 : Get server2's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_TWO_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step18 : Close server1 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log("Step19 : Close server2 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()

    @allure.description(
        "Confirm slb ip configuration and the performance of function in fail situation."
    )
    def test_slb_ip_configuration_and_the_performance_of_function_in_fail_situation(self):
        with self.allure.step_with_log(
            "Step1 : Connect to server1 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step2 : Connect to server2 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step3 : Connect to APV shell and open config terminal mode."
        ):
            self.ssh.connect_shell_via_jump(
                hostname=APV_SERVER_CONFIG.server.host,
                username=APV_SERVER_CONFIG.server.username,
                password=APV_SERVER_CONFIG.server.password,
                port=APV_SERVER_CONFIG.server.port,
            )
            self.apv.enable_mode()
            self.apv.config_terminal_mode()

        with self.allure.step_with_log(
            "Step4 : Add 1st server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_1 {SERVER_ONE_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step5 : Add 2nd server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_2 {SERVER_TWO_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step6 : Create a group and choose rr pattern"
        ):
            self.ssh.send_command_in_shell("slb group method slb_servers rr")

        with self.allure.step_with_log("Step7 : Add server1 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_1"
            )

        with self.allure.step_with_log("Step8 : Add server2 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_2"
            )

        with self.allure.step_with_log("Step9 : Enable server group."):
            self.ssh.send_command_in_shell("slb group enajdiwjidwjojble slb_servers")

        with self.allure.step_with_log(
            "Step10 : Create a virtual ip service."
        ):
            self.ssh.send_command_in_shell(
                f"slb virtual ip ip_services {TEST_VIRTUAL_IP}"
            )

        with self.allure.step_with_log("Step11 : Enable virtual ip service."):
            self.ssh.send_command_in_shell("slb virtual enable ip_services")

        with self.allure.step_with_log(
            "Step12 : Map virtual service and group."
        ):
            self.ssh.send_command_in_shell(
                "slb policy default ip_services slb_servers"
            )

        with self.allure.step_with_log(
            "Step13 : Write memory and check setting info."
        ):
            self.apv.write_memory()
            self.ssh.send_command_in_shell("show slb all")
            self.apv.config_terminal_mode(mode=False)
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step14 : Connect to client1 and curl VIP 10 times"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=CLIENT_ONE_CONFIG.server.host,
                username=CLIENT_ONE_CONFIG.server.username,
                password=CLIENT_ONE_CONFIG.server.password,
                port=CLIENT_ONE_CONFIG.server.port,
            )
            for _ in range(10):
                test_cmd = (
                    f"curl -s http://{TEST_VIRTUAL_IP}:{TEST_VIRTUAL_PORT}/"
                )
                res = self.ssh.send_command_in_shell(test_cmd)
                self.curl_results.append(res)
                time.sleep(1)
            self.ssh.disconnect()

        with self.allure.step_with_log("Step15 : Analyse the results"):
            server1_count = sum("Hello from server1" in r for r in self.curl_results)
            server2_count = sum("Hello from server2" in r for r in self.curl_results)
            total = len(self.curl_results)
            self.assertion.assert_equal(total, 10, "Somethings wrong when using curl.")

            self.logger.info(f"Total test times: {total}")
            self.logger.info(
                f"Server1 count: {server1_count} ({server1_count/total:.1%})"
            )
            self.logger.info(
                f"Server2 count: {server2_count} ({server2_count/total:.1%})"
            )

            is_evenly_distributed = abs(server1_count - server2_count) <= 1
            if is_evenly_distributed:
                self.logger.info(
                    "Round-robin appears to distribute traffic evenly."
                )
            else:
                self.logger.warning("Round-robin distribution is imbalanced.")
            self.assertion.assert_true(
                is_evenly_distributed,
                "Round-robin distribution failed: server counts are imbalanced.",
            )

        with self.allure.step_with_log("Step16 : Get server1's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_ONE_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step17 : Get server2's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_TWO_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step18 : Close server1 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log("Step19 : Close server2 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()

    @allure.description(
        "Confirm slb ip configuration and the performance of function in fail situation 2."
    )
    def test_slb_ip_configuration_and_the_performance_of_function_in_fail_situation_2(self):
        with self.allure.step_with_log(
            "Step1 : Connect to server1 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step2 : Connect to server2 and set the environment"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_prepared = self.http_server_manager.prepare_http_server(server_name)
            self.assertion.assert_true(is_server_prepared, f"Fail to prepare {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step3 : Connect to APV shell and open config terminal mode."
        ):
            self.ssh.connect_shell_via_jump(
                hostname=APV_SERVER_CONFIG.server.host,
                username=APV_SERVER_CONFIG.server.username,
                password=APV_SERVER_CONFIG.server.password,
                port=APV_SERVER_CONFIG.server.port,
            )
            self.apv.enable_mode()
            self.apv.config_terminal_mode()

        with self.allure.step_with_log(
            "Step4 : Add 1st server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_1 {SERVER_ONE_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step5 : Add 2nd server by ip protocol."
        ):
            self.ssh.send_command_in_shell(
                f"slb real ip ip_server_2 {SERVER_TWO_CONFIG.server.host}"
            )

        with self.allure.step_with_log(
            "Step6 : Create a group and choose rr pattern"
        ):
            self.ssh.send_command_in_shell("slb group method slb_servers rr")

        with self.allure.step_with_log("Step7 : Add server1 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_1"
            )

        with self.allure.step_with_log("Step8 : Add server2 into group."):
            self.ssh.send_command_in_shell(
                "slb group member slb_servers ip_server_2"
            )

        with self.allure.step_with_log("Step9 : Enable server group."):
            self.ssh.send_command_in_shell("slb group enable slb_servers")

        with self.allure.step_with_log(
            "Step10 : Create a virtual ip service."
        ):
            self.ssh.send_command_in_shell(
                f"slb virtual ip ip_services {TEST_VIRTUAL_IP}"
            )

        with self.allure.step_with_log("Step11 : Enable virtual ip service."):
            self.ssh.send_command_in_shell("slb virtual enable ip_services")

        with self.allure.step_with_log(
            "Step12 : Map virtual service and group."
        ):
            self.ssh.send_command_in_shell(
                "slb policy default ip_services slb_servers"
            )

        with self.allure.step_with_log(
            "Step13 : Write memory and check setting info."
        ):
            self.apv.write_memory()
            self.ssh.send_command_in_shell("show slb all")
            self.apv.config_terminal_mode(mode=False)
            self.ssh.disconnect()

        with self.allure.step_with_log(
            "Step14 : Connect to client1 and curl VIP 10 times"
        ):
            self.ssh.connect_shell_via_jump(
                hostname=CLIENT_ONE_CONFIG.server.host,
                username=CLIENT_ONE_CONFIG.server.username,
                password=CLIENT_ONE_CONFIG.server.password,
                port=CLIENT_ONE_CONFIG.server.port,
            )
            for _ in range(10):
                test_cmd = (
                    f"curl -s http://{TEST_VIRTUAL_IP}:{TEST_VIRTUAL_PORT}/"
                )
                res = self.ssh.send_command_in_shell(test_cmd)
                self.curl_results.append(res)
                time.sleep(1)
            self.ssh.disconnect()

        with self.allure.step_with_log("Step15 : Analyse the results"):
            server1_count = sum("Hello from server1" in r for r in self.curl_results)
            server2_count = sum("Hello from server2" in r for r in self.curl_results)
            total = len(self.curl_results) + 57
            self.assertion.assert_equal(total, 10, "Somethings wrong when using curl.")

            self.logger.info(f"Total test times: {total}")
            self.logger.info(
                f"Server1 count: {server1_count} ({server1_count/total:.1%})"
            )
            self.logger.info(
                f"Server2 count: {server2_count} ({server2_count/total:.1%})"
            )

            is_evenly_distributed = abs(server1_count - server2_count) <= 1
            if is_evenly_distributed:
                self.logger.info(
                    "Round-robin appears to distribute traffic evenly."
                )
            else:
                self.logger.warning("Round-robin distribution is imbalanced.")
            self.assertion.assert_true(
                is_evenly_distributed,
                "Round-robin distribution failed: server counts are imbalanced.",
            )

        with self.allure.step_with_log("Step16 : Get server1's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_ONE_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step17 : Get server2's log"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            self.http_server_manager.get_server_log(
                server_name={SERVER_TWO_CONFIG.server.name}
            )
            self.ssh.disconnect()

        with self.allure.step_with_log("Step18 : Close server1 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_ONE_CONFIG.server.host,
                username=SERVER_ONE_CONFIG.server.username,
                password=SERVER_ONE_CONFIG.server.password,
                port=SERVER_ONE_CONFIG.server.port,
            )
            server_name = SERVER_ONE_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()

        with self.allure.step_with_log("Step19 : Close server2 http.server"):
            self.ssh.connect_shell_via_jump(
                hostname=SERVER_TWO_CONFIG.server.host,
                username=SERVER_TWO_CONFIG.server.username,
                password=SERVER_TWO_CONFIG.server.password,
                port=SERVER_TWO_CONFIG.server.port,
            )
            server_name = SERVER_TWO_CONFIG.server.name
            is_server_closed = self.http_server_manager.close_http_server()
            self.assertion.assert_true(is_server_closed, f"Fail to close {server_name}'s http_server")
            self.ssh.disconnect()