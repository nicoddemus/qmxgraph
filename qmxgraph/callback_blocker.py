# Heavily based on `pytestqt.wait_signal.CallbackBlocker`.
from typing import Any, Callable, Optional, Hashable, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class CallbackBlocker:
    """
    An object which checks if the returned callback gets called.

    Intended to be used as a context manager.

    :ivar int timeout:
        Maximum time to wait for the callback to be called.

    :ivar tuple args:
        The arguments with which the callback was called, or None if the
        callback wasn't called at all.

    :ivar dict kwargs:
        The keyword arguments with which the callback was called, or None if
        the callback wasn't called at all.
    """

    DEFAULT_TIMEOUT = 1000

    def __init__(
        self, timeout: int = DEFAULT_TIMEOUT, msg: Optional[str] = None,
    ):
        self.timeout = timeout
        self.args = None
        self.msg = msg
        self.kwargs = None
        self.called = False
        self._loop = QtCore.QEventLoop()
        if timeout is None:
            self._timer = None
        else:
            self._timer = QtCore.QTimer(self._loop)
            self._timer.setSingleShot(True)
            self._timer.setInterval(timeout)

    def wait(self) -> None:
        """
        Waits until either the returned callback is called or timeout is
        reached.
        """
        __tracebackhide__ = True
        if self.called:
            return
        if self._timer is not None:
            self._timer.timeout.connect(self._quit_loop_by_timeout)
            self._timer.start()
        self._loop.exec_()
        if not self.called:
            msg = f"Callback wasn't called after {self.timeout}ms."
            if self.msg:
                msg += f'\n> {self.msg}'
            raise TimeoutError(msg)

    def _quit_loop_by_timeout(self) -> None:
        try:
            self._cleanup()
        finally:
            self._loop.quit()

    def _cleanup(self) -> None:
        if self._timer is not None:
            silent_disconnect(self._timer.timeout, self._quit_loop_by_timeout)
            self._timer.stop()
            self._timer = None

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        # Not inside the try: block, as if self.called is True, we did quit the
        # loop already.
        if self.called:
            raise CallbackCalledTwiceError("Callback called twice")
        try:
            self.args = args
            self.kwargs = kwargs
            self.called = True
            self._cleanup()
        finally:
            self._loop.quit()

    def __enter__(self) -> 'CallbackBlocker':
        return self

    def __exit__(self, type, value, traceback) -> None:
        __tracebackhide__ = True
        if value is None:
            # only wait if no exception happened inside the "with" block.
            self.wait()


class CallbackBarrier:
    """
    This class allow to register a callable to be call after an arbitrary
    number of callbacks are called. When using as a context manager `wait`
    is implicitly called when exiting.

    A function should be supplied when creating tha barrier, that function
    will be called when the barrier is "crossed".

    Call "cleanup" after async functions "foo" and "bar" are executed.
    This will not block waiting for any call to complete:

    ```
    with CallbackBarrier(cleanup) as barrier:
        barrier.increment(2)
        foo(result_callback=barrier)
        bar(result_callback=barrier)
    ```

    `CallbackBlocker` can be used in conjunction of `CallbackBarrier`.
    This will block when exiting the context until the "barrier" is called
    twice:

    ```
    with CallbackBlocker() as cb, CallbackBarrier(cb) as barrier:
        barrier.increment(2)
        foo(result_callback=barrier)
        bar(result_callback=barrier)
    ```

    The are 3 major states for a barrier:

    - editing: the barrier can be `increment`ed and `wait`ed;
    - waiting: `increment`s raise errors (barrier not called the expected
        times yet);
    - crossed: the barrier have been `wait`ed on and it has been called the
        expected times already causing the registered function to be called,
        `increment`s and extra call to the barrier raise errors;
    """

    class StoredResult:
        def __init__(self, parent, key):
            # Create a cycle with the parent to prevent the parent collection
            # because parent hold barrier logic.
            self._parent = parent
            self._key = repr(key)
            self._value = None
            self._called = False

        @property
        def value(self) -> Optional[Any]:
            assert self._called, f'stored results key: {self._key}'
            return self._value

        def __call__(self, value: Optional[Any]) -> None:
            if self._called:
                raise RuntimeError('stored result can store only one value')
            self._called = True
            self._value = value

            self._parent(value)
            self._parent = None  # Break the cycle.

    def __init__(self):
        self._waiting_on_barrier = False
        self._crossed = False
        self._calls_pending = 0
        self._stored_results: Dict[Hashable, CallbackBarrier.StoredResult] = {}

        self._to_execute_after_barrier = []

    def register(self, to_call, pass_self=False):
        self._to_execute_after_barrier.append((to_call, pass_self))
        if self._crossed:
            self._cross_barrier()

    def create_stored_result_callback(
        self, key: Hashable
    ) -> 'CallbackBarrier.StoredResult':
        """
        Creates a slot in the barrier to store a call result, this value cen
        be safely queried after the barrie has been crossed.
        """
        if key in self._stored_results:
            raise ValueError(
                'stored result "key" already in use ("key"s should be unique)'
            )
        stored_result = self.StoredResult(self, key)
        self.increment()
        self._stored_results[key] = stored_result
        return stored_result

    def __getitem__(self, item: Hashable) -> 'CallbackBarrier.StoredResult':
        if item in self._stored_results:
            return self._stored_results[item]
        else:
            return self.create_stored_result_callback(item)

    def get_result(self, key: Hashable) -> Optional[Any]:
        return self._stored_results[key].value

    def increment(self, n: int = 1) -> None:
        """
        Increase the number of times the barrier must be called before calling
        the registered function.

        :type n: int
        """
        if self._waiting_on_barrier or self._crossed:
            raise RuntimeError("can't increment barrier after wait")
        if n < 1:
            raise ValueError('`n` should be greater that 0 (zero)')
        self._calls_pending += n

    def wait(self) -> None:
        """
        Puts the barrier in the "waiting" state. If the expected number of
        calls have already been reached "cross" the barrier.
        """
        if self._crossed:
            raise RuntimeError("can't wait on crossed barrier")
        if self._waiting_on_barrier:
            raise RuntimeError("already waiting on barrier")
        if self._calls_pending < 0:
            raise RuntimeError(
                'barrier already called more times than expected'
            )
        self._waiting_on_barrier = True
        if self._calls_pending == 0:
            self._cross_barrier()

    def _cross_barrier(self) -> None:
        self._crossed = True
        self._waiting_on_barrier = False

        to_execute_after_barrier = self._to_execute_after_barrier
        self._to_execute_after_barrier = []
        for to_call, pass_self in to_execute_after_barrier:
            if pass_self:
                to_call(self)
            else:
                to_call()

    def __call__(self, *args: Optional[Any], **kwargs: Optional[Any]) -> None:
        if self._crossed:
            raise RuntimeError('unexpected call after crossing barrier')
        self._calls_pending -= 1
        if self._waiting_on_barrier and self._calls_pending == 0:
            self._cross_barrier()

    def __enter__(self) -> 'CallbackBarrier':
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.wait()


class CallbackCalledTwiceError(Exception):
    """
    The exception raise by `CallbackBlocker` instances if called more
    than once.
    """


def silent_disconnect(signal: pyqtSignal, slot: Callable) -> None:
    """
    Disconnects a signal from a slot, ignoring errors. Sometimes Qt
    might disconnect a signal automatically for unknown reasons.
    """
    from contextlib import suppress
    with suppress(TypeError, RuntimeError):
        if slot is None:
            signal.disconnect()
        else:
            signal.disconnect(slot)
