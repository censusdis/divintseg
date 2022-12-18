``divintseg``
=============

``divintseg`` is a simple package for computing diversity,
integration, and segregation metrics on data sets.
It is typically used with demographic data such as
census data.

For details on how ``divintseg`` defines diversity,
integration, and segregation, including detailed
examples, please see the `README.md`_ file in the
`divintseg repository`_.

.. _README.md: https://github.com/vengroff/divintseg/blob/main/README.md

.. _divintseg repository: https://github.com/vengroff/divintseg

Installing ``divintseg``
------------------------

Installation follows the typical model for Python::

    pip install divintseg

will install the package in your python environment.

If you are using a tool like `conda <https://docs.conda.io/en/latest/>`_
or `poetry <https://python-poetry.org/>`_ to manage
your dependencies, then you can add ``divitseg`` the
same way you would add any other dependency.

A Motivating Example
--------------------

Consider a set of communities, *W*, *X*, and *Y*. Each has three
demographic groups, whose members are represented below by blue, orange
and green dots.

Community W
"""""""""""

.. image:: _static/n-d-and-s.png
    :height: 240
    :alt: Community W

Community X
"""""""""""

.. image:: _static/n-d-and-i.png
    :height: 240
    :alt: Community X

Community Y
"""""""""""

.. image:: _static/n-d-and-i2.png
    :height: 240
    :alt: Community Y

Intuitively, *W* is diverse, because it has equal numbers
of all three groups, but not at all integrated, because each
of the groups live in entirely different neighborhoods.
*X*, on the other hand, is not only diverse, but integrated.
There are equal numbers of all three groups and they are
equally distributed among the three neighborhoods. What about
*Y*? It is also diverse like *W* and *X*. It looks more
integrated than *W*, but less integrated than *X*.

What happens if we ask ``divinseg``? Here's some code::

    import pandas as pd

    from divintseg import di

    df = pd.DataFrame(
        [
            ['W', 'A', 108, 0, 0],
            ['W', 'B', 0, 108, 0],
            ['W', 'C', 0, 0, 108],

            ['X', 'A', 36, 36, 36],
            ['X', 'B', 36, 36, 36],
            ['X', 'C', 36, 36, 36],

            ['Y', 'A', 36, 36, 36],
            ['Y', 'B', 72, 0, 36],
            ['Y', 'C', 0, 72, 36],
        ],
        columns=['community', 'neighborhood', 'blue', 'green', 'orange'],
    )

    df_di = di(df, by='community', over='neighborhood')


The resulting ``df_di`` is as follows::

               diversity  integration
    community
    W           0.666667     0.000000
    X           0.666667     0.666667
    Y           0.666667     0.518519

As we expected, the overall diversity of the three
communities is the same, ``0.666667``. The integration
of *W* is ``0.000000``, which means there is no
integration at all. That also ties out with what we
expected.

What about *X*'s integration. It is ``0.666667``,
the same as its diversity was. When using ``divintseg``'s
chosen methodology, diversity sets an uppor bound
on integration. So *X*'s integration is as high as it can
possibly be give that its diversity is ``0.666667``.

And finally, *Y*. It also has diversity ``0.666667`` like the
other two. But its integration is ``0.518519``. Unlike *X*,
it did not acheive it's maximum integration potential given
its diversity. That also ties out with what we expect
based on a visual examination of the two.

We haven't gone into any of the math behind how these numbers
are computed, but we have at least shown that they are producing
results that make intuitive sense for the three cases above.
The math behind all of this is explained in the
the `README.md`_ file in the
`divintseg repository`_.

A Second, Less Diverse Example
------------------------------

All of the communities we looked at in the previous section were
quite diverse, though their level of integration clearly differed.
What about some less diverse communities? Consider *Z* and *Q* as
shown here.

Community Z
"""""""""""

.. image:: _static/n-nd-and-mi.png
    :height: 240
    :alt: Community Z


