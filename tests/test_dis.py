# Copyright (c) 2022 Darren Erik Vengroff

import unittest

import pandas as pd

from divintseg import di, diversity, integration, segregation


class DfTestCase(unittest.TestCase):
    """Test diversity in a DataFrame"""

    def setUp(self) -> None:
        self.df = pd.DataFrame(
            [
                [10, 10, 10],
                [10, 10, 0],
                [10, 0, 0],
                [98, 1, 1],
            ],
            columns=["A", "B", "C"],
        )

    def test_diversity_of_df(self):
        """Test diversity of a dataframe."""
        s_diversity = diversity(self.df)

        self.assertAlmostEqual(2.0 / 3.0, s_diversity[0], places=10)
        self.assertAlmostEqual(1.0 / 2.0, s_diversity[1], places=10)
        self.assertEqual(0.0, s_diversity[2])

        self.assertAlmostEqual(
            0.98 * 0.02 + 0.01 * 0.99 + 0.01 * 0.99, s_diversity[3], places=10
        )

    def test_diversity_of_sub_df(self):
        """Test diversity of a subset of the columns of a dataframe."""
        s_diversity = diversity(self.df[["A", "C"]])

        self.assertAlmostEqual(0.5, s_diversity[0], places=10)
        self.assertAlmostEqual(0.0, s_diversity[1], places=10)
        self.assertEqual(0.0, s_diversity[2])

        self.assertAlmostEqual(
            (98.0 / 99.0) * (1.0 / 99.0) + (1.0 / 99.0) * (98.0 / 99.0),
            s_diversity[3],
            places=10,
        )


class IterableTestCase(unittest.TestCase):
    """
    Test diversity in an iterable.

    This is not a common case. Usually DataFrames are used.
    """

    def setUp(self) -> None:
        # An array of population counts.
        self.a = [10, 20, 30, 40]
        # Manually computed diversity.
        self.div = 0.1 * 0.9 + 0.2 * 0.8 + 0.3 * 0.7 + 0.4 * 0.6

    def test_array(self):
        """Test diversity of an array."""
        div = diversity(self.a)

        self.assertAlmostEqual(self.div, div, places=10)

    def test_series(self):
        """Test diversity of a pandas Series."""
        s = pd.Series(self.a)

        div = diversity(s)

        self.assertAlmostEqual(self.div, div, places=10)


class IntegrationTestCase(unittest.TestCase):
    """Test integtation computations."""

    def setUp(self) -> None:
        """Set up before each test."""
        self.df = pd.DataFrame(
            [
                # Regions of different size but equal
                # diversity.
                ["X", 10, 10, 10],
                ["X", 20, 20, 20],
                ["X", 30, 30, 30],
                # Regions of zero diversity.
                ["Y", 100, 0, 0],
                ["Y", 0, 100, 0],
                ["Y", 0, 0, 100],
                # Small diverse region and large
                # homogeneous region.
                ["Z", 1, 1, 1],
                ["Z", 97, 0, 0],
            ],
            columns=["region", "A", "B", "C"],
        )

        self.regional_diversity = {
            "X": 2.0 / 3.0,
            "Y": 2.0 / 3.0,
            "Z": 0.98 * 0.02 + 0.01 * 0.99 + 0.01 * 0.99,
        }
        self.integration = {"X": 2.0 / 3.0, "Y": 0.0, "Z": 0.03 * (2.0 / 3.0)}

    def test_integration(self):
        """Test integration."""
        df_int = integration(self.df, by="region")

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_segregation(self):
        """Test segregation."""
        df_seg = segregation(self.df, "region")

        for region in df_seg.index:
            self.assertAlmostEqual(
                1.0 - self.integration[region], df_seg.loc[region][0], places=10
            )

    def test_di(self):
        """Test diversity and integration API."""
        df_di = di(self.df, "region")

        for region in df_di.index:
            self.assertAlmostEqual(
                self.integration[region], df_di.loc[region]["integration"], places=10
            )
            self.assertAlmostEqual(
                self.regional_diversity[region],
                df_di.loc[region]["diversity"],
                places=10,
            )


