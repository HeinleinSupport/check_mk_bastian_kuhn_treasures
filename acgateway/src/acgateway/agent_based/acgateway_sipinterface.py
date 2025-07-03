#!/usr/bin/env python3

"""
Kuhn & Rueß GmbH
Consulting and Development
https://kuhn-ruess.de
"""

from cmk.agent_based.v2 import (
    all_of,
    contains,
    register,
    render,
    Metric,
    OIDEnd,
    Result,
    Service,
    SNMPTree,
    State,
)

def _item_acgateway_sipinterface(line):
    return "%s %s" % (line[0], line[10])

def _find_line(idx, lines):
    for line in lines:
        if line[0] == idx:
            return line

def parse_acgateway_sipinterface(string_table):
    rowStatus = {
        '1': 'active',
        '2': 'notInService',
        '3': 'notReady',
    }
    sipInterfaceApplicationType = {
        '0': 'gwIP2IP',
        '1': 'sas',
        '2': 'sbc',
        }
    sysInterfaceApplicationType = {
        '0': 'oam',
        '1': 'media',
        '2': 'control',
        '3': 'oamAndMedia',
        '4': 'oamAndControl',
        '5': 'mediaAndControl',
        '6': 'oamAndMediaAndControl',
        '99': 'maintenance',
        }
    sysInterfaceMode = {
        '3': 'IPv6PrefixManual',
        '4': 'IPv6Manual',
        '10': 'IPv4Manual',
        }
    section = {}
    for line in string_table[0]:
        item = _item_acgateway_sipinterface(line)
        section[item] = {
            'siprowstatus': rowStatus.get(line[1], 'unknown'),
            'sipapptype': sipInterfaceApplicationType.get(line[5], 'unknown'),
            'udpport': line[6],
            'tcpport': line[7],
            'tlsport': line[8],
            'name': line[10]
        }
        if line[4].startswith('.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.22.1.11.'):
            idx = line[4][43:]
            sysiface = _find_line(idx, string_table[1])
            if sysiface:
                section[item].update({
                    'sysrowstatus': rowStatus.get(sysiface[1], 'unknown'),
                    'sysapptype': sysInterfaceApplicationType.get(sysiface[2], 'unknown'),
                    'sysmode': sysInterfaceMode.get(sysiface[3], 'unknown'),
                    'sysip': "%s/%s" % (sysiface[4], sysiface[5]),
                    'sysgateway': sysiface[6],
                    'sysvlan': sysiface[7],
                    'sysname': sysiface[8]
                })
                if sysiface[12].startswith('.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.26.1.7.'):
                    idx = sysiface[12][42:]
                    device = _find_line(idx, string_table[2])
                    if device:
                        section[item].update({
                            'devrowstatus': rowStatus.get(device[1], 'unknown'),
                            'devvlan': device[4],
                            'devname': device[5]
                        })
    return section

snmp_section_acgateway_sipinterface = SimpleSNMPSection(
    name = "acgateway_sipinterface",
    parse_function = parse_acgateway_sipinterface,
    fetch=[
        SNMPTree(
            base = '.1.3.6.1.4.1.5003.9.10.3.1.1.27.21.1',
            oids = [
                '1',  # 0  AcGateway::sipInterfaceIndex
                '2',  # 1  AcGateway::sipInterfaceRowStatus
                '3',  # 2  AcGateway::sipInterfaceAction
                '4',  # 3  AcGateway::sipInterfaceActionResult
                '5',  # 4  AcGateway::sipInterfaceNetworkInterface
                '6',  # 5  AcGateway::sipInterfaceApplicationType
                '7',  # 6  AcGateway::sipInterfaceUDPPort
                '8',  # 7  AcGateway::sipInterfaceTCPPort
                '9',  # 8  AcGateway::sipInterfaceTLSPort
                '10', # 9  AcGateway::sipInterfaceSRD
                '11', # 10 AcGateway::sipInterfaceInterfaceName
            ]
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.22.1',
            oids = [
                OIDEnd(),
                '2',  # 1  AC-SYSTEM-MIB::acSysInterfaceRowStatus
                '5',  # 2  AC-SYSTEM-MIB::acSysInterfaceApplicationTypes
                '6',  # 3  AC-SYSTEM-MIB::acSysInterfaceMode
                '7',  # 4  AC-SYSTEM-MIB::acSysInterfaceIPAddress
                '8',  # 5  AC-SYSTEM-MIB::acSysInterfacePrefixLength
                '9',  # 6  AC-SYSTEM-MIB::acSysInterfaceGateway
                '10', # 7  AC-SYSTEM-MIB::acSysInterfaceVlanID
                '11', # 8  AC-SYSTEM-MIB::acSysInterfaceName
                '12', # 9  AC-SYSTEM-MIB::acSysInterfacePrimaryDNSServerIPAddress
                '13', # 10 AC-SYSTEM-MIB::acSysInterfaceSecondaryDNSServerIPAddress
                '14', # 11 AC-SYSTEM-MIB::acSysInterfaceUnderlyingInterface
                '15', # 12 AC-SYSTEM-MIB::acSysInterfaceUnderlyingDevice
            ]
        ),
        SNMPTree(
            base = '.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.26.1',
            oids = [
                OIDEnd(),
                '2',  # 1  AC-SYSTEM-MIB::acSysEthernetDeviceRowStatus
                '3',  # 2  AC-SYSTEM-MIB::acSysEthernetDeviceAction
                '4',  # 3  AC-SYSTEM-MIB::acSysEthernetDeviceActionRes
                '5',  # 4  AC-SYSTEM-MIB::acSysEthernetDeviceVlanID
                '7',  # 5  AC-SYSTEM-MIB::acSysEthernetDeviceName
            ]
        ),
    ],
    detect = all_of(
        contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.5003.8.1.1"),
        contains(".1.3.6.1.2.1.1.1.0", "SW Version: 7.20A"),
    ),
)

def discover_acgateway_sipinterface(section):
    for item, data in section.items():
        yield Service(item=item,
                      parameters={
                          'siprowstatus': data.get('siprowstatus'),
                          'sysrowstatus': data.get('sysrowstatus'),
                          'devrowstatus': data.get('devrowstatus'),
                      })

def check_acgateway_sipinterface(item, params, section):
    if item in section:
        data = section[item]
        yield Result(state=State.OK,
                     summary='SIP application type: %s' % data['sipapptype'])
        yield Result(state=State.OK,
                     summary='system interface %s on device %s' % (data.get('sysname'), data.get('devname')))
        if data['udpport'] != '0':
            proto = 'UDP'
            port = data['udpport']
        if data['tcpport'] != '0':
            proto = 'TCP'
            port = data['tcpport']
        if data['tlsport'] != '0':
            proto = 'TLS'
            port = data['tlsport']
        yield Result(state=State.OK,
                     summary='%s port %s' % (proto, port))
        if 'sysip' in data:
            yield Result(state=State.OK,
                         summary=data['sysip'])
        if 'sysgateway' in data and data['sysgateway']:
            yield Result(state=State.OK,
                         summary='gateway: %s' % data['sysgateway'])
        for param, value in params.items():
            if value != data.get(param):
                yield Result(state=State.CRIT,
                             summary='%s is %s' % (param, data.get(param)))

check_plugin_acgateway_sipinterface = CheckPlugin(
    name = "acgateway_sipinterface",
    service_name = "SIP Interface %s",
    discovery_function = discover_acgateway_sipinterface,
    check_function = check_acgateway_sipinterface,
    check_default_parameters = {},
)
