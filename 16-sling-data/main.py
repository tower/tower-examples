import yaml
from sling import Replication

def main() -> None:
    print("Replicating data into Snowflake...")

    # # Or load into object
    with open('sling.yaml') as file:
      config = yaml.load(file, Loader=yaml.FullLoader)

    replication = Replication(**config)
    replication.run()
    print("Done!")

if __name__ == "__main__":
    main()	
