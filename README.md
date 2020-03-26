PipetteWrapper
-----
The Opentrons API only allowed for use of all 8 channels of the multichannel pipette attachments. PipetteWrapper is used to wrap opentrons multichannel Pipette objects to allow the use of any number of channels while automatically tracking tip usage.

__CURRENTLY REQUIRES A MODIFICATION TO LINE 67 IN `opentrons/api/calibration.py`:__

__CHANGE:__

``inst.pick_up_tip(container._container[0])``

__TO:__

``inst.pick_up_tip(location=container._container[0])``

Installation
-----
1. ssh into opentrons robot
2. Install from pypi: `pip install pipettewrapper`

Example
-----
```
from pipettewrapper import PipetteWrapper
from opentrons import labware, instruments

tip_rack = labware.load('opentrons-tiprack-300ul', slot='4')
pipette = PipetteWrapper(instruments.P50_multi(mount='left', tip_racks=[tip_rack]))
plate = labware.load('96-flat')

pipette.distribute(50, plate.wells('A1'), plate.wells('A2'), num_tips=4)  # Uses 4 tips
pipette.transfer(50, plate.wells('A1'), plate.wells('A2'))  # Default behaviour (8 tips)
```
