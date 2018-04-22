# Cisco UCS and ACI Integration Script (FUSE)


### Overview
Cisco ACI and UCS currently have no integration between each other, so when a Vlan is trunked on an
ACI Leaf port that is connected to an UCS Fabric Interconnect the Vlan creation is not propagated
into UCS. A manual configuration on UCS is needed to create the VLAN, assign it to the north bound ports and the VNIC
must be completed by an UCS administrator. This is not very efficent unless you have a very robust automation teir
that sits above ACI and UCS. This script closes the gap and provides some level of integration depending on whether
you are implementing VMM integration vs baremetal.

##### VMM Integration
Starting with VMware integration - This script will create Vlan(s), assign the Vlan(s) to the northbound interfaces as well as
VNICs associated to the DVS uplink ports.


##### Baremetal Blades / C-Series
Integration is a little more difficult with baremetal because of the lack of information provided to ACI, so the only
thing currently available from an integration aspect is creating the VLANs on the Fabric Interconnections and applying them
to the northbound intefaces. There is no visibility into the actual VNIC on the baremetal server.

The following versions have been used during the testing of these scripts. There are some
scripts that use additional libraries and will be noted.

#### Requirements

APIC Versions Tested:

	3.1(1i) - Inital tested release.

UCSM Version Tested:

    3.2(2d) - Initial tested release.

** Just a note on the tested versions - We do not leverage any SDK for the connectivity, queries of ACI and UCS. All connectivity
is through the UCS XML API and ACI REST calls.

