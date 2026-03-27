import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
RESOLVED_CONFIG_PATH = ROOT / "config.resolved.json"
WORKSPACE_PATH = ROOT / "workspace"


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    config["agents"]["defaults"]["workspace"] = str(WORKSPACE_PATH)
    config["providers"]["custom"]["apiKey"] = require_env("LLM_API_KEY")
    config["providers"]["custom"]["apiBase"] = require_env("LLM_API_BASE_URL")

    config["gateway"]["host"] = require_env("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    config["gateway"]["port"] = int(require_env("NANOBOT_GATEWAY_CONTAINER_PORT"))

    channels = config.setdefault("channels", {})
    webchat = channels.setdefault("webchat", {})
    webchat["enabled"] = True
    webchat["host"] = require_env("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat["port"] = int(require_env("NANOBOT_WEBCHAT_CONTAINER_PORT"))
    webchat["allowFrom"] = webchat.get("allowFrom") or ["*"]

    lms = (
        config.setdefault("tools", {})
        .setdefault("mcpServers", {})
        .setdefault("lms", {})
    )
    lms["type"] = "stdio"
    lms["command"] = "python"
    lms["args"] = ["-m", "mcp_lms"]
    lms["env"] = {
        "NANOBOT_LMS_BACKEND_URL": require_env("NANOBOT_LMS_BACKEND_URL"),
        "NANOBOT_LMS_API_KEY": require_env("NANOBOT_LMS_API_KEY"),
        "NANOBOT_LOGS_BASE_URL": require_env("NANOBOT_LOGS_BASE_URL"),
        "NANOBOT_TRACES_BASE_URL": require_env("NANOBOT_TRACES_BASE_URL"),
    }

    RESOLVED_CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")

    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(RESOLVED_CONFIG_PATH),
            "--workspace",
            str(WORKSPACE_PATH),
        ],
    )


if __name__ == "__main__":
    main()
