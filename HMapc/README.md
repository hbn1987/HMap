# HMapc

Towards Comprehensive and Efficient Internet-wide Scan in IPv6 & IPv4 Networks.

## Description

*HMapc* has undergone an enhancement from its predecessors, XMap and ZMap. This C implementation of HMap, i.e., HMap v2.0, can swiftly discover IPv6 end-hosts and peripherals. Combined with Gasser et al.'s hitlist, HMap's TGA (Target Generation Algorithm) can further comprehensively scan IPv6 networks.

Furthermore, HMap can dynamically and randomly scan specific networks, such as SpaceX and ISPs, with any prefix length and subnets, like 2001:db8::/32-64 and 192.168.0.1/16-20. Moreover, HMap supports simultaneous scanning of multiple ports.

Access the IPv6 hitlists gathered by HMap by visiting [HMap Hitlists](http://175.6.54.250/ipv6)

With banner grab and TLS handshake tool, [ZGrab2](https://github.com/zmap/zgrab2), more involved scans could be performed.

## Installation

HMap operates on GNU/Linux and BSD.

### Dependencies

HMap has the following dependencies:

- [CMake](http://www.cmake.org/) - Cross-platform, open-source build system
- [GMP](http://gmplib.org/) - Free library for arbitrary precision arithmetic
- [gengetopt](http://www.gnu.org/software/gengetopt/gengetopt.html) - Command line option parsing for C programs
- [libpcap](http://www.tcpdump.org/) - Famous user-level packet capture library
- [flex](http://flex.sourceforge.net/) and [byacc](http://invisible-island.net/byacc/) - Output filter lexer and parser generator
- [json-c](https://github.com/json-c/json-c/) - JSON implementation in C
- [libunistring](https://www.gnu.org/software/libunistring/) - Unicode string library for C
- [libdnet](https://github.com/dugsong/libdnet) - (macOS Only) Gateway and route detection
- [hiredis](https://github.com/redis/hiredis) - RedisDB support in C

Install the required dependencies with the following commands.

* On Debian-based systems (including Ubuntu):
   ```sh
   sudo apt-get install build-essential cmake libgmp3-dev gengetopt libpcap-dev flex byacc libjson-c-dev pkg-config libunistring-dev libcurl4-openssl-dev

   ```

* On RHEL- and Fedora-based systems (including CentOS):
   ```sh
   sudo yum install cmake gmp-devel gengetopt libpcap-devel flex byacc json-c-devel libunistring-devel
   libcurl4-openssl-dev
   ```

### Building & Installing

  ```sh
  cmake .
  make -j4
  make install
  ```

### Development Notes

- Enabling development turns on debug symbols, and turns off optimizations.
  Release builds should be built with `-DENABLE_DEVELOPMENT=OFF`.

- Enabling `log_trace` can have a major performance impact and should not be used
  except during early development. Release builds should be built with `-DENABLE_LOG_TRACE=OFF`.

- Redis support is not enabled by default. If you want to use XMap with Redis,
  you will first need to install hiredis. Then run cmake with `-DWITH_REDIS=ON`.
  Debian/Ubuntu has packaged hiredis as `libhiredis-dev`; Fedora and RHEL/CentOS
  have packaged it as `hiredis-devel`.

- Building packages for some systems like Fedora and RHEL requires a user-definable
  directory (buildroot) to put files. The way to respect this prefix is to run cmake
  with `-DRESPECT_INSTALL_PREFIX_CONFIG=ON`.

- Manpages (and their HTML representations) are generated from the `.ronn` source
  files in the repository, using the [ronn](https://github.com/rtomayko/ronn) tool.
  This does not happen automatically as part of the build process; to regenerate the
  man pages you'll need to run `make manpages`. This target assumes that `ronn` is
  in your PATH.

- Building with some versions of CMake may fail with `unable to find parser.h`.
  If this happens, try updating CMake. If it still fails, don't clone HMap into a
  path that contains the string `.com`, and try again.

- HMap may be installed to an alternative directory, with the `CMAKE_INSTALL_PREFIX`
  option. For example, to install it in `$HOME/opt` run
    ```sh
    cmake -DCMAKE_INSTALL_PREFIX=$HOME/opt .
    make -j4
    make install
    ```

## Usage

### Synopsis

hmap [ -4 | -6 ] [ -x &lt;len&gt; ] [ -p &lt;port&gt; ] [ -o &lt;outfile&gt; ] [ OPTIONS... ] [ ip|domain|range ]

### Options

   * `-6`, `--ipv6`:
     Scanning the IPv6 networks (default).

   * `-4`, `--ipv4`:
     Scanning the IPv4 networks.

   * `-x`, `--max-len=len`:
     Max IP bit length to scan (default = `32`).

   * `ip`|`domain`|`range`:
     IP addresses or DNS hostnames to scan. Accept IP ranges in CIDR block notation. Max length of domains is 256, e.g, 2001::/64, 192.168.0.1/16, and www.qq.com/32. Default to `::/0` and `0.0.0.0/0`.
     
   * `-p`, `--target-port=port|range`:
     TCP or UDP port(s) number to scan (for SYN scans and basic UDP scans). Accepts port ranges with `,` and `-`, e.g., `80,443,8080-8081`. With `--target-port`, one target is a **<ip/x, port>**.

   * `-P`, `--target-index=num`:
     Payload number to scan. With `--target-index`, one target is a **<ip/x, (port), index>**.

   * `-o`, `--output-file=name`:
     When using an output module that uses a file, write results to this file. Use `-` for stdout.
     
   * `-b`, `--blacklist-file=path`:
     File of subnets to exclude, accept DNS hostnames, in CIDR notation, one-per line. It is recommended you use this to exclude RFC 1918 addresses, multicast, IANA reserved space, and other IANA special-purpose addresses. An example blacklist file **blacklist4.conf** for this purpose.
     
   * `-w`, `--whitelist-file=path`:
     File of subnets to include, accept DNS hostnames, in CIDR notation, one-per line. Specifying a whitelist file is equivalent to specifying to ranges directly on the command line interface, but allows specifying a large number of subnets. **Note**: if you are specifying a large number of individual IP addresses (more than 1 million), you should instead use `--list-of-ips-file`. An example whitelist file **whitelist6.conf** for this purpose.
     
   * `-I`, `--list-of-ips-file=path`:
     File of individual IP addresses to scan, one-per line. This feature allows you to scan a large number of unrelated addresses. If you have a small number of IPs, it is faster to specify these on the command line or by using `--whitelist-file`. **Note**: this should only be used when scanning more  than 1 million addresses. When used in with `--whitelist-file`, only hosts in the intersection of both sets will be scanned. Hosts specified here, but included in the `--blacklist-file` will be excluded.

   * `-R`, `--rate=pps`:
     Set the send rate in pkts/sec. Note: when combined with `--probes` or `--retries`,  this is total packets per second, not target number per second. Setting the rate to `0` will scan at full line rate (no sleep). Default to `100K` pps.
     
   * `-B`, `--bandwidth=bps`:
     Set the send rate in bits/sec (supports suffixes G/g, M/m, and K/k, e.g. -B 10M for 10 mbps). This overrides the `--rate` flag. Default to `0` bps.
     
   * `--batch=num`:
     Number of packets to send in a burst between checks to the ratelimit. A batch size above 1 allows the sleep-based rate-limiter to be used with proportionally higher rates. This can reduce CPU usage, in exchange for a bursty send rate (default = `1`).
     
   * `--probes=num`:
     Number of probes to send to each target (default = `1`).
     
   * `--retries=num`:
     Number of times to try resending a packet if the sendto call fails (default = `1`).
     
   * `-n`, `--max-targets=num`:
     Capture number of targets to probe (default = `-1`).
     
   * `-k`, `--max-packets=num`:
     Capture number of packets to send (default = `-1`).
     
   * `-t`, `--max-runtime=secs`:
     Capture length of time for sending packets (default = `-1`).
     
   * `-N`, `--max-results=num`:
     Exit after receiving this many results (default = `-1`).

   * `-E`, `--est-elements=num`:
     Estimated number of results for unique (default = `5e8`). **Note**: HMap uses the bloomfilter to check the duplicate results, which costs some of the memory. Choose the proper `--est-elements` to adapt to your memory capacity.
     
   * `-c`, `--cooldown-secs=secs`:
     How long to continue receiving after sending has completed (default = `5`).
     
   * `-e`, `--seed=num`:
     Seed used to select address permutation and generate random probe validation msg. Use this if you want to scan addresses in the same order and generate the same probe validation msg for multiple HMap runs (default = `0`).
     
   * `--shards=num`:
     Split the scan up into N shards/partitions among different instances of hmap (default = `1`). When sharding, `--seed` is required.
     
   * `--shard=num`:
     Set which shard to scan (default = `0`). Shards are 0-indexed in the range [0, N), where N is the total number of shards. When sharding`--seed` is required.

   * `-s`, `--source-port=port|range`:
     Source port(s) to send packets from. Accept port ranges with `-`, e.g., `12345-54321`. Default to `32768-61000`.

   * `-S`, `--source-ip=ip|range`:
     Source address(es) to send packets from. Either single IP or range. Accept ip ranges with `,` and `-` (max=`1024`), e.g., 2001::1, 2001::2-2001::10.
     
   * `-G`, `--gateway-mac=mac`:
     Gateway MAC address to send packets to (in case auto-detection fails).

   * `--source-mac=mac`:
     Source MAC address to send packets from (in case auto-detection fails).

   * `-i`, `--interface=name`:
     Network interface to use.

   * `-X`, `--iplayer`:
     Send IP layer packets instead of ethernet packets (for non-Ethernet interface).

   * `--list-probe-modules`:
     List available probe modules (e.g., tcp_syn).

   * `-M`, `--probe-module=name`:
     Select probe module (default = `icmp_echo`).

   * `--probe-args=args`:
     Arguments to pass to probe module.

   * `--probe-ttl=hops`:
     Set TTL value for probe IP packets (default = `255`).

   * `--list-output-fields`:
     List the fields the selected probe module can send to the output module.

   * `--list-output-modules`:
     List available output modules (e.g., csv).

   * `-O`, `--output-module=name`:
     Select output module (default = `csv`).

   * `--output-args=args`:
     Arguments to pass to output module.

   * `-f`, `--output-fields=fields`:
     Comma-separated list of fields to output. Accept fields with `,` and `*`.

   * `--output-filter`:
     Specify an output filter over the fields defined by the probe module. See the output filter section for more details.

   * `--list-iid-modules`:
     List available iid modules (e.g., low).

   * `-U`, `--iid-module=name`:
     Select iid module (default = `low`).

   * `--iid-args=args`:
     Arguments to pass to iid module.

   * `--iid-num=num`:
     Number of iid for one target prefix.

   * `-q`, `--quiet`:
     Do not print status updates once per second.

   * `-v`, `--verbosity=n`:
     Level of log detail (0-5, default = `3`).

   * `-l`, `--log-file=filename`:
	 Output file for log messages. By default, `stderr`.

   * `-L`, `--log-directory=path`:
     Write log entries to a timestamped file in this directory.

   * `-m`, `--metadata-file=filename`:
     Output file for scan metadata (JSON).

   * `-u`, `--status-updates-file`:
     Write scan progress updates to CSV file.

   * `--disable-syslog`:
     Disables logging messages to syslog.

   * `--notes=notes`:
     Inject user-specified notes into scan metadata.

   * `--user-metadata=json`:
     Inject user-specified JSON metadata into scan metadata.

   * `-T`, `--sender-threads=num`:
     Threads used to send packets. XMap will attempt to detect the optimal number of send threads based on the number of processor cores.
     
   * `-C`, `--config=filename`:
     Read a configuration file, which can specify any other options.

   * `-d`, `--dryrun`:
     Print out each packet to stdout instead of sending it (useful for debugging).
     
   * `--max-sendto-failures=num`:
     Maximum NIC sendto failures before scan is aborted.

   * `--min-hitrate=rate`:
     Minimum hitrate that scan can hit before scan is aborted.

   * `--cores`:
     Comma-separated list of cores to pin to.

   * `--ignore-blacklist-error`:
      Ignore invalid, malformed, or unresolvable entries in `--whitelist-file` and `--blacklist-file`.
      
   * `--ignore-filelist-error`:
      Ignore invalid, malformed, or unresolvable entries in `--list-of-ips-file`.
      
   * `-h`, `--help`:
     Print help and exit.

   * `-V`, `--version`:
     Print version and exit.

### Output Filters

Replies can undergo filtration before being transferred to the output module. These filters are specified across the output fields of a probe module. Written in a straightforward filtering language akin to SQL, filters are supplied to HMap via the `--output-filter` option. Output filters are frequently employed to eliminate duplicate outcomes or exclusively relay successful responses to the output module.

Filter expressions are of the form `<fieldname> <operation> <value>`. The type of `<value>` must be either a string or unsigned integer literal, and match the type of `<fieldname>`. The valid operations for integer comparisons are `=`, `!=`, `<`, `>`, `<=`, `>=`. The operations for string comparisons are `=`, `!=`. The`--list-output-fields` flag will print what fields and types are available for the selected probe module, and then exit.

Compound filter expressions may be constructed by combining filter expressions using parenthesis to specify order of operations, the `&&` (logical AND) and `||` (logical OR) operators.

For example, a filter for only successful, non-duplicate responses would be written as: `--output-filter="success = 1 && repeat = 0"`.

### UDP Probe Options

These arguments are all passed using the `--probe-args=args` option. Only one argument may be passed at a time.

   * `file:/path/to/file`:
     Path to payload file to send to each host over UDP.
     
   * `text:<text>`:
     ASCII text to send to each destination host.
     
   * `hex:<hex>`:
     Hex-encoded binary to send to each destination host.
     
   * `dir:/directory/to/file`:
     Directory to payload file to send to each host over UDP when probing multiple ports. 
     File extension priority: `pkt`>`txt`>`hex`. Each file is named by the port number, e.g., 53.pkt for DNS payload.
     
   * `template:/path/to/template`:
     Path to template file. For each destination host, the template file is populated, set as the UDP payload, and sent. 
     
   * `template-fields`:
     Print information about the allowed template fields and exit.
     
   * `icmp-type-code-str`:
     Print value of the icmp related filters and exit. 

## Examples

```shell
hmap
# Scan the ::/0-32 space by Echo ping and output to stdout
hmap -4
# Scan the 0.0.0.0/0-32 space by Echo ping and output to stdout
hmap -N 5 -B 10M
# Find 5 alive IPv6 hosts, scanning at 10 Mb/s
hmap 2001::/8 2002::/16
# Scan both subnets for 2001::/8-32 and 2002::/16-32 space
hmap -x 64 2001::/32 -U rand
# Scan 2001::/32-64 with random IID, e.g., 2001::1783:ab42:9247:cb38
hmap -M icmp_echo -O csv -U low -h
# Show help text for modules icmp_echo, csv, and low
hmap -M tcp_syn -p 80,443,8080-8081
# Scan the ::/0-32 space for port 80,443,8080,8081 by TCP SYN ping	

hmap -D hitlist
# Download Gasser et al.'s IPv6 hitlist
hmap -D aliasPrefix
# Download Gasser et al.'s alias prefixes

hmap -w prefixes32 -U low -x 42 -b GaliasPrefix -f "outersaddr" -o Hhitlist-low -O csv -R 200000 --output-filter="type=1||type=3||type=129"
# Scan the global BGP prefixes in the file 'prefixes32' using low-byte mode up to a maximum prefix length of 42. Exclude probing the (alias) addresses in the file 'GaliasPrefix'. Record the replies in the format <source> in the output file 'Hhitlist-low', while ensuring a maximum probing speed of 200Kpps. 

hmap -I Seeds -U tga -b GaliasPrefix -R 200000 -O csv -o Hhitlist-tga -f "outersaddr, type" --output-filter="type=1||type=3||type=129" --ignore-filelist-error
# Use TGA (Target Generation Algorithm) mode for address generation with a maximum seed number of 10M and a maximum probing budget of 1B in a scan by default. Exclude probing the (alias) addresses in the file 'GaliasPrefix'. Record the replies in the format <source, type> in the output file 'Hhitlist-tga' The reply types are constrained to '1' (Destination_Unreachable), indicative of a periphery; '3' (Time_Exceeded), likely representing a middlebox; and '129' (Echo_Reply), likely representing an end-host. 
```

## Reference

### Prober
>X. Li, B. Liu, X. Zheng, H. Duan, Q. Li, and Y. Huang, “Fast IPv6 Network Periphery Discovery and Security Implications,” in DSN, 2021.

>Z. Durumeric, E. Wustrow, J. A. Halderman, E. Wustrow, and J. A. Halderman, “ZMap: Fast Internet-wide scanning and Its Security Applications,” in USENIX Security, 2013.

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
