import dlt
from typing import Any

from dlt.extract import DltResource
from dlt.destinations import filesystem
from core.actions import Action


class WriteFile(Action):

    def __init__(self, actionname: str = None, bucket_url: str = None):
        """
        :param actionname:
        :param bucket_url (str, optional) : file\://absolute/path for absolute path, file\:///relative/path for a relative path
        """
        super().__init__(actionname)

        self.writeitems = []

        # TODO: review filesystem (bucket_url="memory://m")
        self.dltdestination = filesystem(
            bucket_url = bucket_url,
            destination_name=self.actionname + "_destination"
        )

        self.dltpipeline = dlt.pipeline(
            self.actionname + "_destination_pipeline",
            destination=self.dltdestination,
            # dataset_name=self.actionname + "_dataset",
        )


    def do(self, items, *args: Any, **kwargs: Any):
        """ Writes to files.
            Text files will be compressed using gzip
            To view contents of these files, add the .Z extension, and then run zcat <file>.Z or type gunzip -c <file>
        Args:
            items ([] or dict) : items to write
            loader_file_format (str, optional): "jsonl", "parquet", "insert_values" see https://dlthub.com/docs/dlt-ecosystem/file-formats/
        Returns:
        """
        self.writeitems = items
        # sso 3/9/25
        source = self.memory_source(self)
        self.dltpipeline.run(source, *args, **kwargs)

    @dlt.source
    def memory_source(self):
        if isinstance(self.writeitems, dict):
            # put dict elements into kwargs
            for k, v in self.writeitems.items():
                yield self.memory_resource(self, items = v, resource_name = k)
        elif isinstance(self.writeitems, list):
            yield self.memory_resource(self, items = self.writeitems, resource_name = self.actionname+"_resource")


    @dlt.resource
    def memory_resource(self, items : [], resource_name : str) -> DltResource:
        items_generator = (item for item in items)
        return dlt.resource(
            items_generator,
            name=resource_name,
        )
