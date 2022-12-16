# divintseg

`divintseg` is a simple package for computing diversity,
integration, and segregation statistics on data sets.
Typically, it is used with demographic data such as 
census data.

[![Hippocratic License HL3-CL-ECO-EXTR-FFD-LAW-MIL-SV](https://img.shields.io/static/v1?label=Hippocratic%20License&message=HL3-CL-ECO-EXTR-FFD-LAW-MIL-SV&labelColor=5e2751&color=bc8c3d)](https://firstdonoharm.dev/version/3/0/cl-eco-extr-ffd-law-mil-sv.html)

## Methodology

`divintseg` uses a straightforward methodology to
compute its metrics. It is designed to make
mathematical sense and have nice mathematical 
properties, while at the same time remaining 
simple enough that it makes sense to non-technical
people as well.

### Visualizing Diversity, Integration, and Segregation

In order to build up some intuition on what our
metrics are trying to model, it's useful to start
with some visual illustrations of the concepts
the metrics try to capture.

The most basic notion in our methodology is that of a
community that consists of members of different
non-overlapping groups. In order to build a basic
intuition for communities, groups, and the metrics
we will compute on them, we will begin with some visual
representations.

We'll start with a community that, intuitively, looks
both diverse and integrated.

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/d-and-i.png?raw=true)

Each small circle represents an individual. The color
of the circle represents which one of three groups 
they belong to. There are equal numbers of blue,
green, and orange circles, so we would tend to
consider this group to be diverse. Furthermore, the
members of the different groups are spread out
throughout the community so that every individual
has nearby neighbors that are in different groups
than they are. This looks integrated.

In contrast, here is a community that looks diverse
but not integrated.

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/d-and-s.png?raw=true)

Just like the previous community, this community
is diverse. It has an equal number of members of
each group. But it is not integrated. Instead, it
is segregated. Each of the three groups is 
concentrated and most individuals do not have
nearby neighbors of a different group.

Now let's look at some communities that are less diverse.
Here is a non-diverse community. Almost all the 
individuals are in the blue group. 

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/nd-and-ni.png?raw=true)

This is also a segregated community. The few members of
the orange and green groups are all together in one
corner of the community.

Let's look at another community that is also not diverse,
but is at least a little more integrated than the last one.

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/nd-and-mi.png?raw=true)

It is certainly more integrated than the last one, 
but is this community integrated? The few individuals
in the orange and green groups are scattered around,
but there aren't really enough of them to say that the
community is integrated. As we will see when we develop
the math behind our methodology, a community that is
not that diverse cannot really be that integrated either,
no matter how the individuals are distributed.

### From Visuals to Mathematics

We will introduce our metrics one
by one, starting with diversity, then integration,
and finally segregation. Informed by the visuals
above, we'll try to come up with definitions that
make sense and can be translated into mathematical
equations and then into code.


#### Diversity

Let's begin with a working definition of diversity.
We say a community is diverse if an average 
member of the community is likely to encounter 
people who are not members of their group as they 
navigate the community.

Now let's turn that into math. In order to
compute the average chance a member of the 
community encounters someone of a different
group, we will first compute, for each group,
what the chance that a random person from
the entire population comes from a different
group. We will then compute the overall average
across all groups.

Let's start with the population shown here:

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/d-and-s2.png?raw=true)

All three groups are the same size. Let's start
with the blue group. The chance that a randomly
chosen member of the population is a member of
the blue group is thus $1/3$, or 
approximately $0.333$. We'll call this number 
$p$. 

The probability that a member of
the blue group encounters someone of one of the
other two groups when they encounter a random
person from the entire population is 
$1 - p = 2/3$, or approximately $0.667$.

Since all three groups are of the same size,
they all have the same value of $p$. We can
summarize this in a table as follows:

| Group                                   | Representation ($p$) | Chance of Encountering a Member of Another Group ($= 1 - p$) |
|-----------------------------------------|:----------------------:|:--------------------------------------------------------------:|
| <span style="color:blue;">Blue</span>   |       $0.333$        |                           $0.667$                            |
| <span style="color:blue;">Orange</span> |       $0.333$        |                           $0.667$                            |
|  <span style="color:blue;">Green</span> |       $0.333$        |                           $0.667$                            |

If we define the diversity of the population $D$ to be the average chance
of any member of the population encountering a member of another group, then 
in this example it is

$$D = 0.333(0.667) + 0.333(0.667) + 0.333(0.667) = 0.667.$$

