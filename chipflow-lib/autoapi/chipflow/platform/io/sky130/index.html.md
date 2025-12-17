# chipflow.platform.io.sky130

Sky130-specific IO definitions.

## Classes

| [`Sky130DriveMode`](#chipflow.platform.io.sky130.Sky130DriveMode)   | Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html))   |
|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## Module Contents

### *class* chipflow.platform.io.sky130.Sky130DriveMode

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html))
These are both statically configurable and can be set at runtime on the :py:mod:drive_mode.Sky130Port lines on the port.