class IntegrationOverTestCase(unittest.TestCase):
    """Test integration over an inne geography."""

    def setUp(self) -> None:
        """Set up before each test."""
        self.df = pd.DataFrame(
            [
                ["X", "X1", 10, 10, 10],
                ["X", "X1", 20, 20, 20],
                ["X", "X1", 30, 30, 30],
                ["X", "X2", 100, 0, 0],
                ["X", "X2", 0, 100, 0],
                ["X", "X2", 0, 0, 100],
                ["Y", "Y1", 10, 0, 0],
                ["Y", "Y1", 20, 0, 0],
                ["Y", "Y1", 30, 0, 0],
                ["Y", "Y2", 0, 10, 0],
                ["Y", "Y2", 0, 20, 0],
                ["Y", "Y2", 0, 30, 0],
                ["Z", "Z1", 20, 0, 0],
                ["Z", "Z1", 15, 0, 0],
                ["Z", "Z1", 25, 0, 0],
                ["Z", "Z1", 37, 0, 0],
                ["Z", "Z2", 1, 1, 1],
            ],
            columns=["region", "subregion", "A", "B", "C"],
        )

        self.regional_diversity = {
            "X": 2.0 / 3.0,
            "Y": 1.0 / 2.0,
            "Z": 0.98 * 0.02 + 0.01 * 0.99 + 0.01 * 0.99,
        }

        self.integration = {"X": 2.0 / 3.0, "Y": 0.0, "Z": 0.03 * (2.0 / 3.0)}

    def test_integration_over(self):
        """Test integration."""
        df_int = integration(self.df, by="region", over="subregion")

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_di_over(self):
        """Test diversity and integration API."""
        df_di = di(self.df, by="region", over="subregion")

        for region in df_di.index:
            self.assertAlmostEqual(
                self.integration[region], df_di.loc[region]["integration"], places=10
            )
            self.assertAlmostEqual(
                self.regional_diversity[region],
                df_di.loc[region]["diversity"],
                places=10,
            )


class IntegrationOverNonNumericTestCase(unittest.TestCase):
    """Test with extra non-numeric columns for different geography levels."""

    def setUp(self) -> None:
        """Set up before each test."""
        self.df = pd.DataFrame(
            [
                ["X", "X1", "X101", 10, 10, 10],
                ["X", "X1", "X101", 20, 20, 20],
                ["X", "X1", "X102", 30, 30, 30],
                ["X", "X2", "X201", 100, 0, 0],
                ["X", "X2", "X202", 0, 100, 0],
                ["X", "X2", "X202", 0, 0, 100],
                ["Y", "Y1", "Y101", 10, 0, 0],
                ["Y", "Y1", "Y102", 20, 0, 0],
                ["Y", "Y1", "Y103", 30, 0, 0],
                ["Y", "Y2", "Y201", 0, 10, 0],
                ["Y", "Y2", "Y201", 0, 20, 0],
                ["Y", "Y2", "Y201", 0, 30, 0],
                ["Z", "Z1", "Z101", 20, 0, 0],
                ["Z", "Z1", "Z102", 15, 0, 0],
                ["Z", "Z1", "Z103", 25, 0, 0],
                ["Z", "Z1", "Z104", 37, 0, 0],
                ["Z", "Z2", "Z201", 1, 1, 1],
            ],
            columns=["region", "subregion", "neighborhood", "A", "B", "C"],
        )

        self.regional_diversity = {
            "X": 2.0 / 3.0,
            "Y": 1.0 / 2.0,
            "Z": 0.98 * 0.02 + 0.01 * 0.99 + 0.01 * 0.99,
        }

        self.integration_region_over_subregion = {
            "X": 2.0 / 3.0,
            "Y": 0.0,
            "Z": 0.03 * (2.0 / 3.0),
        }

        self.integration_region_over_neighborhood = {
            "X": (
                (90.0 / 480.0) * (2.0 / 3.0)
                + (90.0 / 480.0) * (2.0 / 3.0)  # X101
                + (100.0 / 480.0) * 0.0  # X102
                + (200.0 / 480.0) * 0.5  # X201  # X202
            ),
            "Y": 0.0,
            "Z": 0.03 * (2.0 / 3.0),
        }

    def test_integration_region_over_subregion(self):
        """Integration at the region over subregion level."""
        df_int = integration(
            self.df, by="region", over="subregion", drop_non_numeric=True
        )

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration_region_over_subregion[region],
                df_int.loc[region][0],
                places=10,
            )

    def test_di_region_over_subregion(self):
        """Diversity and integration at the region over subregion level."""
        df_di = di(self.df, by="region", over="subregion", drop_non_numeric=True)

        for region in df_di.index:
            self.assertAlmostEqual(
                self.integration_region_over_subregion[region],
                df_di.loc[region]["integration"],
                places=10,
            )
            self.assertAlmostEqual(
                self.regional_diversity[region],
                df_di.loc[region]["diversity"],
                places=10,
            )

    def test_integration_region_over_neighborhood(self):
        """Integration at the region over neighborhood level."""
        df_int = integration(
            self.df, by="region", over="neighborhood", drop_non_numeric=True
        )

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration_region_over_neighborhood[region],
                df_int.loc[region][0],
                places=10,
            )

    def test_di_region_over_neighborhood(self):
        """Diversity and integration at the region over neighborhood level."""
        df_di = di(
            self.df,
            by="region",
            over="neighborhood",
            add_segregation=True,
            drop_non_numeric=True,
        )

        for region in df_di.index:
            self.assertAlmostEqual(
                self.integration_region_over_neighborhood[region],
                df_di.loc[region]["integration"],
                places=10,
            )
            self.assertAlmostEqual(
                1.0 - self.integration_region_over_neighborhood[region],
                df_di.loc[region]["segregation"],
                places=10,
            )
            self.assertAlmostEqual(
                self.regional_diversity[region],
                df_di.loc[region]["diversity"],
                places=10,
            )


if __name__ == "__main__":
    unittest.main()