Each of the three terms is for one of the three groups, and for 
each of them the fraction of the population in the group is
$0.333$ and the chance of encountering a member of another group
is $0.667$.

Now let's look at another example. It is one of the communities we
looked at above.

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/d-and-i.png?raw=true)

In this example, each of the groups is also exactly one third of
the population of the community, so we have the exact same numbers as before:

| Group                                   | Representation ($p$) | Chance of Encountering a Member of Another Group ($= 1 - p$) |
|-----------------------------------------|:----------------------:|:--------------------------------------------------------------:|
| <span style="color:blue;">Blue</span>   |       $0.333$        |                           $0.667$                            |
| <span style="color:blue;">Orange</span> |       $0.333$        |                           $0.667$                            |
| <span style="color:blue;">Green</span>  |       $0.333$        |                           $0.667$                            |

And again, 

$$D = 0.333(0.667) + 0.333(0.667) + 0.333(0.667) = 0.667.$$

So this community has the same exact diversity as the last one,
though it is clearly more integrated. We'll return to that later.

Finally, let's look at a less diverse community. Again, this is
one we looked at before.

![a community](https://github.com/vengroff/divintseg/blob/main/docs/static/nd-and-ni.png?raw=true)

Let's compute the $p$ for each of the three groups, and then
compute $D$. We'll add a column to our table
where we will compute $p(1-p)$ for each group, and then we 
will sum these up at the bottom of the table to get $D$.

| Group                                   |   $p$   | $1 - p$ | Weighted Representation $p(1-p)$ |
|-----------------------------------------|:---------:|:---------:|:----------------------------------:|
| <span style="color:blue;">Blue</span>   | $0.963$ | $0.037$ |             $0.036$              |
| <span style="color:blue;">Orange</span> | $0.022$ | $0.978$ |             $0.022$              |
| <span style="color:blue;">Green</span>  | $0.015$ | $0.985$ |             $0.015$              |
| Weighted Sum                            ||| $0.073$ |

So this community's diversity is $0.073$. As we would expect
from visual inspection, it is much lower than the diversity of the
previous two communities ($0.667$).

#### Integration

As we saw above, two communities can have the exact same diversity,
but to the eye appear to be very different when it comes to integration.
Integration is all about whether the members of a diverse community
actually do interact, as the definition of diversity assumes they
do, by randomly encountering one another, or if, on the contrary,
they live in segregated neighborhoods within the community in which
they rarely encounter members of other groups.

In order to make this notion of integration a little more formal,
in a way that we can then write math and code to compute it, we will
say that a community is integrated if the average member of the community 
is likely to encounter people who are not members of their 
group as they navigate their local neighborhood within the community.
Another way of putting this is that if the neighborhoods within a 
community are diverse, then the community is integrated. If the community
as a whole is diverse, but none of the neighborhoods in the community
are themselves diverse, then the community is not integrated.
Mathematically speaking, integration is the population-weighted average of 
neighborhood diversity in the community.

Let's look at an example of a community consisting of three neighborhoods
of equal population.

![a community of neighborhoods](https://github.com/vengroff/divintseg/blob/main/docs/static/n-d-and-i.png?raw=true)

We can compute the diversity withing each of the three neighborhoods.
Since each neighborhood has exactly equal numbers of members of each
group, each neighborhood has diversity $D = 0.667$. We get this 
number by doing the exact same kind of calculation we did for the 
diversity of the community with equal members of each group above. 
We just repeat it three times, once for each neighborhood.

Now, let's define $r$ for each neighborhood to be the fraction of
the total population of the community that lives in the neighborhood.
For our current example, $r = 1/3$ for each of the three 
neighborhoods since they are of equal size. 

Knowing $r$ and $D$ for each neighborhood, we can compute the
integration of the community by multiplying the $r$ and $D$ values
together for each neighborhood and summing them up. We do this in the
following table.

| Neighborhood |   $r$   |   $D$   | Weighted Diversity $rD$ |
|--------------|:---------:|:---------:|:-------------------------:|
| A            | $0.333$ | $0.667$ |         $0.222$         |
| B            | $0.333$ | $0.667$ |         $0.222$         |
| C            | $0.333$ | $0.667$ |         $0.222$         |
| Weighted Sum ||| $0.667$ |

So the integration of our community is $I = 0.667$. This is 
exactly the same as the overall diversity of the community.

We won't go into the details here, but one of the consequences
of the way we set up our mathematical definitions of diversity
and integration is that the value of $I$ for a community can
never be more that the value of $D$. That is, $I \le D$ in
all cases. More generally, $I$ and $D$ are also both between
$0$ and $1$, so $0 \le I \le D \le 1$ no matter how our
community and the neighborhoods within it are constructed. No 
matter how big the community is, how big the neighborhoods are,
whether the neighborhoods are all the same size or not, or how
many groups there are, the fundamental relationship 

$$0 \le I \le D \le 1$$

will always hold true.

Now let's look at a community where $I < D$, meaning that 
integration is less than diversity in the community.

![a community of neighborhoods](https://github.com/vengroff/divintseg/blob/main/docs/static/n-d-and-i2.png?raw=true)

If we repeat our calculation of $D$ for each neighborhood and
use that to calculate $I$ again, we get

| Neighborhood |   $r$   |   $D$   | Weighted Diversity $rD$ |
|--------------|:---------:|:---------:|:-------------------------:|
| A            | $0.333$ | $0.667$ |         $0.222$         |
| B            | $0.333$ | $0.444$ |         $0.148$         |
| C            | $0.333$ | $0.444$ |         $0.148$         |
| Weighted Sum ||| $0.519$ |

So $I = 0.519$ for this community. Looking at this community vs. the
previous one, it does appear to be less integrated. Neighborhood A
is diverse, with equal numbers of each of the three groups, but the other
two neighborhoods are less diverse. Each of them is completely lacking
one of the three groups and has unequal numbers of the other two.

So, as far as out math working out to produce $I = 0.519 < D = 0.667$
for this community, things make sense. The way the people in the 
community are divided up into neighborhoods results in integration
being less than the diversity of the community as a whole. This is in
contrast to the previous example where each neighborhood was as diverse
as the whole community, and as a result, $I$ was equal to $D$.

Now let's look at a third example, one in which the diversity of the 
community as a whole was already low, and even the limited diversity
that exists is not shared among the neighborhoods. This should result
in a value of $I$ even lower than the already low value of $D$.

![a community of neighborhoods](https://github.com/vengroff/divintseg/blob/main/docs/static/n-nd-and-s.png?raw=true)

If we do our calculation of $D$ as we did above when we looked at 
this community without the neighborhood boundaries, $D = 0.073$.
Now let's calculate $I$.

| Neighborhood |   $r$   |   $D$   | Weighted Diversity $rD$ |
|--------------|:---------:|:---------:|:-------------------------:|
| A            | $0.333$ | $0.000$ |         $0.000$         |
| B            | $0.333$ | $0.000$ |         $0.000$         |
| C            | $0.333$ | $0.204$ |         $0.068$         |
| Weighted Sum ||| $0.068$ |

Two of the neighborhoods (A and B) have no diversity at all. Neighborhood
C has a little bit. The overall integration of the community is $I = 0.068$,
which is less than the diversity of $D = 0.073$ as we expected.

Finally, just to drive home the point that diversity and integration are
different concepts, let's look at a community with high diversity but
no integration at all.

![a community of neighborhoods](https://github.com/vengroff/divintseg/blob/main/docs/static/n-d-and-s.png?raw=true)

Overall diversity of the community is $D = 0.667$, but if we calculate
$I$ we get

| Neighborhood |   $r$   |   $D$   | Weighted Diversity $rD$ |
|--------------|:---------:|:---------:|:-------------------------:|
| A            | $0.333$ | $0.000$ |         $0.000$         |
| B            | $0.333$ | $0.000$ |         $0.000$         |
| C            | $0.333$ | $0.000$ |         $0.000$         |
| Weighted Sum ||| $0.000$ |

$I = 0$. Despite the community being diverse, it is not integrated at all.

#### Segregation

Segregation is the opposite of integration. Since we know that for
all communities, $0 \le I \le 1$ we simply define segregation as $S = 1 - I$.
We don't generally use $S$ as often as we use $D$ and $I$, since it is
so related to $I$, but for completeness, the `divintseg` library can 
compute it.

## Code Examples

Now that we have gone through the methodology behind `divintseg` at 
length, let's look at some examples of how to use the code itself.

In most cases, data we will want to analyze with `divintseg` will
exist in Pandas DataFrames, or in some other format that is easy
to convert to a DataFrame. We'll use them in our examples.

### Diversity

We begin with some diversity computations.

First, let's start with a very simple example consisting of a single-row
DataFrame with a column for each group. The numbers in the columns represent
the number of people in the community that belong to each group.
The first community we looked at had 108 members of each group. So we could
construct it in code and compute its diversity as follows:

```python
import pandas as pd

from divintseg import diversity

df = pd.DataFrame(
    [[108, 108, 108]],
    columns=['blue', 'green', 'orange']
)

print(diversity(df))
```

This will print 

```text
0    0.666667
Name: diversity, dtype: float64
```

The return value of the call to `diversity(df)` is a pandas Series with a 
single element, the diversity of the single row of `df`. And as we 
would expect, it got the same number we calculated manually above.

Now let's try something a little more advanced, with three neighborhoods
in a community like in our examples above.

```python
import pandas as pd

from divintseg import diversity

df = pd.DataFrame(
    [
        ['A', 36, 36, 36],
        ['B', 36, 36, 36],
        ['C', 36, 36, 36],
    ],
    columns=['neighborhood', 'blue', 'green', 'orange']
)

df.set_index('neighborhood', inplace=True)

print(diversity(df))
```

This time the output is 

```text
neighborhood
A    0.666667
B    0.666667
C    0.666667
Name: diversity, dtype: float64
```

`diversity(df)` calculated the diversity of each row independently.
Again we reproduced some of the same results as we got manually 
above.

Now let's try another example with some different diversity in
different neighborhoods.

```python
import pandas as pd

from divintseg import diversity

df = pd.DataFrame(
    [
        ['A', 36, 36, 36],
        ['B', 72, 0, 36],
        ['C', 0, 72, 36],
    ],
    columns=['neighborhood', 'blue', 'green', 'orange'],
)

df.set_index('neighborhood', inplace=True)

print(diversity(df))
```

Now the output is 

```text
neighborhood
A    0.666667
B    0.444444
C    0.444444
Name: diversity, dtype: float64
```

just as we would expect.

### Integration

Now let's move on to integration. The API is almost as simple
as for diversity, but we have to specify what column or index
represents the neighborhood. 

More generally, since we might
not actually be working with neighborhoods, but with various
other kinds of nested geographic areas. For example, if we 
are working with US Census data, we might be interested in
integration at the block group level computed over the diversity
of the different blocks in the block group. But we might
also want to skip a level in the census hierarchy as compute
the integration of census tracts (groups of multiple block groups)
over diversity down at the block level. The `integration` API
gives us the flexibility to choose how we do this.

Here is an example where we put two communities in the same
DataFrame. The first, community `"X"` has equally diverse
neighborhoods. The second, community `"Y"` has unequally
diverse neighborhoods.

```python
import pandas as pd

from divintseg import integration

df = pd.DataFrame(
    [
        ['X', 'A', 36, 36, 36],
        ['X', 'B', 36, 36, 36],
        ['X', 'C', 36, 36, 36],
        
        ['Y', 'A', 36, 36, 36],
        ['Y', 'B', 72, 0, 36],
        ['Y', 'C', 0, 72, 36],
    ],
    columns=['community', 'neighborhood', 'blue', 'green', 'orange'],
)

print(integration(df, by='community', over='neighborhood'))
```

The two keyword arguments are important. The first `by="community`, tells
the API that we want our results by community. There are two unique communities
in the data, `"X"`, and `"Y"`, so we should get two results. The second keyword,
`over='neigborhood'` tells us what column to use to represent the inner level
of geography at which to compute the diversity numbers that we then aggregate
up to the level specified by the `by=` argument.

The result is 

```text
           integration
community             
X             0.666667
Y             0.518519
```

This again matches the results we computed manually for these example communities
and neighborhoods.

### Diversity, Integration (and Segregation) All at Once

More often than not, we want to compute diversity and integration
for the same communities at the same time. We can do that with a single
API `divintseg.di`. It can also optionally tell us segregation too.
Here is how to use it.

```python
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
        
        ['Z', 'A', 108, 0, 0],
        ['Z', 'B', 108, 0, 0],
        ['Z', 'C', 96, 5, 7],
    ],
    columns=['community', 'neighborhood', 'blue', 'green', 'orange'],
)

print(di(df, by='community', over='neighborhood', add_segregation=True))
```

This gives us everything we would want to know about diversity, 
integration, and segregation in these communities in one output
DataFrame.

```text
           diversity  integration  segregation
community      
W           0.666667     0.000000     1.000000                               
X           0.666667     0.666667     0.333333
Y           0.666667     0.518519     0.481481
Z           0.071997     0.067844     0.932156
```


















