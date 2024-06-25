/*
 * HMap Copyright 2024 Bingnan Hou from NUDT
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

#ifndef HMAP_TGA_H
#define HMAP_TGA_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Define a structure to store IP list
typedef struct IPVector{
    char **ips;
    size_t size;
    size_t capacity;
} IPVector;

// Define a node structure for the hash set
typedef struct Node {
    char* key; // String key
    struct Node* next; // Pointer to the next node
} Node;

// Define the hash set structure
typedef struct {
    Node** table; // Array of pointers to hash buckets
    size_t size; // Current number of elements in the hash set
    size_t capacity; // Capacity of the hash set (number of buckets)
} HashSet;

#define IPV6_LENGTH 32
#define HAMMING_THRESHOLD 3 // Define the Hamming distance threshold
#define SEED_MAX_CAPACITY 10000000 // Define maximum capacity of seed addresses
#define TARGET_MAX_CAPACITY 1000000000 // Define maximum capacity of target addresses
#define INITIAL_HASH_SIZE 1000000 // Initial hash table size
#define LOAD_FACTOR_THRESHOLD 0.75 // Load factor threshold for resizing

// Initialize IPVector
void initIPVector(IPVector *vec);

// Add an IP to IPVector
void addIP(IPVector *vec, const char *ip);

// Free memory allocated by IPVector
void freeIPVector(IPVector *vec);

int compareStrings(const void *a, const void *b);

// Convert colon-hexadecimal notation to base-16 mode notation
char *seed2vec(char *line);

void hierarchical_cluster(IPVector *ipvec);

void target_generation(IPVector *targets, char* subspace, int start_idx);

// Initialize the hash set
HashSet* HashSet_init(size_t initial_capacity);

// Hash a string key
size_t hash(const char* key, size_t table_size);

// Insert a key into the hash set
void HashSet_insert(HashSet* set, const char* key);

// Check if a key exists in the hash set
int HashSet_contains(HashSet* set, const char* key);

// Resize the hash set
void HashSet_resize(HashSet* set, size_t new_capacity);

// Free the memory allocated for the hash set
void HashSet_free(HashSet* set);

#endif // HMAP_TGA_H
