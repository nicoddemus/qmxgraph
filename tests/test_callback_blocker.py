import pytest

from qmxgraph.callback_blocker import CallbackBarrier


@pytest.mark.parametrize('pass_self', [True, False])
@pytest.mark.parametrize('n_calls', [1, 4, 7])
def test_callback_barrier_context_manager_call_before_wait(
    mocker, pass_self, n_calls
):
    stub = mocker.Mock()
    with CallbackBarrier(stub, pass_self) as barrier:
        barrier.increment(n_calls)
        # Calls inside context manager.
        for _ in range(n_calls):
            barrier()
        assert stub.call_count == 0
    assert stub.call_count == 1
    if pass_self:
        assert stub.call_args == ((barrier,), {})
    else:
        assert stub.call_args == ((), {})


@pytest.mark.parametrize('pass_self', [True, False])
@pytest.mark.parametrize('n_calls', [1, 4, 7])
def test_callback_barrier_context_manager_call_after_wait(
    mocker, pass_self, n_calls
):
    stub = mocker.Mock()
    with CallbackBarrier(stub, pass_self) as barrier:
        barrier.increment(n_calls)
        assert stub.call_count == 0
    assert stub.call_count == 0
    # Calls outside context manager.
    for _ in range(n_calls):
        barrier()
    assert stub.call_count == 1
    if pass_self:
        assert stub.call_args == ((barrier,), {})
    else:
        assert stub.call_args == ((), {})


@pytest.mark.parametrize('n_calls', [1, 4, 7])
def test_callback_barrier_no_context_manager(
    mocker, n_calls
):
    stub = mocker.Mock()
    barrier = CallbackBarrier(stub)
    barrier.increment(n_calls)
    for _ in range(n_calls):
        barrier()
    assert stub.call_count == 0
    barrier.wait()
    assert stub.call_count == 1


def test_callback_barrier_no_expected_calls(mocker):
    stub = mocker.Mock()
    with CallbackBarrier(stub):
        assert stub.call_count == 0
    assert stub.call_count == 1


def test_callback_barrier_stored_result(mocker):
    stub = mocker.Mock()
    with CallbackBarrier(stub, True) as barrier:
        barrier.increment(2)
        foo = barrier['foo']
        bar = barrier['bar']
        assert stub.call_count == 0

    barrier(1, 2)
    assert stub.call_count == 0
    foo(7)
    assert stub.call_count == 0
    bar('blue')
    assert stub.call_count == 0
    barrier('a', 'b')
    assert stub.call_count == 1
    assert stub.call_args == ((barrier,), {})
    assert barrier['foo'].value == 7
    assert barrier['bar'].value == 'blue'


def test_callback_barrier_error_increment_after_wait(mocker):
    stub = mocker.Mock()
    with CallbackBarrier(stub, True) as barrier:
        barrier.increment()
        barrier.create_stored_result_callback('foo')
        assert stub.call_count == 0

    with pytest.raises(
        RuntimeError, match="can't increment barrier after wait"
    ):
        barrier.increment()

    with pytest.raises(
        RuntimeError, match="can't increment barrier after wait"
    ):
        barrier.create_stored_result_callback('bar')


def test_callback_barrier_error_call_on_crossed_barrier(mocker):
    stub = mocker.Mock()
    with CallbackBarrier(stub, True) as barrier:
        barrier.increment()
        assert stub.call_count == 0
    assert stub.call_count == 0
    barrier()
    assert stub.call_count == 1

    with pytest.raises(
        RuntimeError, match='unexpected call after crossing barrier'
    ):
        barrier()


def test_callback_barrier_error_call_twice_stored_result(mocker):
    stub = mocker.Mock()
    with CallbackBarrier(stub, True) as barrier:
        barrier.create_stored_result_callback('foo')
        assert stub.call_count == 0
    assert stub.call_count == 0
    barrier['foo'](None)
    assert stub.call_count == 1

    with pytest.raises(
        RuntimeError, match='stored result can store only one value'
    ):
        barrier['foo'](None)

