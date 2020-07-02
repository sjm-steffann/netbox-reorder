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
    output = ''
    match = re.search(INTERFACE_NAME_REGEX, value)
    if match is None:
        return value

    # First, we order by slot/position, padding each to four digits. If a field is not present,
    # set it to 9999 to ensure it is ordered last.
    for part_name in ('slot', 'subslot', 'position', 'subposition', 'id'):
        part = match.group(part_name)
        if part is not None:
            output += part.rjust(4, '0')
        else:
            output += '9999'

    # Append the type, if any.
    if match.group('type') is not None:
        output += match.group('type')

    # Append any remaining fields, left-padding to six digits each.
    for part_name in ('channel', 'vc'):
        part = match.group(part_name)
        if part is not None:
            output += part.rjust(6, '0')
        else:
            output += '......'

    # Finally, naturalize any remaining text and append it
    if match.group('remainder') is not None and len(output) < max_length:
        remainder = naturalize(match.group('remainder'), max_length - len(output))
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
