from django.test import SimpleTestCase

from ..global_id import generate_identifier, decode_identifier, DecodeHashidError


class Test(SimpleTestCase):

    def test(self):
        data = {"key":2, "value":4}
        ident = generate_identifier(version=1, **data)

        decoded_data = decode_identifier(version=1,
                                         identifier=ident,
                                         keys=data.keys())
        self.assertDictEqual(decoded_data, data)


        with self.assertRaises(DecodeHashidError):
            decoded_data = decode_identifier(version=2,
                                             identifier=ident,
                                             keys=data.keys())
