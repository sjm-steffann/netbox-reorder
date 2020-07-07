import re

from django.db.models.query_utils import Q

from dcim.models import Interface
from utilities.ordering import INTERFACE_NAME_REGEX, naturalize
from utilities.query_functions import CollateAsChar


def naturalize_interface(value, max_length):
    """
    Similar in nature to naturalize(), but takes into account a particular naming format adapted from the old
    InterfaceManager.

    :param value: The value to be naturalized
    :param max_length: The maximum length of the returned string. Characters beyond this length will be stripped.
    """
    match = re.search(INTERFACE_NAME_REGEX, value)
    if match is None:
        return value

    matches = match.groupdict()

    # Add padding
    for part in ('slot', 'subslot', 'position', 'subposition'):
        matches[part] = matches[part].rjust(4, '0') if matches[part] else '9999'

    for part in ('id', 'channel', 'vc'):
        matches[part] = matches[part].rjust(6, '0') if matches[part] else '......'

    matches['type'] = matches['type'] or ''
    matches['remainder'] = matches['remainder'] or ''

    # Apply heuristics to interface type
    if matches['type'].lower() in ('vl', 'vlan'):
        matches['slot'] = '9996'
    if matches['type'].lower() in ('lo', 'loopback'):
        matches['slot'] = '9997'
    if matches['type'].lower() in ('ae', 'po', 'port-channel'):
        matches['slot'] = '9998'

    # Format output
    output = (matches['slot'] + matches['subslot'] + matches['position'] + matches['subposition'] + matches['id'] +
              matches['type'] + matches['channel'] + matches['vc'])

    # Finally, naturalize any remaining text and append it
    if matches['remainder'] and len(output) < max_length:
        remainder = naturalize(matches['remainder'], max_length - len(output))
        output += remainder

    return output[:max_length]


def vc_interfaces(self):
    """
    Return a QuerySet matching all Interfaces assigned to this Device or, if this Device is a VC master, to another
    Device belonging to the same VirtualChassis.
    """
    filter = Q(device=self)
    if self.virtual_chassis and self.virtual_chassis.master == self:
        filter |= Q(device__virtual_chassis=self.virtual_chassis, mgmt_only=False)
    return Interface.objects.filter(filter).order_by(CollateAsChar('_name'))
