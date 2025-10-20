import json
import os
from datetime import datetime


class ToolLogger:
    def __init__(self, log_file="tool_results.json"):
        self.log_file = log_file
        self.logs = []

    def log_tool_result(self, tool_name: str, query: str, result: dict, success: bool):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "query": query,
            "success": success,
            "result": result,
            "result_keys": (
                list(result.keys()) if isinstance(result, dict) else "not_dict"
            ),
        }
        self.logs.append(log_entry)

        # Save to file immediately
        with open(self.log_file, "w") as f:
            json.dump(self.logs, f, indent=2)

    def get_logs(self):
        return self.logs


# Global logger instance
tool_logger = ToolLogger()
