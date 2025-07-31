import unittest
from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, Any, Optional
import sys
import json
import time

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
    print(f"Sending {msg=}")
    server.stdin.write(json.dumps(msg) + '\n')
    server.stdin.flush()
    response = json.loads(server.stdout.readline())
    print(f"Response: {response}")
    return (response) 

def send(method:str, params:Optional[Dict[str, Any]] = None, id:Optional[int] = None):
    msg: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params: msg["params"] = params
    if id: msg["id"] = id

    server = subprocess.Popen([sys.executable, "mcp_server.py"], 
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, text=True)
    # server.stdin.write(json.dumps(msg) + '\n')
    # server.stdin.flush()
    # response = server.stdout.readline()
    
    test_response = get_response(server, msg)
    server.terminate()
    
    server = subprocess.Popen([sys.executable, "__tests__/run_gold_server.py"], 
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, text=True)

    gold_response = get_response(server, msg)
    server.terminate()

    return test_response, gold_response

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test, self.gold = send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "Interactive Client", "version": "1"}}, 1)

    def testCapabilities(self):
        print(self.test["result"]["capabilities"])
        print(self.gold["result"]["capabilities"])
        self.assertDictContainsSubset(self.test["result"]["capabilities"], self.gold["result"]["capabilities"])
    

    def testResult(self):
        self.assertDictContainsSubset(self.test["result"], self.gold["result"])
    
        

if __name__ == "__main__":
    unittest.main()


# Gold Response:  {'experimental': {}, 'logging': None, 'prompts': {'listChanged': False}, 'resources': {'subscribe': False, 'listChanged': False}, 'tools': {'listChanged': False}, 'completions': None}
   
# Test Response: {'experimental': {}, 'prompts': {'listChanged': False}, 'resources': {'subscribe': False, 'listChanged': False}, 'tools': {'listChanged': False}}