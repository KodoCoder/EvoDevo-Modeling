
# ### Code ###
from part import Part, BodyPart, JointPart, NeuronPart, SensorPart, WirePart


def update_cycles(parts_developing):
    """Updates all proto-parts, in series (step-by-step).

    When proto-part is fully developed, this function removes the part
    from parts_developing and places it into parts_built.  If the part
    cannot develope fully, it is discarded"""
    parts_built = []
    while(parts_developing):
        count = 0
        for i in parts_developing:
            # Check for non-producing proto-parts, and if they are all
            # that is left, end development.
            if i.regulators_per_update == 0:
                count += 1
                i._diffusion()
                if count == len(parts_developing):
                    parts_developing.remove(i)
                    count -= 1
            # Check if proto-part is done with development, and take out
            # of the update_cycles if it is.
            elif (i.capacity <= (i.regulatory_elements +
                                 i.regulators_per_update)):
                i.set_characteristics()
                parts_built.append(i)
                parts_developing.remove(i)
            # Otherwise, keep updating
            else:
                i.update()
                i._diffusion()
    return parts_built
