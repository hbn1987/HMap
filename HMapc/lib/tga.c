/*
 * HMap Copyright 2024 Bingnan Hou from NUDT
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at http://www.apache.org/licenses/LICENSE-2.0
 */

#include "tga.h"

// Initialize IPVector
void initIPVector(IPVector *vec) {
    vec->ips = NULL;
    vec->size = 0;
    vec->capacity = 0;
}

// Add an IP to IPVector
void addIP(IPVector *vec, const char *ip) {
    if (vec->size >= vec->capacity) {
        // Expand capacity
        vec->capacity = (vec->capacity == 0) ? 1 : vec->capacity * 2;
        vec->ips = realloc(vec->ips, vec->capacity * sizeof(char *));
    }
    // Allocate memory and copy IP
    vec->ips[vec->size] = strdup(ip);
    vec->size++;
}

// Free memory allocated by IPVector
void freeIPVector(IPVector *vec) {
    if (vec->ips) {
        for (size_t i = 0; i < vec->size; i++) {
            free(vec->ips[i]);
        }
        free(vec->ips);
    }
}

// Comparison function for qsort
int compareStrings(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

// Convert IPv6 address to a 32-bit base-16 mode notation string
char *seed2vec(char *ipv6) {
    // Allocate space for 32 bits + '\0'
    char *base16 = (char *)malloc((IPV6_LENGTH + 1) * sizeof(char));
    base16[0] = '\0'; // Initialize as an empty string

    int double_colon_index = -1; // Variable to store the position of the double colon
    char *ipv6_copy;

    // Find the position of the double colon
    char *double_colon_ptr = strstr(ipv6, "::");
    if (double_colon_ptr != NULL) {
        double_colon_index = (int)(double_colon_ptr - ipv6); // Store the position of the double colon

        // Allocate enough memory for ipv6_copy
        ipv6_copy = (char *)malloc((strlen(ipv6) + 2) * sizeof(char)); // Copy length + "*" + '\0'
        strcpy(ipv6_copy, ipv6);

        // Replace double colon with ":*:"
        strcpy(ipv6_copy + double_colon_index, ":*:"); // Replace the double colon
        strcpy(ipv6_copy + double_colon_index + 3, ipv6 + double_colon_index + 2); // Copy the part after the double colon
    } else {
        // Allocate enough memory for ipv6_copy
        ipv6_copy = (char *)malloc((strlen(ipv6) + 1) * sizeof(char)); // Copy length + '\0'
        strcpy(ipv6_copy, ipv6); // If there is no double colon, simply copy the entire IPv6 address
    }

    int segments = 0; // Variable to count the number of segments
    char *token;
    token = strtok(ipv6_copy, ":");
    // Start converting IPv6 address to base-16 mode notation string
    while (token != NULL) {
        if (!strcmp(token, "*")) {
            strcat(base16, "*"); // Append '*' directly to the result string
        } else {
            int num;
            sscanf(token, "%x", &num); // Convert hexadecimal string to integer
            sprintf(base16 + strlen(base16), "%04x", num); // Format as a 4-digit hexadecimal string and append to the result string
            segments++; // Increment segment count
        }
        token = strtok(NULL, ":");
    }
    free(ipv6_copy); // Free memory allocated for ipv6_copy

    // If '*' is present, fill it with '0'
    char *ptr = strstr(base16, "*");
    if (ptr != NULL) {
        int num_zeros = (8 - segments) * 4; // Calculate the number of '0's required
        memmove(ptr + num_zeros, ptr + 1, strlen(ptr + 1) + 1); // Move the characters after '*' to make space
        memset(ptr, '0', num_zeros); // Fill with '0's
    }

    return base16; // Return the base-16 mode notation string
}

// Calculate Hamming distance between two strings
int hamming_distance(const char *str1, const char *str2) {
    int distance = 0;
    for (int i = 0; i < IPV6_LENGTH; i++) {
        if (str1[i] != str2[i]) {
            distance++;
        }
    }
    return distance;
}

// Merge two strings based on Hamming distance
char *merge_strings(const char *str1, const char *str2) {
    char *result = malloc((IPV6_LENGTH + 1) * sizeof(char));
    if (result == NULL) {
        // Error handling: Failed to allocate memory
        return NULL;
    }
    for (int i = 0; i < IPV6_LENGTH; i++) {
        result[i] = (str1[i] == str2[i]) ? str1[i] : '*';
    }
    result[IPV6_LENGTH] = '\0';
    return result;
}

// Perform hierarchical clustering
void hierarchical_cluster(IPVector *ipvec) {
    for (size_t i = 0; i < ipvec->size - 1; i++) {
        size_t j = i + 1;
        while (j < ipvec->size) {
            int distance = hamming_distance(ipvec->ips[i], ipvec->ips[j]);
            if (distance <= HAMMING_THRESHOLD) {
                char *merged_string = merge_strings(ipvec->ips[i], ipvec->ips[j]);
                ipvec->ips[i] = merged_string;
                j++;
            } else {
                i = j - 1;
                break;
            }
        }
    }
}

// Translate the base-16 mode notation into the colon-hexadecimal notation.
char* vec2colon(const char* line) {
    // Allocate memory for the result string
    char* res_str = (char*)malloc(40 * sizeof(char));
    
    int res_idx = 0;
    for (int i = 0; i < 7; i++) {
        // Copy four characters followed by a colon
        for (int j = 0; j < 4; j++) {
            res_str[res_idx++] = line[i * 4 + j];
        }
        // Add a colon
        res_str[res_idx++] = ':';
    }
    // Copy the last four characters
    for (int j = 28; j < 32; j++) {
        res_str[res_idx++] = line[j];
    }
    // Null-terminate the result string
    res_str[res_idx] = '\0';
    
    return res_str;
}

void target_generation(IPVector *targets, char* subspace, int start_idx) {
    int idx;
    for (idx = start_idx; idx < 32; idx++) {
        if (subspace[idx] == '*') {
            break;
        }
    }
    if (idx == 32) {
        // printf("Target IP address: %s\n", vec2colon(subspace));
        addIP(targets, vec2colon(subspace));
        return;
    }
    // Iterate over possible values for the wildcard character
    for (int i = 0; i < 16; i++) {
        if (i < 10) {
            subspace[idx] = '0' + i;
        } else { // i >= 10
            subspace[idx] = 'a' + i - 10;
        }
        // Recursively generate target IP addresses
        target_generation(targets, subspace, idx + 1);
    }
    // Restore the wildcard character for backtracking
    subspace[idx] = '*';
}

// Initialize the hash set
HashSet* HashSet_init(size_t initial_capacity) {
    HashSet* set = (HashSet*)malloc(sizeof(HashSet));
    set->table = (Node**)malloc(initial_capacity * sizeof(Node*));
    set->size = 0;
    set->capacity = initial_capacity;
    for (size_t i = 0; i < initial_capacity; i++) {
        set->table[i] = NULL;
    }
    return set;
}

// Hash a string key
size_t hash(const char* key, size_t table_size) {
    size_t hash = 0;
    while (*key) {
        hash = (hash * 31 + *key) % table_size;
        key++;
    }
    return hash;
}

// Insert a key into the hash set
void HashSet_insert(HashSet* set, const char* key) {
    // Check if the key already exists in the hash set
    if (HashSet_contains(set, key)) {
        return; // Key already exists, no need to insert again
    }
    // Check load factor and resize if necessary
    if ((double)set->size / set->capacity >= LOAD_FACTOR_THRESHOLD) {
        HashSet_resize(set, set->capacity * 2);
    }
    size_t h = hash(key, set->capacity);
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->key = strdup(key);
    newNode->next = set->table[h];
    set->table[h] = newNode;
    set->size++;
}

// Check if a key exists in the hash set
int HashSet_contains(HashSet* set, const char* key) {
    size_t h = hash(key, set->capacity);
    Node* current = set->table[h];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return 1;
        }
        current = current->next;
    }
    return 0;
}

// Resize the hash set
void HashSet_resize(HashSet* set, size_t new_capacity) {
    Node** new_table = (Node**)calloc(new_capacity, sizeof(Node*));
    for (size_t i = 0; i < set->capacity; i++) {
        Node* current = set->table[i];
        while (current != NULL) {
            Node* next = current->next;
            size_t h = hash(current->key, new_capacity);
            current->next = new_table[h];
            new_table[h] = current;
            current = next;
        }
    }
    free(set->table);
    set->table = new_table;
    set->capacity = new_capacity;
}

// Free the memory allocated for the hash set
void HashSet_free(HashSet* set) {
    for (size_t i = 0; i < set->capacity; i++) {
        Node* current = set->table[i];
        while (current != NULL) {
            Node* temp = current;
            current = current->next;
            free(temp->key);
            free(temp);
        }
    }
    free(set->table);
    free(set);
}