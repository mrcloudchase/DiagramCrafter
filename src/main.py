from load_config import load_config
from azure_diagrams import generate_all_diagrams

def main():
    config = load_config("./config/config.json")
    generate_all_diagrams(config)

if __name__ == "__main__":
    main()
