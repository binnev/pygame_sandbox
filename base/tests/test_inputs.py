from base.inputs.gamecube import create_mapping


def test_create_mapping():
    joystick_map = create_mapping((0, 0.86), (0, 1), limit_output=True)
    assert joystick_map(0) == 0
    assert joystick_map(0.86) == 1
    assert joystick_map(1) == 1
    assert joystick_map(-0.5) == 0

    trigger_map = create_mapping((-0.4, 0.98), (0, 1), limit_output=True)
    assert trigger_map(-0.4) == 0
    assert trigger_map(-0.7) == 0
    assert trigger_map(0.98) == 1
    assert trigger_map(3) == 1
    assert 0 < trigger_map(0.5) < 1
