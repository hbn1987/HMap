# sources file
set(LIB_SOURCES
        blocklist.c
        bloom.c
        constraint.c
        csv.c
        gmp-ext.c
        lockfd.c
        logger.c
        random.c
        rijndael-alg-fst.c
        util.c
        halloc.c
        tga.c
        )

if (WITH_REDIS)
    SET(LIB_SOURCES ${LIB_SOURCES} redis.c)
endif()

# gen link target
add_library(hmaplib
        STATIC ${LIB_SOURCES}
        )

# specify the dir for gen target
target_include_directories(hmaplib
        PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
        )

if (WITH_CURL)
        target_link_libraries(hmaplib ${CURL_LIBRARIES})
endif ()
