/*
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
*/

/*
 * Benchmark Schnorr's Proof.
 */

#include "bench.h"
#include "amcl/schnorr.h"

#define MIN_TIME    5.0
#define MIN_ITERS   10

char *ID_str = "unique_identifier_123";
char *AD_hex = "d7d3155616778fb436a1eb2070892205";

char *R_hex = "803ccd21cddad626e15f21b1ad787949e9beef08e6e68a9e00df59dec16ed290";
char *X_hex = "fab4ce512dff74bd9c71c89a14de5b877af45dca0329ee3fcb72611c0784fef3";
char *V_hex = "032cf4b348c9d00718f01ed98923e164df53b5e8bc4c2250662ed2df784e1784f4";

int main()
{
    int rc;

    int iterations;
    clock_t start;
    double elapsed;

    char x_char[SGS_SECP256K1];
    octet X = {0, sizeof(x_char), x_char};

    char v[SFS_SECP256K1+1];
    octet V = {0, sizeof(v), v};

    char id[32];
    octet ID = {0, sizeof(id), id};

    char ad[32];
    octet AD = {0, sizeof(ad), ad};

    char r[SGS_SECP256K1];
    octet R = {0, sizeof(r), r};

    char c[SFS_SECP256K1+1];
    octet C = {0, sizeof(c), c};

    char e[SGS_SECP256K1];
    octet E = {0, sizeof(e), e};

    char p[SGS_SECP256K1];
    octet P = {0, sizeof(p), p};

    // Load values
    OCT_jstring(&ID, ID_str);
    OCT_fromHex(&AD, AD_hex);

    OCT_fromHex(&R, R_hex);
    OCT_fromHex(&X, X_hex);
    OCT_fromHex(&V, V_hex);

    print_system_info();

    printf("Timing info\n");
    printf("===========\n");

    iterations=0;
    start=clock();
    do
    {
        SCHNORR_commit(NULL, &R, &C);
        iterations++;
        elapsed=(clock()-start)/(double)CLOCKS_PER_SEC;
    }
    while (elapsed<MIN_TIME || iterations<MIN_ITERS);

    elapsed= MICROSECOND * elapsed / iterations;
    printf("\tSCHNORR_commit\t\t%8d iterations\t",iterations);
    printf("%8.2lf us per iteration\n",elapsed);

    iterations=0;
    start=clock();
    do
    {
        SCHNORR_challenge(&V, &C, &ID, &AD, &E);
        iterations++;
        elapsed=(clock()-start)/(double)CLOCKS_PER_SEC;
    }
    while (elapsed<MIN_TIME || iterations<MIN_ITERS);

    elapsed= MICROSECOND * elapsed / iterations;
    printf("\tSCHNORR_challenge\t%8d iterations\t",iterations);
    printf("%8.2lf us per iteration\n",elapsed);

    iterations=0;
    start=clock();
    do
    {
        SCHNORR_prove(&R, &E, &X, &P);
        iterations++;
        elapsed=(clock()-start)/(double)CLOCKS_PER_SEC;
    }
    while (elapsed<MIN_TIME || iterations<MIN_ITERS);

    elapsed= MICROSECOND * elapsed / iterations;
    printf("\tSCHNORR_prove\t\t%8d iterations\t",iterations);
    printf("%8.2lf us per iteration\n",elapsed);

    iterations = 0;
    start = clock();
    do
    {
        rc = SCHNORR_verify(&V, &C, &E, &P);
        iterations++;
        elapsed = (clock() - start) / (double)CLOCKS_PER_SEC;
    }
    while (elapsed < MIN_TIME || iterations < MIN_ITERS);

    if (rc != SCHNORR_OK)
    {
        printf("FAILURE SCHNORR_verify: %d\n", rc);
        exit(EXIT_FAILURE);
    }

    elapsed = MICROSECOND * elapsed / iterations;
    printf("\tSCHNORR_verify\t\t%8d iterations\t", iterations);
    printf("%8.2lf us per iteration\n", elapsed);

    exit(EXIT_SUCCESS);
}
