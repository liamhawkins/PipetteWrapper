from functools import partial


class NoTipRackError(Exception):
    pass


class TipTracker:
    # TODO: Support multiple tip_racks
    # TODO: Support returning tips
    # TODO: Validate that tiprack/source/destination slot is not going to cause collision
    # TODO: Create automatic mode that would determine number of tips to use from source (?)
    """
    TipTracker tracks the tips used by an 8-channel pipette so it can be used as a single channel. TipTracker.next_tip()
    take n tips as an argument and return location of a tiprack that would result in the pipette picking up that many
    tips
    """
    def __init__(self, tiprack):
        self.tiprack = tiprack
        self.letters = list(reversed(list('ABCDEFGH')))
        self.nums = list(range(1, 12 + 1))
        self.num_rows = len(self.letters)
        self.num_cols = len(self.nums)
        self.rack = []

        # Creates tip layout as nested list of lists
        for n in self.nums:
            col = []
            for l in self.letters:
                col.append('{}{}'.format(l, n))
            self.rack.append(col)

    def __str__(self):
        for i in range(self.num_rows):
            row = []
            for col in self.rack:
                row.append(col[-i-1])
            print(row)

    def next_tip(self, n=1):
        """
        Returns location on tiprack that would result in pipette picking up n tips when passed as location parameter to
        Pipette.pick_up_tip()

        Parameters
        ----------
        n: int
            Number of tips to pick up

        Returns
        -------
        location
            Location on tiprack that would result in pipette picking up n tips
        """
        assert n <= 8, "Cannot pick up more than 8 tips"
        for i in range(self.num_cols):
            for j in list(range(self.num_rows)):
                # Scan up columns until n non-empty tips are found
                try:
                    self.rack[i][j+n-1]
                except IndexError:
                    continue
                tips = self.rack[i][j:j+n]
                # If any tips are empty (None) continue scanning up column or next column
                if any(x is None for x in tips):
                    continue
                else:
                    # When usable tips are found, set them to None and return highest tip in the column
                    for t in range(n):
                        self.rack[i][j+t] = None
                    tip_name = tips[-1]
                    print("\nTaking {} tips".format(n))
                    return self.tiprack.wells(tip_name)


class PipetteWrapper:
    """
    PipetteWrapper is used to wrap opentrons multichannel Pipette objects to allow multichannels to act as single
    channels.

    CURRENTLY REQUIRES A MODIFICATION TO LINE 67 IN opentrons/api/calibration.py:
    CHANGE:
    ``inst.pick_up_tip(container._container[0])``
    TO:
    ``inst.pick_up_tip(location=container._container[0])``

    Example
    -----
    ``from opentrons import labware, instruments``

    ``tip_rack = labware.load('opentrons-tiprack-300ul', slot='4')``

    ``pipette = PipetteWrapper(instruments.P50_multi(mount='left', tip_racks=[tip_rack]))``

    ``plate = labware.load('96-flat')``

    ``pipette.distribute(50, plate.wells('A1'), plate.wells('A2'), num_tips=4)  # Uses 4 tips``

    ``pipette.transfer(50, plate.wells('A1'), plate.wells('A2'))  # Defaults behaviour (8 tips)``
    """
    def __init__(self, pipette):
        # Check that pipette has 8-channels
        if pipette.channels != 8:
            raise ValueError('{} is not an 8-channel pipette'.format(pipette.name))
        self.pipette = pipette

        # Check that pipette has been defined with a tip_rack
        self.tip_racks = self.pipette.tip_racks
        if not self.tip_racks:
            raise NoTipRackError('Pipette object must be defined with tip_racks')
        if len(self.tip_racks) > 1:
            raise NotImplementedError("Support for multiple tipracks has not been implemented")
        self.tiptracker = TipTracker(self.tip_racks[0])

    def __getattr__(self, name):
        """
        Pass through calls for methods and attributes from self.pipette object. If `name` is callable (method)
        monkey patch self.pipette.pick_up_tip with location defined by TipTracker object according to how many
        tips were requested by `num_tips` parameter. Any self.pipette method that uses `pick_up_tip` will be affected.
        Not passing num_tips results in default pipette behaviour (8 tips)

        Parameters
        ----------
        name: str
            Name of attribute or method for self.pipette object

        Returns
        -------
        any
            Attribute from self.pipette or method with monkey patched self.pipette.pick_up_tip
        """
        if name == 'return_tip':
            raise NotImplementedError('Returning tip has not been implemented yet')
        if not callable(getattr(self.pipette, name)):
            # If not a method, pass attribute through
            return getattr(self.pipette, name)
        else:
            # If a method is called, monkeypatch `pick_up_tip` with location that would pick up a specific number of
            # tips specified by num_tips kwarg
            def method(*args, **kwargs):
                if 'num_tips' in kwargs:
                    num_tips = kwargs['num_tips']
                    kwargs.pop('num_tips')  # pop 'num_tips' so that pick_up_tips() can be used directly
                else:
                    num_tips = 8
                location = self.tiptracker.next_tip(n=num_tips)
                self.pipette.pick_up_tip = partial(self.pipette.pick_up_tip, location=location)
                return getattr(self.pipette, name)(*args, **kwargs)
            return method