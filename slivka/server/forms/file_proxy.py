import os
import typing

import shutil

from slivka.db.documents import UploadedFile, JobMetadata


class FileProxy:
    _file = None  # type: typing.IO

    closed = property(lambda self: self._file is None or self.file.closed)
    fileno = property(lambda self: self.file.fileno)
    flush = property(lambda self: self.file.flush)
    isatty = property(lambda self: self.file.isatty)
    read = property(lambda self: self.file.read)
    readable = property(lambda self: self.file.readable)
    readinto = property(lambda self: self.file.readinto)
    readline = property(lambda self: self.file.readline)
    readlines = property(lambda self: self.file.readlines)
    seek = property(lambda self: self.file.seek)
    seekable = property(lambda self: self.file.seekable)
    tell = property(lambda self: self.file.tell)
    truncate = property(lambda self: self.file.truncate)
    writable = property(lambda self: self.file.writable)
    write = property(lambda self: self.file.write)
    writelines = property(lambda self: self.file.writelines)

    def __init__(self, file=None, path=None):
        self.file = file
        self.path = path

    def __iter__(self):
        return iter(self.file)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _tb):
        self.close()

    def reopen(self):
        if not self.closed:
            self.seek(0)
        elif self.path and os.path.exists(self.path):
            self.file = open(self.path, 'rb')
        else:
            raise OSError("Can't open the file.")
        return self

    def _get_file(self):
        if self._file is None:
            if self.path is None:
                raise ValueError("The proxy has no associated file")
            self.reopen()
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def save_as(self, path, fp=None):
        """
        Saves the file at the specified location. If ``fp`` is specified it
        will be used to write the content. Otherwise, a new file at ``path``
        will be created.

        :param path: Path to the destination file
        :param fp: File-like object at the location specified by ``path``
        """
        self.reopen()
        path = os.path.realpath(path)
        if fp:
            shutil.copyfileobj(self.file, fp)
        else:
            with open(path, 'wb') as dst:
                shutil.copyfileobj(self.file, dst)
        self.path = path

    def close(self):
        if self._file is not None:
            self._file.close()


def _get_file_from_uuid(uuid, database):
    tokens = uuid.split('/', 1)
    if len(tokens) == 1:
        # user uploaded file
        uf = UploadedFile.find_one(database, uuid=uuid)
        if uf is None: return None
        return FileProxy(path=uf['path'])
    else:
        # job output file
        job_uuid, filename = tokens
        job = JobMetadata.find_one(database, uuid=job_uuid)
        return job and FileProxy(path=os.path.join(job.work_dir, filename))