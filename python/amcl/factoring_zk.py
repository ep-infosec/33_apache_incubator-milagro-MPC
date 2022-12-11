"""
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
"""

"""

This module use cffi to access the c functions in the amcl_mpc library.

"""

import platform
from . import core_utils

_ffi = core_utils._ffi
_ffi.cdef("""
typedef struct
{
    BIG_1024_58 p[1];
    BIG_1024_58 q[1];
    BIG_1024_58 invpq[1];
    BIG_1024_58 n[2];
} FACTORING_ZK_modulus;

void FACTORING_ZK_prove(csprng *RNG, FACTORING_ZK_modulus *m, const octet *ID, const octet *AD, octet *R, octet *E, octet *Y);
int FACTORING_ZK_verify(octet *N, octet *E, octet *Y, const octet *ID, const octet *AD);
void FACTORING_ZK_modulus_fromOctets(FACTORING_ZK_modulus *m, octet *P, octet *Q);
void FACTORING_ZK_modulus_kill(FACTORING_ZK_modulus *m);
""")

if (platform.system() == 'Windows'):
    _libamcl_mpc = _ffi.dlopen("libamcl_mpc.dll")
    _libamcl_paillier = _ffi.dlopen("libamcl_paillier.dll")
elif (platform.system() == 'Darwin'):
    _libamcl_mpc = _ffi.dlopen("libamcl_mpc.dylib")
    _libamcl_paillier = _ffi.dlopen("libamcl_paillier.dylib")
else:
    _libamcl_mpc = _ffi.dlopen("libamcl_mpc.so")
    _libamcl_paillier = _ffi.dlopen("libamcl_paillier.so")

# Constants
B        = 16  # Security parameter - 128 bit
FS_2048  = 256 # Size in bytes of an FF_2048
HFS_2048 = 128 # Half size in bytes of an FF_2048

OK   = 0
FAIL = 91


def prove(rng, p, q, id, ad=None, r=None):
    """Generate factoring knowledge proof



    Args::

        rng : Pointer to cryptographically secure pseudo-random
              number generator instance
        p   : First prime factor of n. HFS_2048 bytes long
        q   : Second prime factor of n. HFS_2048 bytes long
        id  : Unique identifier of the prover
        ad  : Additional data to bind in the proof. Optional
        r   : Deterministic value for r. FS_2048 bytes long

    Returns::

        e : First component of the factoring proof. B bytes long
        y : Second component of the factoring proof. FS_2048 bytes long

    Raises:

    """
    if r is None:
        r_oct = _ffi.NULL
    else:
        r_oct, r_val = core_utils.make_octet(None, r)
        _ = r_val # Suppress warning
        rng = _ffi.NULL

    if ad is None:
        ad_oct = _ffi.NULL
    else:
        ad_oct, ad_val = core_utils.make_octet(None, ad)
        _ = ad_val # Suppress warning

    p_oct, p_val   = core_utils.make_octet(None, p)
    q_oct, q_val   = core_utils.make_octet(None, q)
    e_oct, e_val   = core_utils.make_octet(B)
    y_oct, y_val   = core_utils.make_octet(FS_2048)
    id_oct, id_val = core_utils.make_octet(None, id)
    _ = p_val, q_val, e_val, y_val, id_val # Suppress warnings

    modulus = _ffi.new('FACTORING_ZK_modulus*')

    _libamcl_mpc.FACTORING_ZK_modulus_fromOctets(modulus, p_oct, q_oct)
    _libamcl_mpc.FACTORING_ZK_prove(rng, modulus, id_oct, ad_oct, r_oct, e_oct, y_oct)

    # Clear memory
    _libamcl_mpc.FACTORING_ZK_modulus_kill(modulus)
    core_utils.clear_octet(p_oct)
    core_utils.clear_octet(q_oct)

    return core_utils.to_str(e_oct), core_utils.to_str(y_oct)


def verify(n, e, y, id, ad=None):
    """Verify knowledge of factoring proof

    Args::

        n : public modulus
        e : First component of the factoring proof. B bytes long
        y : Second component of the factoring proof. FS_2048 bytes long
        id  : Unique identifier of the prover
        ad  : Additional data to bind in the challenge. Optional

    Returns::

        rc : OK if the verification is successful or an error code

    Raises:

    """
    if ad is None:
        ad_oct = _ffi.NULL
    else:
        ad_oct, ad_val = core_utils.make_octet(None, ad)
        _ = ad_val # Suppress warning

    n_oct, n_val   = core_utils.make_octet(None, n)
    e_oct, e_val   = core_utils.make_octet(None, e)
    y_oct, y_val   = core_utils.make_octet(None, y)
    id_oct, id_val = core_utils.make_octet(None, id)
    _ = n_val, e_val, y_val, id_val # Suppress warning

    rc = _libamcl_mpc.FACTORING_ZK_verify(n_oct, e_oct, y_oct, id_oct, ad_oct)

    return rc