Community Q
"""""""""""

.. image:: _static/n-nd-and-s2.png
    :height: 240
    :alt: Community Q

Neither of these is diverse. The size of the green and orange groups in both
are small at 3 and 7 respectively. But *Z*, where the small green and orange
groups are spread out among the neighborhoods, looks like it is at least
be more integrated (and thus less segregated) than *Q*, where all of the
orange and green groups are in Neighborhood C. Let's run the numbers and
find out::

    df = pd.DataFrame(
        [
            ['Z', 'A', 105, 1, 2],
            ['Z', 'B', 105, 1, 2],
            ['Z', 'C', 104, 1, 3],

            ['Q', 'A', 108, 0, 0],
            ['Q', 'B', 108, 0, 0],
            ['Q', 'C', 98, 3, 7],

        ],
        columns=['community', 'neighborhood', 'blue', 'green', 'orange'],
    )

    df_di = di(df, by='community', over='neighborhood', add_segregation=True)

The result is::

               diversity  integration  segregation
    community
    Q           0.060223     0.057213     0.942787
    Z           0.060223     0.060185     0.939815

This time, we added the ``add_segregation=True`` flag, which gave
us a third column in the result.

As expected, the diversity numbers for *Q* and *Z* are a lot lower
than they were for *X*, *Y*, and *Z*. They are also the same, because
the total size of each of the three groups in the community is the
same in *Q* and *Z*. But, as expected, *Q* is more segregated. It is
also less integrated.

As was the case before with *W*, *X*, and *Y*, neither *Z* nor *Q* has an
integration number greater than its diversity number. Even though in *Z* the
minority groups are spread out, the community as a whole has a low
integration score of ``0.060185``. The maximum it could possibly
achieve is it's diversity score, which is ``0.060223``. So even though the
minority groups are spread out, the fact that *Z* is not diverse means
it has no chance of acheiving the kind of integration scores that *X* and
*Y* did.

Again, the details of the computation are explained in the
the `README.md`_ file in the
`divintseg repository`_.

Additional Uses
===============

We often think of diversity and integration as something we look
at in residential communities, as in the examples above. But it
can be used in other contexts, for example to look at the diversity
and integration of a company. Instead of a community, we look at
a company, and instead of neighborhoods, we look at departments.
A company might be diverse overall, but if all the executive roles
are populated by one demographic group and all the low-level roles
are populated by a different demographic group, it might not be so
integrated.

We can illustrate this with an example. Consider two companies,
WidgetCo and Gadgetly. Each company maintains a database
that assigns each employee to one of twelve demographic groups.
If we summarize the number of employees from each demographic group
in each department, we might get something that looks like::

    import pandas as pd

    df_company_demographics = pd.DataFrame(
        [
            ['WidgetCo', 'Administration', 0, 14, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            ['WidgetCo', 'Engineering', 100, 7, 6, 1, 5, 1, 0, 1, 22, 12, 0, 0],
            ['WidgetCo', 'Executive', 12, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0],
            ['WidgetCo', 'Human Resources', 2, 12, 0, 2, 0, 2, 0, 0, 0, 3, 0, 0],
            ['WidgetCo', 'Legal', 9, 3, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0 ],
            ['WidgetCo', 'Marketing', 5, 19, 0, 0, 0, 1, 0, 0, 0, 4, 0, 0],
            ['WidgetCo', 'Manufacturing', 4, 2, 86, 4, 117, 9, 0, 0, 3, 0, 0, 0],
            ['WidgetCo', 'Sales', 24, 8, 0, 2, 0, 4, 0, 0, 0, 0, 0, 0],

            ['Gadgetly', 'Administration', 1, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            ['Gadgetly', 'Engineering', 22, 3, 1, 0, 0, 0, 0, 0, 12, 3, 0, 0],
            ['Gadgetly', 'Executive', 5, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
            ['Gadgetly', 'Human Resources', 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            ['Gadgetly', 'Legal', 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
            ['Gadgetly', 'Marketing', 1, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            ['Gadgetly', 'Operations', 2, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        ],
        columns=[
            'company', 'department',
            'W-NHL-M', 'W-NHL-F', 'W-HL-M', 'W-HL-F',
            'B-NHL-M', 'B-NHL-F', 'B-HL-M', 'B-HL-F',
            'A-NHL-M', 'A-NHL-F', 'A-HL-M', 'A-HL-F',
        ]
    )

We wrote it as a data frame initialization to make it easy for you to
copy and paste if you want to try the example yourself. The data looks
like::

         company       department  W-NHL-M  W-NHL-F  W-HL-M  W-HL-F  B-NHL-M  B-NHL-F  B-HL-M  B-HL-F  A-NHL-M  A-NHL-F  A-HL-M  A-HL-F
    0   WidgetCo   Administration        0       14       0       0        0        0       0       0        0        1       0       0
    1   WidgetCo      Engineering      100        7       6       1        5        1       0       1       22       12       0       0
    2   WidgetCo        Executive       12        2       0       0        0        0       0       0        3        0       0       0
    3   WidgetCo  Human Resources        2       12       0       2        0        2       0       0        0        3       0       0
    4   WidgetCo            Legal        9        3       0       0        0        0       0       0        2        2       0       0
    5   WidgetCo        Marketing        5       19       0       0        0        1       0       0        0        4       0       0
    6   WidgetCo    Manufacturing        4        2      86       4      117        9       0       0        3        0       0       0
    7   WidgetCo            Sales       24        8       0       2        0        4       0       0        0        0       0       0
    8   Gadgetly   Administration        1        3       0       0        0        1       0       0        0        0       0       0
    9   Gadgetly      Engineering       22        3       1       0        0        0       0       0       12        3       0       0
    10  Gadgetly        Executive        5        1       0       0        0        0       0       0        2        0       0       0
    11  Gadgetly  Human Resources        0        2       0       0        0        0       0       0        0        1       0       0
    12  Gadgetly            Legal        1        1       0       0        0        0       0       0        1        0       0       0
    13  Gadgetly        Marketing        1        3       0       0        0        0       0       0        0        1       0       0
    14  Gadgetly       Operations        2        1       0       1        0        0       0       0        1        0       0       0

Now what happens if we compute the diversity of each company and the
integration of each company over its departments? The code is simply::

    from divintseg import di

    df_company_di = di(df_company_demographics, by='company', over='department')

The result is::

              diversity  integration
    company
    Gadgetly       0.69         0.60
    WidgetCo       0.80         0.55

Taken as a whole company, WidgetCo is more diverse than
Gadgetly, by a score of ``0.80`` to ``0.69``. Gadgetley has lower
diversity in part because there are five
demographic groups of which it has no employees at all, and three
more of which it has only one employee. 

But if we look at integration, a more complex story emerges. WidgetCo
is actually less integrated than Gadgetly. Their integration is much
lower than their diversity. Why? It is because there are demographic
groups whose members are very heavily concentrated in one or two
departments. The company has a lot of different people from different
demographic groups, but many of them see mostly members of their own
group in the department they work in. The company is segregated by
department, not integrated.

Examples like this are why we believe that anywhere we want to look
at diversity we should look at integration too. Otherwise we might
be missing important parts of the story.

.. toctree::
   :maxdepth: 1
   :hidden:

   self
   api.rst

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
