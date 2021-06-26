import multiprocessing as _multiprocessing
import threading as _threading
import typing as _typing

_DataType = _typing.TypeVar("_DataType")


class DataBuffer(_typing.Iterable[_DataType]):
    def __iter__(self) -> _typing.Iterator[_DataType]:
        raise NotImplementedError


class _BasicDataBuffer(DataBuffer):
    class _DataBufferIterator(_typing.Iterator[_DataType]):
        def __iter__(self) -> _typing.Iterator[_DataType]:
            return self

        def __init__(self, data_source_iterator: _typing.Iterator[_DataType], buffer_size: int):
            self.__data_source_iterator: _typing.Iterator[_DataType] = data_source_iterator
            self._buffer_size: int = buffer_size

            self.__buffer: _typing.List[_DataType] = []

            self.__data_or_stop_iteration_exception: _typing.List[
                _typing.Union[_DataType, StopIteration]
            ] = []
            self.__fetching_process: _typing.Union[
                _threading.Thread, _multiprocessing.Process
            ] = _threading.Thread(target=self._fetch_data_task)
            self.__fetching_process.start()

        def _fetch_data_task(self):
            while True:
                if len(self.__data_or_stop_iteration_exception) < self._buffer_size:
                    try:
                        self.__data_or_stop_iteration_exception.append(
                            next(self.__data_source_iterator)
                        )
                    except Exception as _exception:
                        self.__data_or_stop_iteration_exception.append(_exception)
                        return

        def __next__(self) -> _DataType:
            while len(self.__data_or_stop_iteration_exception) == 0:
                continue
            data_or_stop_iteration_exception: _typing.Union[_DataType, Exception] = (
                self.__data_or_stop_iteration_exception.pop(0)
            )
            if (
                    isinstance(data_or_stop_iteration_exception, Exception) or
                    isinstance(data_or_stop_iteration_exception, StopIteration)
            ):
                raise data_or_stop_iteration_exception
            else:
                return data_or_stop_iteration_exception

    def __iter__(self) -> _typing.Iterator[_DataType]:
        return self._DataBufferIterator(iter(self._data_source), self._buffer_size)

    def __init__(self, data_source: _typing.Iterable[_DataType], buffer_size: int):
        if not isinstance(data_source, _typing.Iterable):
            raise TypeError
        if type(buffer_size) != int:
            raise TypeError
        elif buffer_size <= 0:
            raise ValueError
        self._data_source: _typing.Iterable[_DataType] = data_source
        self._buffer_size: int = buffer_size


class DataBufferDefaultBuilder(_typing.Generic[_DataType]):
    def __init__(self, data_source: _typing.Iterable[_DataType], buffer_size: int):
        if not isinstance(data_source, _typing.Iterable):
            raise TypeError
        if type(buffer_size) != int:
            raise TypeError
        elif buffer_size <= 0:
            raise ValueError
        self._data_source: _typing.Iterable[_DataType] = data_source
        self._buffer_size: int = buffer_size

    def build(self, *__args, **__kwargs) -> DataBuffer[_DataType]:
        return _BasicDataBuffer(self._data_source, self._buffer_size)
