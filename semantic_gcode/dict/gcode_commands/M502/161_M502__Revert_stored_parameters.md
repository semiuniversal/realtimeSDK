## M502: Revert stored parameters

### Examples

M502

### Description

This sets all machine parameters to the values defined in config.g, ignoring the config-override.g file so that any changes that were saved by M500 are not applied. It does this by running config.g but ignoring any M501 commands that it contains.

M502 does not clear or reset the config-override.g file; so next time the machine is started, the values that were saved by M500 will once again be applied. If you want to cancel the changes saved by M500 permanently, you can run M502 and then M500.

