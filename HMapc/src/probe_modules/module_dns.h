/*
 * ZMap Copyright 2013 Regents of the University of Michigan
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

#ifndef XMAP_MODULE_DNS_H
#define XMAP_MODULE_DNS_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct __attribute__((packed)) {
    uint16_t id;         /* transaction ID */
    unsigned rd : 1;     /* recursion desired */
    unsigned tc : 1;     /* truncation */
    unsigned aa : 1;     /* authoritative answer */
    unsigned opcode : 4; /* opcode 0=std query 1=Inverse query 2=srv status
                            request */
    unsigned qr : 1;     /* query/response */

    unsigned rcode : 4; /* response code */
    unsigned cd : 1;    /* checking disabled */
    unsigned ad : 1;    /* authenticated data */
    unsigned z : 1;     /* reserved set to 0 */
    unsigned ra : 1;    /* recursion available */

    uint16_t qdcount; /* # entries in question section */
    uint16_t ancount; /* # RR in answer section */
    uint16_t nscount; /* # name server RR in authority section */
    uint16_t arcount; /* # RR in additional information section */
} dns_header;

typedef struct __attribute__((packed)) {
    uint16_t qtype;
    uint16_t qclass;
} dns_question_tail;

typedef struct __attribute__((packed)) {
    uint16_t type;
    uint16_t class;
    uint32_t ttl;
    uint16_t rdlength;
    char     rdata[];
} dns_answer_tail;

typedef struct __attribute__((packed)) {
    uint16_t type;         /* should be OPT (41) */
    uint16_t udpsize;      /* UDP payload size */
    uint8_t  ercode;       /* higher bits in extended rcode */
    uint8_t  eversion;     /* EDNS0 version */
    uint16_t dodnssec : 1; /* handle DNSSEC security or not */
    uint16_t z : 15;       /* reserved set to 0 */
    uint16_t dlength;      /* data length */
    char     data[];       /* data */
} dns_option_tail;

typedef enum {
    DNS_QTYPE_A        = 1,
    DNS_QTYPE_NS       = 2,
    DNS_QTYPE_CNAME    = 5,
    DNS_QTYPE_SOA      = 6,
    DNS_QTYPE_PTR      = 12,
    DNS_QTYPE_MX       = 15,
    DNS_QTYPE_TXT      = 16,
    DNS_QTYPE_AAAA     = 28,
    DNS_QTYPE_RRSIG    = 46,
    DNS_QTYPE_ALL      = 255,
    DNS_QTYPE_SIG      = 24,
    DNS_QTYPE_SRV      = 33,
    DNS_QTYPE_DS       = 43,
    DNS_QTYPE_DNSKEY   = 48,
    DNS_QTYPE_TLSA     = 52,
    DNS_QTYPE_SVCB     = 64,
    DNS_QTYPE_HTTPS    = 65,
    DNS_QTYPE_CAA      = 257,
    DNS_QTYPE_HTTPSSVC = 65479,
    DNS_QTYPE_OPT      = 41,
} dns_qtype;

typedef enum {
    DNS_RCODE_NOERR        = 0,
    DNS_RCODE_FORMATERR    = 1,
    DNS_RCODE_SRVFAILURE   = 2,
    DNS_RCODE_NXDOMAIN     = 3,
    DNS_RCODE_QTYPENOTIMPL = 4,
    DNS_RCODE_QRYREFUSED   = 5
} dns_rcode;

typedef enum {
    DNS_LTYPE_RAW    = 1,
    DNS_LTYPE_STR    = 2,
    DNS_LTYPE_TIME   = 3,
    DNS_LTYPE_RANDOM = 4,
    DNS_LTYPE_SRCIP  = 5
} dns_ltype;

#endif // XMAP_MODULE_DNS_H
