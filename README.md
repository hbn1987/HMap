# HMap

Towards Comprehensive and Efficient Internet-wide Scan in IPv6 & IPv4 Networks.

## Description

*HMapc* has undergone an enhancement from its predecessors, XMap and ZMap. This C implementation of HMap, i.e., HMap v2.0, can swiftly discover IPv6 end-hosts and peripherals. Combined with Gasser et al.'s hitlist, HMap's TGA (Target Generation Algorithm) can further comprehensively scan IPv6 networks.

*Yarrp* is an efficent route interface discovery tool designed for rapid mapping at Internet scales.

Access the IPv6 hitlists gathered by HMap by visiting [HMap Hitlists](http://175.6.54.250/ipv6)

With banner grab and TLS handshake tool, [ZGrab2](https://github.com/zmap/zgrab2), more involved scans could be performed.

## Installation

Please install [HMapc] and [Yarrp] before use.

## Usage

```shell
./runner.sh
```

## Reference

### Prober
>X. Li, B. Liu, X. Zheng, H. Duan, Q. Li, and Y. Huang, “Fast IPv6 Network Periphery Discovery and Security Implications,” in DSN, 2021.

>Z. Durumeric, E. Wustrow, J. A. Halderman, E. Wustrow, and J. A. Halderman, “ZMap: Fast Internet-wide scanning and Its Security Applications,” in USENIX Security, 2013.

>R. Beverly, R. Durairajan, D. Plonka, and J. P. Rohrer, “In the IP of the Beholder: Strategies for Active IPv6 Topology Discovery,” in IMC, 2018.

>R. Beverly, “Yarrp’ing the Internet: Randomized High-Speed Active Topology Discovery,” in IMC, 2016.

### TGA
>B. Hou, Z. Cai, K. Wu, T. Yang, and T. Zhou, “Search in the Expanse: Towards Active and Global IPv6 Hitlists,” in INFOCOM, 2023.

### Hitlists & Aliases
>O. Gasser et al., “Clusters in the Expanse: Understanding and Unbiasing IPv6 Hitlists,” in IMC, 2018.

## License & Copyright

HMap Copyright 2024-2025 Bingnan Hou from NUDT

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See LICENSE for the specific
language governing permissions and limitations under the License.
