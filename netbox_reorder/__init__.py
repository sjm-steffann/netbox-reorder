VERSION = '1.0'

try:
    from extras.plugins import PluginConfig
except ImportError:
    # Dummy for when importing outside of netbox
    class PluginConfig:
        pass


class NetBoxReorderConfig(PluginConfig):
    name = 'netbox_reorder'
    verbose_name = 'GitLab Reorder'
    version = VERSION
    author = 'Sander Steffann'
    author_email = 'sander@isp.solcon.nl'
    description = 'Order interfaces more intuitively'
    base_url = 'reorder'
    required_settings = []
    default_settings = {}

    def ready(self):
        super().ready()

        from netbox_reorder.ordering import naturalize_interface as new_naturalize_interface
        from netbox_reorder.ordering import vc_interfaces as new_vc_interfaces

        # Patch the ordering algorithm
        import utilities.ordering
        utilities.ordering.naturalize_interface = new_naturalize_interface

        # Patch the model fields
        from dcim.models import Interface, InterfaceTemplate
        Interface._meta.get_field('_name').naturalize_function = new_naturalize_interface
        InterfaceTemplate._meta.get_field('_name').naturalize_function = new_naturalize_interface

        # Patch the vc_interfaces ordering
        from dcim.models import Device
        setattr(Device, 'vc_interfaces', property(new_vc_interfaces))


config = NetBoxReorderConfig
