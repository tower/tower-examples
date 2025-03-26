from core.actions import Action
import glob
from typing import (
    Any)

class ReadFilepaths(Action):

    def __init__(self, actionname: str = None):
        super().__init__(actionname)

    def do(self, *args:Any, **kwargs: Any):
        """
        Creates a list of pathnames matching a specified pattern.
        Common patterns:
            do('/home/bill/*.txt') -> ['/home/bill/fileA.txt', '/home/bill/fileB.txt']
            do('*.txt|*.jpg') -> ['fileA.txt', 'fileB.txt', 'ImageA.jpg', 'ImageB.jpg']
            do('*.txt|*.jpg', root_dir = '/home/bill')
            do('./../data/**/*.jpg', recursive=True) -> All jpg files in ./../data and all its subdirectories
        :param args:
        :param kwargs:
        :return:
        """

        # see https://medium.com/@tubelwj/how-to-match-files-in-a-directory-using-python-1c5a5426861d#
        # see https://docs.python.org/3/library/glob.html
        out = glob.glob(*args,**kwargs)
        return out
