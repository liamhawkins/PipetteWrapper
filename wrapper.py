from functools import partial


class TipTracker:
    def __init__(self, tiprack=None):
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

    def print_rack(self):
        for i in range(self.num_rows):
            row = []
            for col in self.rack:
                row.append(col[-i-1])
            print(row)

    def next_tip(self, n=1):
        assert n <= 8, "Cannot pick up more than 8 tips"
        for i in range(self.num_cols):
            for j in list(range(self.num_rows)):
                try:
                    self.rack[i][j+n-1]
                except IndexError:
                    continue
                tips = self.rack[i][j:j+n]
                if any(x is None for x in tips):
                    continue
                else:
                    for t in range(n):
                        self.rack[i][j+t] = None
                    tip_name = tips[-1]
                    print("\nTaking {} tips".format(n))
                    return self.tiprack.wells(tip_name)


class PipetteWrapper:
    def __init__(self, pipette):
        self.pipette = pipette
        self.tip_racks = self.pipette.tip_racks
        self.tiptracker = TipTracker(self.tip_racks[0])

    def __getattr__(self, name):
        if not callable(getattr(self.pipette, name)):
            return getattr(self.pipette, name)
        else:
            def method(*args, **kwargs):
                if 'num_tips' in kwargs:
                    num_tips = kwargs['num_tips']
                else:
                    num_tips = 8
                location = self.tiptracker.next_tip(n=num_tips)
                self.pipette.pick_up_tip = partial(self.pipette.pick_up_tip, location=location)
                return getattr(self.pipette, name)(*args, **kwargs)
            return method