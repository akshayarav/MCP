import unittest
from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, Any, Optional
import sys
import json
import time


def close_server(server):
    if server.stdin:
        server.stdin.close()
    if server.stdout:
        server.stdout.close()
    if server.stderr:
        server.stderr.close()
    server.terminate()
    server.wait()


def get_response(server, msg) -> Dict[str, Any]:
    # Give server time to start
    time.sleep(0.5)

    if server.poll() is not None:
        print(f"Server exited with code: {server.returncode}")
        if server.stderr:
            stderr_output = server.stderr.read()
            if stderr_output:
                print(f"Server error: {stderr_output}")
            sys.exit(1)
    if not server.stdin:
        raise Exception("Server.stdout is None")
    if not server.stdout:
        raise Exception("Server.stdin is None")
    server.stdin.write(json.dumps(msg) + "\n")
    server.stdin.flush()
    response = json.loads(server.stdout.readline())
    return response


def send(
    method: str, params: Optional[Dict[str, Any]] = None, id: Optional[int] = None
):
    msg: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params:
        msg["params"] = params
    if id:
        msg["id"] = id

    server = subprocess.Popen(
        [sys.executable, "src/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    test_response = get_response(server, msg)
    close_server(server)

    server = subprocess.Popen(
        [sys.executable, "__tests__/run_gold_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    gold_response = get_response(server, msg)
    close_server(server)

    return test_response, gold_response


class TestInitialize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.test, cls.gold = send(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "Interactive Client", "version": "1"},
            },
            1,
        )

    def test_valid_jsonrpc_response(self):
        self.assertEqual(self.test.get("jsonrpc"), "2.0")

    def test_has_result(self):
        self.assertIn("result", self.test)

    def test_has_capabilities(self):
        self.assertIn("capabilities", self.test["result"])

    def test_has_required_prompts_capability(self):
        self.assertIn("prompts", self.test["result"]["capabilities"])

    def test_has_required_resources_capability(self):
        self.assertIn("resources", self.test["result"]["capabilities"])

    def test_has_required_tools_capability(self):
        self.assertIn("tools", self.test["result"]["capabilities"])

    def test_protocol_version_matches(self):
        self.assertEqual(
            self.test["result"]["protocolVersion"],
            self.gold["result"]["protocolVersion"],
        )

    def test_no_error_present(self):
        self.assertNotIn("error", self.test)

    def test_supports_all_gold_capabilities(self):
        """Ensure our server supports everything the gold server does"""
        test_caps = self.test["result"]["capabilities"]
        gold_caps = self.gold["result"]["capabilities"]

        for cap_name in gold_caps.keys():
            self.assertIn(cap_name, test_caps)


class TestToolList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test, cls.gold = send("tools/list", id=2)

    def test_tools_list(self):
        test, gold = send("tools/list", None, 2)  # id=2 for tools/list
        self.assertEqual(test.get("jsonrpc"), "2.0")

    def test_tools_list_has_result(self):
        test, gold = send("tools/list", None, 2)
        self.assertIn("result", test)

    def test_tools_list_has_tools(self):
        test, gold = send("tools/list", None, 2)
        self.assertIn("tools", test["result"])

    def test_greeting_tool_present(self):
        test, gold = send("tools/list", None, 2)
        tool_names = [tool["name"] for tool in test["result"]["tools"]]
        self.assertIn(
            "greeting", tool_names
        )  # Assuming your Greeting tool is named "greeting"


if __name__ == "__main__":
    unittest.main()
