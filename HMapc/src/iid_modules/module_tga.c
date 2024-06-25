/*
 * HMap Copyright 2024 Bingnan Hou from NUDT
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

#include "iid_modules.h"

#include <assert.h>
#include <string.h>

iid_module_t module_tga;
static int   ipv46_bytes;

int tga_global_init(struct state_conf *conf) {
    assert(conf);
    ipv46_bytes = conf->ipv46_bytes;
    memset(IID, 0, ipv46_bytes);

    return EXIT_SUCCESS;
}

int tga_thread_init(void) { return EXIT_SUCCESS; }

int tga_get_current_iid(void *iid, UNUSED int iid_index, UNUSED void *args) {
    memcpy(iid, IID, ipv46_bytes);

    return EXIT_SUCCESS;
}

int tga_close(void) { return EXIT_SUCCESS; }

iid_module_t module_tga = {
    .name            = "tga",
    .global_init     = tga_global_init,
    .thread_init     = tga_thread_init,
    .get_current_iid = tga_get_current_iid,
    .close           = tga_close,
    .helptext        = "TGA mode IID (suffix), used for target generation scan."};
