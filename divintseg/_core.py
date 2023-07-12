# Copyright (c) 2022 Darren Erik Vengroff

from typing import Any, Iterable, Mapping, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pandas.api.types


def _diversity_of_df(
    df_communities: pd.DataFrame,
) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the diversity of each row of a dataframe.

    Each row is assumed to be an independent community.

    Parameters
    ----------
    df_communities
        The DataFrame
    Returns
    -------
        A tuple of a series containing the diversity metric for each
        row and a series of the total population of each row.

    """

    # Compute the total population of each row, as
    # a series.
    s_total_population = df_communities.sum(axis="columns", numeric_only=True)

    # Compute the fraction of the population in each
    # group. This is also known as p.
    df_p = df_communities.div(s_total_population, axis="rows")

    # Now let q = 1 - p and compute pq.
    df_pq = df_p * (1 - df_p)

    s_diversity = df_pq.sum(axis=1)
    s_diversity.name = "diversity"

    return s_diversity, s_total_population


def diversity(
    communities: Union[pd.DataFrame, Iterable[float]]
) -> Union[pd.Series, float]:
    """
    Compute the diversity of one or more communities.

    Parameters
    ----------
    communities
        The communities. This is either an iterable over
        the population of each group in the community or,
        more commonly, a :py:class:`~pd.DataFrame` with
        each row representing a community and each column
        representing a group.
    Returns
    -------
        The diversity of the community or, if passed a
        :py:class:`~pd.DataFrame` then a :py:class:`~pd.Series`
        with one entry for the diversity of each community.
    """
    if isinstance(communities, pd.DataFrame):
        return _diversity_of_df(communities)[0]
    else:
        return _diversity_of_df(pd.DataFrame([communities]))[0][0]


def _drop_non_numeric_except(
    df: pd.DataFrame,
    by: Optional[Any],
    over: Optional[Any],
) -> pd.DataFrame:
    """
    A helper function to drop non-numeric columns that
    may be present, e.g. for different political boundaries
    that are not needed for the current diversity or integration
    calculation.

    Parameters
    ----------
    df
        The original dataframe
    by
        What we are grouping by. This column will not be removed.
    over
        What we are computing inner diversity over. This column
        will not be removed.

    Returns
    -------
        The data with non-numeric columns other than `by` and
        `over` removed.
    """
    drop_cols = [
        col
        for col in df.columns
        if (
            not pandas.api.types.is_numeric_dtype(df[col]) and col != by and col != over
        )
    ]

    if len(drop_cols) > 0:
        return df.drop(drop_cols, axis="columns")

    return df


def integration(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the integration of one of more communities
    over a nested level of population aggregation. For
    example, with US census data we might compute integration
    of block groups over blocks.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the integration of
        each community.
    """

    def integration_of_group(df_group: pd.DataFrame) -> float:
        """
        A helper method to compute the integration of each group.
        """
        if over is not None:
            df_group = df_group.groupby(over).sum(numeric_only=True)

        s_div, s_total = _diversity_of_df(df_group)

        # If there is no population, then there is no integration.
        if s_total.sum() == 0:
            return 0.0

        return np.average(s_div, weights=s_total)

    if drop_non_numeric:
        df_communities = _drop_non_numeric_except(df_communities, by, over)

    df_integration = pd.DataFrame(
        df_communities.groupby(by=by).apply(integration_of_group),
        columns=["integration"],
    )

    return df_integration


