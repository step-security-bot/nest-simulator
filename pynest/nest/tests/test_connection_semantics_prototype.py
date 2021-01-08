# -*- coding: utf-8 -*-
#
# test_connection_semantics_prototype.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import nest

nest.set_verbosity('M_ERROR')


class TestConnectionSemanticsPrototype(unittest.TestCase):

    def setUp(self):
        nest.ResetKernel()

    def test_connect_one_to_one_projection(self):
        """Connect with one_to_one projection subclass"""
        n = nest.Create('iaf_psc_alpha')

        projection = nest.projections.OneToOne(source=n, target=n)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), 1)
        self.assertEqual(conns.source, 1)
        self.assertEqual(conns.target, 1)

    def test_connect_fixed_indegree_projection(self):
        """Connect with fixed_indegree projection subclass"""
        n = nest.Create('iaf_psc_alpha')

        projection = nest.projections.FixedIndegree(source=n, target=n, indegree=5)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), 5)

    def test_connect_fixed_outdegree_projection(self):
        """Connect with fixed_outdegree projection subclass"""
        n = nest.Create('iaf_psc_alpha')

        projection = nest.projections.FixedOutdegree(source=n, target=n, outdegree=5)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), 5)

    def test_connect_fixed_total_number_projection(self):
        """Connect with fixed_total_number projection subclass"""
        n = nest.Create('iaf_psc_alpha')

        projection = nest.projections.FixedTotalNumber(source=n, target=n, N=5)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), 5)

    def test_connect_bernoulli_projection(self):
        """Connect with pairwise bernoulli projection subclass"""
        n = nest.Create('iaf_psc_alpha', 100)
        p = 0.5

        projection = nest.projections.PairwiseBernoulli(source=n, target=n, p=p)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), p*len(n)*len(n))

    def test_connect_batch_projections(self):
        """Connect with multiple batched projections"""
        N = 10
        IN_A = 2
        IN_B = 5
        n = nest.Create('iaf_psc_alpha', N)

        nest.projections.Connect(nest.projections.FixedIndegree(source=n, target=n, indegree=IN_A))
        nest.projections.Connect(nest.projections.FixedIndegree(source=n, target=n, indegree=IN_B))
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), N*(IN_A + IN_B))

    def test_connect_batch_projection_list(self):
        """Connect with multiple batched projections as a list"""
        N = 10
        IN_A = 2
        IN_B = 5
        n = nest.Create('iaf_psc_alpha', N)

        nest.projections.Connect([nest.projections.FixedIndegree(source=n, target=n, indegree=IN_A),
                                  nest.projections.FixedIndegree(source=n, target=n, indegree=IN_B)])
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), N*(IN_A + IN_B))

    def test_connect_single_projection(self):
        """Connect with a single projection"""
        n = nest.Create('iaf_psc_alpha', 1)

        nest.projections.ConnectImmediately(nest.projections.OneToOne(source=n, target=n))

        conns = nest.GetConnections()
        self.assertEqual(len(conns), 1)
        self.assertEqual(conns.source, 1)
        self.assertEqual(conns.target, 1)

    def test_connect_projection_list(self):
        """Connect with list of projections"""
        N = 10
        IN_A = 2
        IN_B = 5
        n = nest.Create('iaf_psc_alpha', N)

        nest.projections.ConnectImmediately([nest.projections.FixedIndegree(source=n, target=n, indegree=IN_A),
                                             nest.projections.FixedIndegree(source=n, target=n, indegree=IN_B)])

        conns = nest.GetConnections()
        self.assertEqual(len(conns), N*(IN_A + IN_B))

    def test_connect_with_synapse_object(self):
        """Connect projection with synapse object"""
        weight = 0.5
        delay = 0.7

        for synapse, args, syn_ref in [(nest.synapsemodels.static, {}, 'static_synapse'),
                                       (nest.synapsemodels.ht, {'P': 0.8}, 'ht_synapse'),
                                       (nest.synapsemodels.stdp, {'lambda': 0.02}, 'stdp_synapse')]:
            nest.ResetKernel()
            n = nest.Create('iaf_psc_alpha')

            syn = synapse(weight=weight, delay=delay, **args)
            projection = nest.projections.OneToOne(source=n, target=n, syn_spec=syn)

            nest.projections.Connect(projection)
            nest.projections.BuildNetwork()

            conns = nest.GetConnections()
            self.assertAlmostEqual(conns.weight, weight)
            self.assertAlmostEqual(conns.delay, delay)
            for key, item in args.items():
                self.assertAlmostEqual(conns.get(key), item)
            self.assertEqual(conns.synapse_model, syn_ref)

    def test_connect_with_collocated_synapses(self):
        """Connect projection with collocated synapses"""
        n = nest.Create('iaf_psc_alpha')

        weight_a = -2.
        weight_b = 3.

        syn_spec = nest.CollocatedSynapses(nest.synapsemodels.static(weight=weight_a),
                                           nest.synapsemodels.static(weight=weight_b))
        projection = nest.projections.OneToOne(source=n, target=n, syn_spec=syn_spec)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), len(syn_spec))
        self.assertEqual([weight_a, weight_b], conns.weight)

    def test_connect_projection_spatial(self):
        """Spatial connect with projections"""
        indegree = 1
        dim = [4, 5]
        extent = [10., 10.]
        layer = nest.Create('iaf_psc_alpha', positions=nest.spatial.grid(dim, extent=extent))

        mask = {'rectangular': {
                'lower_left': [-5., -5.],
                'upper_right': [0., 0.]}}
        projection = nest.projections.FixedIndegree(source=layer, target=layer, indegree=indegree, mask=mask)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        conns = nest.GetConnections()
        self.assertEqual(len(conns), len(layer)*indegree)

    def test_connect_projection_spatial_collocated(self):
        """Spatial connect with projections and collocated synapses"""
        indegree = 1
        weight_a = -2.
        weight_b = 3.

        dim = [4, 5]
        extent = [10., 10.]
        layer = nest.Create('iaf_psc_alpha', positions=nest.spatial.grid(dim, extent=extent))

        mask = {'rectangular': {
                'lower_left': [-5., -5.],
                'upper_right': [0., 0.]}}

        syn_spec = nest.CollocatedSynapses(nest.synapsemodels.static(weight=weight_a),
                                           nest.synapsemodels.static(weight=weight_b))
        projection = nest.projections.FixedIndegree(source=layer, target=layer, indegree=indegree, mask=mask,
                                                    syn_spec=syn_spec)
        nest.projections.Connect(projection)
        nest.projections.BuildNetwork()

        weight_ref = sorted([weight_a, weight_b]*len(layer))
        conns = nest.GetConnections()
        self.assertEqual(len(conns), len(layer)*len(syn_spec)*indegree)
        self.assertEqual(sorted(conns.weight), weight_ref)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConnectionSemanticsPrototype)
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
