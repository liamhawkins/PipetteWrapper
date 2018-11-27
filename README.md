PipetteWrapper is used to wrap opentrons multichannel Pipette objects to allow multichannels to act as single channels.

__CURRENTLY REQUIRES A MODIFICATION TO LINE 67 IN `opentrons/api/calibration.py`:__

__CHANGE:__

``inst.pick_up_tip(container._container[0])``

__TO:__

``inst.pick_up_tip(location=container._container[0])``

Example
-----
```
from opentrons import labware, instruments
tip_rack = labware.load('opentrons-tiprack-300ul', slot='4')
pipette = PipetteWrapper(instruments.P50_multi(mount='left', tip_racks=[tip_rack]))
plate = labware.load('96-flat')
pipette.distribute(50, plate.wells('A1'), plate.wells('A2'), num_tips=4)
```