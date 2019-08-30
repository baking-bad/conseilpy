from conseil.core import *
from tests.mock_api import ConseilCase


class MetadataTest(ConseilCase):

    def test_metadata_platforms(self):
        self.conseil()
        self.assertLastGetPathEquals('metadata/platforms')
        self.assertTrue(isinstance(self.conseil, ConseilClient))

    def test_metadata_networks(self):
        self.conseil.tezos()
        self.assertLastGetPathEquals('metadata/tezos/networks')
        self.assertEqual('tezos', self.conseil.tezos['platform_id'])
        self.assertTrue(isinstance(self.conseil.tezos, Platform))
        self.assertEqual(id(self.conseil.tezos), id(self.conseil.tezos))

    def test_metadata_entities(self):
        self.conseil.tezos.alphanet()
        self.assertLastGetPathEquals('metadata/tezos/alphanet/entities')
        self.assertEqual('tezos', self.conseil.tezos.alphanet['platform_id'])
        self.assertEqual('alphanet', self.conseil.tezos.alphanet['network_id'])
        self.assertTrue(isinstance(self.conseil.tezos.aplhanet, Network))
        self.assertEqual(id(self.conseil.tezos.alphanet), id(self.conseil.tezos.alphanet))

    def test_metadata_attributes(self):
        self.conseil.tezos.alphanet.operations()
        self.assertLastGetPathEquals('metadata/tezos/alphanet/operations/attributes')
        self.assertEqual('tezos', self.conseil.tezos.alphanet.operations['platform_id'])
        self.assertEqual('alphanet', self.conseil.tezos.alphanet.operations['network_id'])
        self.assertEqual('operations', self.conseil.tezos.alphanet.operations['entity_id'])
        self.assertTrue(isinstance(self.conseil.tezos.alphanet.operations, Entity))
        self.assertEqual(id(self.conseil.tezos.alphanet.operations),
                         id(self.conseil.tezos.alphanet.operations))

    def test_metadata_values(self):
        self.conseil.tezos.alphanet.operations.kind()
        self.assertLastGetPathEquals('metadata/tezos/alphanet/operations/kind')
        self.assertEqual('tezos', self.conseil.tezos.alphanet.operations.kind['platform_id'])
        self.assertEqual('alphanet', self.conseil.tezos.alphanet.operations.kind['network_id'])
        self.assertEqual('operations', self.conseil.tezos.alphanet.operations.kind['entity_id'])
        self.assertEqual('kind', self.conseil.tezos.alphanet.operations.kind['attribute_id'])
        self.assertTrue(isinstance(self.conseil.tezos.alphanet.operations.kind, Attribute))
        self.assertEqual(id(self.conseil.tezos.alphanet.operations.kind),
                         id(self.conseil.tezos.alphanet.operations.kind))

    def test_metadata_terminator(self):
        value = self.conseil.tezos.alphanet.operations.kind.transaction
        self.assertEqual('transaction', value)
