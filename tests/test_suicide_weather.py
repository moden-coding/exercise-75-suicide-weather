#!/usr/bin/env python3

import contextlib
import io
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.suicide_weather import main, suicide_fractions, suicide_weather


def _spy(method_to_decorate):
    """Wrap a real method with a MagicMock so calls can be asserted while
    the original implementation still runs."""
    mock = MagicMock(name="corr method")

    def wrapper(self, *args, **kwargs):
        mock(*args, **kwargs)
        return method_to_decorate(self, *args, **kwargs)

    wrapper.mock = mock
    return wrapper


class TestSuicideWeather(unittest.TestCase):

    def setUp(self):
        self.tup = suicide_weather()

    def test_return_value(self):
        suicide_n, temperature_n, common_n, corr = self.tup
        self.assertEqual(
            suicide_n,
            141,
            msg="suicide_weather() returned suicide_rows=%r, expected 141 - "
            "the size of the suicide-fractions Series." % (suicide_n,),
        )
        self.assertEqual(
            temperature_n,
            191,
            msg="suicide_weather() returned temperature_rows=%r, expected "
            "191 - the size of the temperature Series." % (temperature_n,),
        )
        self.assertEqual(
            common_n,
            108,
            msg="suicide_weather() returned common_rows=%r, expected 108 - "
            "the number of countries present in both Series." % (common_n,),
        )
        self.assertAlmostEqual(
            corr,
            -0.5580402318136322,
            places=4,
            msg="Spearman correlation should be about -0.5580, got %r."
            % (corr,),
        )

    def test_calls(self):
        method = _spy(pd.core.series.Series.corr)
        f_method = _spy(pd.core.frame.DataFrame.corr)
        with patch(
            "src.suicide_weather.suicide_fractions", wraps=suicide_fractions
        ) as psf, patch(
            "src.suicide_weather.pd.read_html", wraps=pd.read_html
        ) as phtml, patch.object(
            pd.core.series.Series, "corr", new=method
        ), patch.object(
            pd.core.frame.DataFrame, "corr", new=f_method
        ), patch(
            "src.suicide_weather.suicide_weather", wraps=suicide_weather
        ) as psw:
            out_buf = io.StringIO()
            with contextlib.redirect_stdout(out_buf):
                main()
            psf.assert_called_once_with()
            psw.assert_called_once_with()
            phtml.assert_called_once()
            if not f_method.mock.called:
                method.mock.assert_called()
                args, kwargs = method.mock.call_args
            else:
                args, kwargs = f_method.mock.call_args
            correct = (len(args) > 1 and args[1] == "spearman") or (
                "method" in kwargs and kwargs["method"] == "spearman"
            )
            self.assertTrue(
                correct,
                msg="corr() must be called with the Spearman method (either "
                "as the second positional argument or as method='spearman'). "
                "Got args=%r kwargs=%r." % (args, kwargs),
            )

        out = out_buf.getvalue()
        self.assertRegex(
            out,
            r"Suicide DataFrame has \d+ rows",
            msg="Expected a printed line matching 'Suicide DataFrame has "
            "<N> rows', got:\n%s" % (out,),
        )
        self.assertRegex(
            out,
            r"Temperature DataFrame has \d+ rows",
            msg="Expected a printed line matching 'Temperature DataFrame "
            "has <N> rows', got:\n%s" % (out,),
        )
        self.assertRegex(
            out,
            r"Common DataFrame has \d+ rows",
            msg="Expected a printed line matching 'Common DataFrame has "
            "<N> rows', got:\n%s" % (out,),
        )
        self.assertRegex(
            out,
            r"Spearman correlation:\s+[+-]?\d+\.\d+",
            msg="Expected a printed line matching 'Spearman correlation: "
            "<number>', got:\n%s" % (out,),
        )


if __name__ == '__main__':
    unittest.main()
