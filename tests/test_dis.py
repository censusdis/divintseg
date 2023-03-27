# Copyright (c) 2022 Darren Erik Vengroff

import unittest

import pandas as pd

import divintseg as dis


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
        s_diversity = dis.diversity(self.df)

        self.assertAlmostEqual(2.0 / 3.0, s_diversity[0], places=10)
        self.assertAlmostEqual(1.0 / 2.0, s_diversity[1], places=10)
        self.assertEqual(0.0, s_diversity[2])

        self.assertAlmostEqual(
            0.98 * 0.02 + 0.01 * 0.99 + 0.01 * 0.99, s_diversity[3], places=10
        )

    def test_diversity_of_sub_df(self):
        """Test diversity of a subset of the columns of a dataframe."""
        s_diversity = dis.diversity(self.df[["A", "C"]])

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
        div = dis.diversity(self.a)

        self.assertAlmostEqual(self.div, div, places=10)

    def test_series(self):
        """Test diversity of a pandas Series."""
        s = pd.Series(self.a)

        div = dis.diversity(s)

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
        df_int = dis.integration(self.df, by="region")

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_integration_drop(self):
        """Test integration dropping other cols."""
        self.df["country"] = "QQQ"

        df_int = dis.integration(self.df, by="region", drop_non_numeric=True)

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_integration_drop_nothing(self):
        """Test integration dropping other cols when there are none to drop."""
        df_int = dis.integration(self.df, by="region", drop_non_numeric=True)

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_segregation(self):
        """Test segregation."""
        df_seg = dis.segregation(self.df, "region")

        for region in df_seg.index:
            self.assertAlmostEqual(
                1.0 - self.integration[region], df_seg.loc[region][0], places=10
            )

    def test_di(self):
        """Test diversity and integration API."""
        df_di = dis.di(self.df, "region")

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
        df_int = dis.integration(self.df, by="region", over="subregion")

        for region in df_int.index:
            self.assertAlmostEqual(
                self.integration[region], df_int.loc[region][0], places=10
            )

    def test_di_over(self):
        """Test diversity and integration API."""
        df_di = dis.di(self.df, by="region", over="subregion")

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
        df_int = dis.integration(
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
        df_di = dis.di(self.df, by="region", over="subregion", drop_non_numeric=True)

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
        df_int = dis.integration(
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
        df_di = dis.di(
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


class ZeroPopulationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        """Set up before each test."""
        self.df = pd.DataFrame(
            [
                ["X", "X1", 10, 10, 10],
                ["X", "X1", 20, 20, 20],
                ["X", "X1", 30, 30, 30],
                ["X", "X2", 0, 0, 0],
                ["X", "X2", 0, 0, 0],
                ["X", "X2", 0, 0, 0],
            ],
            columns=["region", "subregion", "A", "B", "C"],
        )

    def testDiversity(self):
        df_di = dis.di(self.df, by="subregion", over="region")

        df_expected = pd.DataFrame(
            [
                ["X1", 2.0 / 3.0, 2.0 / 3.0],
                ["X2", 0.0, 0.0],
            ],
            columns=["subregion", "diversity", "integration"],
        )
        df_expected = df_expected.set_index("subregion")

        self.assertTrue((df_expected == df_di).any().any())


class DissimilarityTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.df_reference = pd.DataFrame(
            [[10.0, 20.0, 30.0, 40.0]], columns=["A", "B", "C", "D"]
        )

    def test_self_dissimilarity(self):
        """A population should be perfectly similar to itself."""
        self_dissimilarity = dis.dissimilarity(self.df_reference, self.df_reference)

        self.assertEqual(1, len(self_dissimilarity))
        self.assertEqual(0.0, self_dissimilarity.iloc[0])

    def test_similar(self):
        """Test perfect similarity."""
        # A smaller community with exactly the same ratios.
        df_similar = self.df_reference * 0.5

        dissimilarity_index = dis.dissimilarity(df_similar, self.df_reference)

        self.assertEqual(1, len(dissimilarity_index))
        self.assertEqual(0.0, dissimilarity_index.iloc[0])

    def test_one_group(self):
        """Test when all of the population is in a single group."""
        reference_total = self.df_reference.sum(axis="columns").iloc[0]

        # Try the non-zero value in each possible position.

        for ii in range(len(self.df_reference.columns)):
            # Doesn't matter how many are in the constant-sized
            # population.
            df_test = pd.DataFrame(
                [
                    ([0] * ii)
                    + [test_population]
                    + ([0] * (len(self.df_reference.columns) - ii - 1))
                    for test_population in range(1, 10)
                ],
                columns=self.df_reference.columns,
            )

            dissimilarity_index = dis.dissimilarity(df_test, self.df_reference)

            # The error is based on the fraction of the
            # reference population in the chosen column.
            # It does not matter what the total test
            # population was. It was just in one group (ii).
            for kk in range(9):
                self.assertAlmostEqual(
                    1.0 - self.df_reference.iloc[0, ii] / reference_total,
                    dissimilarity_index.iloc[kk],
                    places=10,
                )


class DissimilarityCensusTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.us = dict(
            B03002_003E=196251375,
            B03002_004E=39994653,
            B03002_005E=2075852,
            B03002_006E=18184182,
            B03002_007E=550080,
            B03002_008E=1017604,
            B03002_010E=827762,
            B03002_011E=8306780,
            B03002_013E=33709438,
            B03002_014E=1232731,
            B03002_015E=612762,
            B03002_016E=237455,
            B03002_017E=61324,
            B03002_018E=15766310,
            B03002_020E=6001045,
            B03002_021E=1739955,
        )

        self.df_us = pd.DataFrame([self.us])

        self.expected_dissimilarity = pd.Series(
            [
                0.720327,
                0.351581,
                0.815910,
                0.805025,
                0.839579,
            ]
        )

    def test_one_group_only(self):
        total = sum(self.us.values())
        for k, v in self.us.items():
            frac = v / total
            homogenous = {key: 100 if key == k else 0 for key in self.us.keys()}
            similarity = dis.similarity(self.df_us, homogenous)
            print(frac, k, similarity)

    def test_tract(self):
        df_tract = pd.DataFrame(
            [
                dict(
                    STATE="28",
                    COUNTY="049",
                    TRACT="010103",
                    B03002_003E=722,
                    B03002_004E=3919,
                    B03002_005E=0,
                    B03002_006E=8,
                    B03002_007E=0,
                    B03002_008E=0,
                    B03002_010E=0,
                    B03002_011E=1,
                    B03002_013E=0,
                    B03002_014E=0,
                    B03002_015E=0,
                    B03002_016E=0,
                    B03002_017E=0,
                    B03002_018E=0,
                    B03002_020E=0,
                    B03002_021E=0,
                ),
                dict(
                    STATE="28",
                    COUNTY="049",
                    TRACT="010104",
                    B03002_003E=1053,
                    B03002_004E=1023,
                    B03002_005E=0,
                    B03002_006E=8,
                    B03002_007E=0,
                    B03002_008E=0,
                    B03002_010E=0,
                    B03002_011E=0,
                    B03002_013E=74,
                    B03002_014E=0,
                    B03002_015E=0,
                    B03002_016E=0,
                    B03002_017E=0,
                    B03002_018E=0,
                    B03002_020E=0,
                    B03002_021E=0,
                ),
                dict(
                    STATE="28",
                    COUNTY="049",
                    TRACT="010201",
                    B03002_003E=171,
                    B03002_004E=3029,
                    B03002_005E=31,
                    B03002_006E=0,
                    B03002_007E=0,
                    B03002_008E=0,
                    B03002_010E=0,
                    B03002_011E=0,
                    B03002_013E=0,
                    B03002_014E=8,
                    B03002_015E=0,
                    B03002_016E=0,
                    B03002_017E=0,
                    B03002_018E=0,
                    B03002_020E=0,
                    B03002_021E=0,
                ),
                dict(
                    STATE="28",
                    COUNTY="049",
                    TRACT="010202",
                    B03002_003E=318,
                    B03002_004E=4797,
                    B03002_005E=14,
                    B03002_006E=12,
                    B03002_007E=0,
                    B03002_008E=0,
                    B03002_010E=0,
                    B03002_011E=31,
                    B03002_013E=0,
                    B03002_014E=0,
                    B03002_015E=0,
                    B03002_016E=0,
                    B03002_017E=0,
                    B03002_018E=0,
                    B03002_020E=0,
                    B03002_021E=0,
                ),
                dict(
                    STATE="28",
                    COUNTY="049",
                    TRACT="010203",
                    B03002_003E=85,
                    B03002_004E=2341,
                    B03002_005E=0,
                    B03002_006E=0,
                    B03002_007E=0,
                    B03002_008E=14,
                    B03002_010E=0,
                    B03002_011E=0,
                    B03002_013E=0,
                    B03002_014E=0,
                    B03002_015E=0,
                    B03002_016E=0,
                    B03002_017E=0,
                    B03002_018E=0,
                    B03002_020E=0,
                    B03002_021E=0,
                ),
            ]
        )
        leaves = [col for col in df_tract.columns if col.startswith("B03002")]

        # Try with both a dictionary and a dataframe.
        for reference in (self.us, self.df_us):
            dissimilarity = dis.dissimilarity(
                df_communities=df_tract[leaves], reference=reference
            )

            for ds1, ds2 in zip(self.expected_dissimilarity, dissimilarity):
                self.assertAlmostEqual(ds1, ds2, places=5)

            similarity = dis.similarity(
                df_communities=df_tract[leaves], reference=reference
            )

            for ds1, sim in zip(self.expected_dissimilarity, similarity):
                self.assertAlmostEqual(1.0 - ds1, sim, places=5)


if __name__ == "__main__":
    unittest.main()
