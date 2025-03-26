import dlt
from dlt.common.typing import TDataItems
from dlt.common.schema import TTableSchema
from dlt.common.destination import Destination
from typing import Any
from core.actions import Action

# https://dlthub.com/devel/dlt-ecosystem/destinations/destination

class Read(Action):

    def __init__(self, actionname: str = None):
        super().__init__(actionname)
        # needs to say from_reference("destination"... to work

        self.dltdestination = Destination.from_reference(
            "destination",
            #destination_name=self.actionname+"_destination",
            destination_callable=self.read_destination)

        self.dltpipeline = dlt.pipeline(
            self.actionname+"_destination_pipeline",
            destination=self.dltdestination)

        self.clean_state()

    def read_destination(self, items: TDataItems, table: TTableSchema, unusedparam = None) -> None:
        # sso 9/6/24: adding unusedparam and assigning a default value to fix a weird behavior that was introduced
        # since April 2024.
        tablename: str
        if table is None:
            tablename = "default"
        else:
            tablename = table["name"]
        if tablename not in self.readitems:
            self.readitems[tablename] = []
        self.readitems[tablename].extend(items)
        self.readtableschema[tablename] = table

    def clean_state(self):
        self.readitems={}
        self.readtableschema={}

    def do(self, *args:Any, **kwargs: Any):
        self.clean_state()
        self.dltpipeline.run(*args, **kwargs)