def segregation(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the segregation of one of more communities
    over a nested level of population aggregation. For
    example, with US census data we might compute integration
    of block groups over blocks.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the segregation of
        each community.
    """

    df_segregation = 1.0 - integration(
        df_communities, by=by, over=over, drop_non_numeric=drop_non_numeric
    )
    df_segregation.columns = ["segregation"]

    return df_segregation


def di(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    add_segregation: bool = False,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the diversity, integration, and optionally
    the segregation of each of a collection of communities.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    add_segregation
        if `True` add a column to the results for
        segregation.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the diversity,
        integration, and optionally the segregation of
        each community.
    """
    if drop_non_numeric:
        df_communities = _drop_non_numeric_except(df_communities, by, over)

    if over is not None:
        df_sum_by = (
            df_communities.drop(over, axis="columns")
            .groupby(by=by)
            .sum(numeric_only=True)
        )
    else:
        df_sum_by = df_communities.groupby(by=by).sum(numeric_only=True)

    df_diversity = diversity(df_sum_by)

    df_integration = integration(df_communities, by=by, over=over)

    df_di = pd.concat([df_diversity, df_integration], axis=1)

    if add_segregation:
        df_di["segregation"] = 1.0 - df_di["integration"]

    return df_di


def dissimilarity(
    df_communities: pd.DataFrame,
    reference: Union[pd.DataFrame, Mapping[str, Union[int, float]]],
) -> pd.Series:
    """
    Compute the dissimilarity index of one or more communities relative to a reference community.

    If you want compute dissimilarity or similarity many times against a
    common reference, then creating at :py:class:`~SimularityReference`
    is a more efficient option.

    Parameters
    ----------
    df_communities
        The communities. This is a :py:class:`~pd.DataFrame` with
        each row representing a community and each column
        representing a group.
    reference
        The reference community. It should be a single row with
        a column with the reference population of each group.
    Returns
    -------
        The dissimilarity index of the each community relative to the reference
        community.
    """
    return SimilarityReference(reference).dissimilarity(df_communities)


def similarity(
    df_communities: pd.DataFrame,
    reference: Union[pd.DataFrame, Mapping[str, Union[int, float]]],
) -> pd.Series:
    """
    Compute the similarity index of one or more communities relative to a reference community.

    Note that similarity is just one minus dissimilarity.

    If you want compute dissimilarity or similarity many times against a
    common reference, then creating at :py:class:`~SimularityReference`
    is a more efficient option.

    Parameters
    ----------
    df_communities
        The communities. This is a :py:class:`~pd.DataFrame` with
        each row representing a community and each column
        representing a group.
    reference
        The reference community. It should be a single row with
        a column with the reference population of each group.
    Returns
    -------
        The similarity of the each community relative to the reference
        community.
    """
    return SimilarityReference(reference).similarity(df_communities)


class SimilarityReference:
    """
    An object that computes dissimilarty from a reference.

    Parameters
    ----------
    reference
        The reference community. It should be a mapping from
        name to count or a dataframe with a single row with
        a column with the reference population of each group.

    """

    def __init__(
        self,
        reference: Union[pd.DataFrame, Mapping[str, Union[int, float]]],
    ):
        if isinstance(reference, pd.DataFrame):
            self._df_reference = reference
        else:
            self._df_reference = pd.DataFrame([reference])

        if len(self._df_reference.index) != 1:
            raise ValueError("Reference community should have a single row.")

        self._reference_total = self._df_reference.sum(axis="columns").iloc[0]
        self._df_reference_fractions = self._df_reference / self._reference_total

    def dissimilarity(
        self,
        df_communities: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the dissimilarity index of one or more communities
        relative to a reference community.

        Parameters
        ----------
        df_communities
            The communities. This is a :py:class:`~pd.DataFrame` with
            each row representing a community and each column
            representing a group.
        Returns
        -------
            The dissimilarity index of the each community relative to the reference
            community.
        """
        community_totals = df_communities.sum(axis="columns")

        df_community_fractions = df_communities.div(community_totals, axis="rows")

        df_abs_differences = abs(
            df_community_fractions.sub(self._df_reference_fractions.iloc[0])
        )

        df_dissimilarity_index = 0.5 * df_abs_differences.sum(axis="columns")

        return df_dissimilarity_index

    def similarity(
        self,
        df_communities: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the representation index of one or more communities.

        If `sim_ref` is a `SimilarityReference`, then `sim_ref.similarity(communities)-
        is equal to `1.0 - sim_ref.similarity(communities)`.

        Parameters
        ----------
        df_communities
            The communities. This is a :py:class:`~pd.DataFrame` with
            each row representing a community and each column
            representing a group.
        Returns
        -------
            The dissimilarity index of the each community relative to the reference
            community.
        """
        return 1.0 - self.dissimilarity(df_communities)


def isolation(
    df_communities: pd.DataFrame,
    group_name: str,
    by: str,
    over: str,
) -> pd.DataFrame:
    """
    Compute the isolation of a group in a community. Isolation is the
    average, over all members of a group in a community, of the proportion
    of the smaller area they reside in that are not members of their group.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    group_name
        The name of the group (name of a column in `df_communities`)
        whose isolation we wish to compute.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.

    Returns
    -------
        A dataframe with one row for each unique value of the `by`
        column indicating the isolation of the `group_name` column
        with respect to all of the other columns in the data frame.

    Examples
    --------

    >>> import pandas as pd
    ...
    ... df = pd.DataFrame(
    ...     [
    ...         ['Region 1', 'Subregion A', 100, 0],
    ...         ['Region 1', 'Subregion B', 50, 50],
    ...         ['Region 2', 'Subregion C', 0, 100],
    ...         ['Region 2', 'Subregion D', 0, 50],
    ...         ['Region 2', 'Subregion E', 10, 90],
    ...     ],
    ...     columns=['REGION', 'SUBREGION', 'S', 'T']
    ... )
    ...
    ... df
         REGION    SUBREGION    S    T
    0  Region 1  Subregion A  100    0
    1  Region 1  Subregion B   50   50
    2  Region 2  Subregion C    0  100
    3  Region 2  Subregion D    0   50
    4  Region 2  Subregion E   10   90

    >>> from divintseg import isolation
    ...
    ... isolation(df, "S", by="REGION", over="SUBREGION")
         REGION        S
    0  Region 1  0.83333
    1  Region 2      0.1

    Let's look at what this example computed. First, we have
    to see how likely each person in group S is to see other
    members of their own group in their subregion. This is as
    follows:

    +----------+-------------+-----------------------+
    | Region   | Subregion   | Likelihood of an S    |
    +==========+=============+=======================+
    | Region 1 | Subregion A | 100 / (100 + 0) = 1.0 |
    +----------+-------------+-----------------------+
    | Region 1 | Subregion B | 50 / (50 + 50) = 0.5  |
    +----------+-------------+-----------------------+
    | Region 2 | Subregion C | 0 / (0 + 100) = 0.0   |
    +----------+-------------+-----------------------+
    | Region 2 | Subregion D | 0 / (0 + 50) = 0.0    |
    +----------+-------------+-----------------------+
    | Region 2 | Subregion E | 10 / (10 + 90) = 0.1  |
    +----------+-------------+-----------------------+

    Next, we can compute the fraction of all S's in
    each subregion of each region. There are 150 S's
    in Region 1 and 10 S's in region 2, therefore, we have:

    +----------+-------------+--------------------------------+
    | Region   | Subregion   | Fraction of all As in Region   |
    +==========+=============+================================+
    | Region 1 | Subregion A | 100 / 150 = 0.6667             |
    +----------+-------------+--------------------------------+
    | Region 1 | Subregion B | 50 / 150 = 0.3333              |
    +----------+-------------+--------------------------------+
    | Region 2 | Subregion C | 0 / 10 = 0.0000                |
    +----------+-------------+--------------------------------+
    | Region 2 | Subregion D | 0 / 10 = 0.0000                |
    +----------+-------------+--------------------------------+
    | Region 2 | Subregion E | 10 / 10 = 1.0000               |
    +----------+-------------+--------------------------------+

    Finally, for each subregion, we multiply these together and
    add them up the values for the subregions in each region.
    For Region 1, we get

    .. math::
        (0.6667 * 1.0) + (0.3333 * 0.5) = 0.8333.

    For Region 2, we get

    .. math::
        0.0 * 0.0 + 0.0 * 0.0 + 1.000 * 0.1 = 0.1.

    Note that the implentation may not do this math exactly as
    specified here, but it will do something equivalent.
    """

    df_grouped = df_communities.groupby([by, over], as_index=False).sum(
        numeric_only=True
    )
    likelihood = df_grouped[group_name] / df_grouped.sum(
        axis="columns", numeric_only=True
    )
    region_population = df_grouped.groupby(by)[group_name].sum(numeric_only=True)
    frac_in_region = df_grouped[group_name] / region_population[
        df_grouped[by]
    ].reset_index(drop=True)
    df_grouped["Product"] = likelihood * frac_in_region
    product_sum = df_grouped.groupby(by)["Product"].sum().reset_index(drop=True)
    final_df = pd.DataFrame(df_communities[by].unique(), columns=[by])
    final_df[group_name] = product_sum
    return final_df
