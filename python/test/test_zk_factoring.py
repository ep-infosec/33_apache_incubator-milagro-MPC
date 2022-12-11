#!/usr/bin/env python3

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

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from amcl import core_utils, factoring_zk

seed_hex = "78d0fb6705ce77dee47d03eb5b9c5d30"

p_hex  = "e008507e09c24d756280f3d94912fb9ac16c0a8a1757ee01a350736acfc7f65880f87eca55d6680253383fc546d03fd9ebab7d8fa746455180888cb7c17edf58d3327296468e5ab736374bc9a0fa02606ed5d3a4a5fb1677891f87fbf3c655c3e0549a86b17b7ddce07c8f73e253105e59f5d3ed2c7ba5bdf8495df40ae71a7f"
q_hex  = "dbffe278edd44c2655714e5a4cc82e66e46063f9ab69df9d0ed20eb3d7f2d8c7d985df71c28707f32b961d160ca938e9cf909cd77c4f8c630aec34b67714cbfd4942d7147c509db131bc2d6a667eb30df146f64b710f8f5247848b0a75738a38772e31014fd63f0b769209928d586499616dcc90700b393156e12eea7e15a835"
id_str = "unique_identifier"
ad_hex = "d7d3155616778fb436a1eb2070892205"

e_hex = "5812ec82060d2a3eab3c967a2d710223"
y_hex = "b4ebebd6177b2eb04149aa463ede7ba2216657e3b4de42f496c0d493b4d734131e63edcde042d951b9bf285622b9d69e9ee170156deeb173725032a952068e68b18f69bd4e52677d48d846055988877ce9e97b962f01e3f425f3101a6a589f020c858b1ee5ae8f79e4c63ce2356d8a9ae7b4e925357bc7aa2fb609c7cb6578b209f3993868c4e569dafeed4bc0a590453b6159819eed28dc7d2d25011641fa7312076813d85751fd23c75f5182e0c97d2fc8dce58d53a5ec2df3ec2ba08a063f6f9de97a8174c442acbd627dd864df41d1e322267c5674bd5459a3f12afad2b26fe5116a110b243cf8a78ce61d8eed22afde7f8d27a7c4b37fc07d55e8bdf412"


def process_tv(vector):
    for key, val in vector.items():
        if key != "TEST":
            vector[key] = bytes.fromhex(val)
    
    return vector


class TestProve(unittest.TestCase):
    """ Test ZK factoring Prove """

    def setUp(self):
        # Deterministic PRNG for testing purposes
        seed = bytes.fromhex(seed_hex)
        self.rng = core_utils.create_csprng(seed)

        self.p  = bytes.fromhex(p_hex)
        self.q  = bytes.fromhex(q_hex)
        self.e  = bytes.fromhex(e_hex)
        self.y  = bytes.fromhex(y_hex)
        self.id = id_str.encode('utf-8')
        self.ad = bytes.fromhex(ad_hex)

        with open("factoring_zk/prove.json", "r") as f:
            self.tv = json.load(f)

        for vector in self.tv:
            process_tv(vector)

    def test_tv(self):
        """ test using test vectors """

        for vector in self.tv:
            if not vector['AD']:
                vector['AD'] = None

            e, y = factoring_zk.prove(None, vector['P'], vector['Q'], vector['ID'], ad=vector['AD'], r=vector['R'])

            self.assertEqual(e, vector['E'])
            self.assertEqual(y, vector['Y'])

    def test_random(self):
        """ test using PRNG """

        e, y = factoring_zk.prove(self.rng, self.p, self.q, self.id, ad=self.ad)

        self.assertEqual(e, self.e)
        self.assertEqual(y, self.y)

class TestVerify(unittest.TestCase):
    """ Test ZK factoring Verify """

    def setUp(self):
        with open("factoring_zk/verify.json", "r") as f:
            self.tv = json.load(f)

        for vector in self.tv:
            process_tv(vector)

    def test_tv(self):
        """ test using test vectors """

        for vector in self.tv:
            if not vector['AD']:
                vector['AD'] = None

            ec = factoring_zk.verify(vector['N'], vector['E'], vector['Y'], vector['ID'], ad=vector['AD'])

            self.assertEqual(ec, factoring_zk.OK)

    def test_failure(self):
        """ Test error codes are propagated correctly """

        ec = factoring_zk.verify(self.tv[0]['Y'], self.tv[0]['E'], self.tv[0]['N'], self.tv[0]['ID'])

        self.assertEqual(ec, factoring_zk.FAIL)

if __name__ == '__main__':
    # Run tests
    unittest.main()
