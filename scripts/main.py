from config import SERVER_SCRIPT_PATH
from mcp_client import run_mcp_client
def main():
    run_mcp_client(SERVER_SCRIPT_PATH)
    print("no blocked")



if __name__ == "__main__":
    main()