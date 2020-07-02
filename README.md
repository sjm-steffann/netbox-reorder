# NetBox plugin to order interfaces more intuitively

> :warning: **This plugin hacks into NetBox**: This plugin definitely does not follow the supported plugin protocol, and can break NetBox!

## Compatibility

This plugin in compatible with [NetBox](https://netbox.readthedocs.org/) 2.8. Because of the way this plugin hacks into the internals of NetBox compatibility with other versions is not guaranteed.

## Installation

First, add `netbox_reorder` to your `/opt/netbox/local_requirements.txt` file. Create it if it doesn't exist.

If you are using a local version of the plugin, for example for development, add `-e /opt/path/to/plugin` instead.

Then enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`, like:

```python
PLUGINS = [
    'netbox_reorder',
]
```

And finally run `/opt/netbox/upgrade.sh`. This will download and install the plugin and update the database when necessary. Don't forget to run `sudo systemctl restart netbox netbox-rq` like `upgrade.sh` tells you!

## Usage

This plugin overrides the default interface sorting algorithm of NetBox.

### Ordering of mixed interface type names

Some devices (for example Juniper switches) can have mixed interface type names. By default NetBox orders these as follows:

- ge-0/0/1
- ge-0/0/3
- xe-0/0/0
- xe-0/0/2
- xe-0/0/4
- ge-0/1/1
- ge-0/1/3
- xe-0/1/0
- xe-0/1/2
- xe-0/1/4

This is because the interface type (`ge` or `xe`) has precedence over the last part of the interface name. This makes sense when using certain Cisco equipment that has both FastEthernet and GigabitEthernet interfaces with the same numbers:

- FastEthernet0/0
- FastEthernet0/1
- GigabitEthernet0/0
- GigabitEthernet0/1

NetBox has consciously chosen this sorting algorithm. This plugin implements an alternative more intuitive algorithm where the ordering will be:

- xe-0/0/0
- ge-0/0/1
- xe-0/0/2
- ge-0/0/3
- xe-0/0/4
- xe-0/1/0
- ge-0/1/1
- xe-0/1/2
- ge-0/1/3
- xe-0/1/4

The downside is that Cisco equipment with duplicate ports numbers will be less intuitive:

- FastEthernet0/0
- GigabitEthernet0/0
- FastEthernet0/1
- GigabitEthernet0/1

### Ordering of virtual chassis interfaces

NetBox orders interfaces first by device name and then by name. This can cause interfaces in a virtual chassis to appear in an unexpected order. Consider for example the following virtual chassis:

| Device Name | Position | Interface names |
|-------------|----------|-----------------|
| one         | 1        | xe-1/x/y        |
| two         | 2        | xe-2/x/y        |
| three       | 3        | xe-3/x/y        |

When viewing the virtual chassis the intuitive order of interfaces would be first `xe-1/x/y`, then `xe-2/x/y` and finally `xe-3/x/y`.

However, because NetBox by default sorts first on device name, the order will be first `xe-1/x/y`, then `xe-3/x/y` and finally `xe-2/x/y`.

Why? Because "three" comes before "two" alphabetically.

This plugin patches NetBox to implement the intuitive order.
