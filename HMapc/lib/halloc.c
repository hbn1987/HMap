#include "halloc.h"

#include <stdlib.h>
#include <string.h>

#include "logger.h"

static void die() __attribute__((noreturn));

void *xcalloc(size_t count, size_t size) {
    void *res = calloc(count, size);
    if (res == NULL) {
        die();
    }

    return res;
}

void xfree(void *ptr) { free(ptr); }

void *xmalloc(size_t size) {
    void *res = malloc(size);
    if (res == NULL) {
        die();
    }
    memset(res, 0, size);

    return res;
}

void *xrealloc(void *ptr, size_t size) {
    void *res = realloc(ptr, size);
    if (res == NULL) {
        die();
    }

    return res;
}

void die() { log_fatal("hmap", "Out of memory"); }
