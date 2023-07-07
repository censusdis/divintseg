import pandas as pd
import divintseg as dis

df = pd.DataFrame(
    [
        ["Region 1", "Subregion A", 100, 0],
        ["Region 1", "Subregion B", 50, 50],
        ["Region 2", "Subregion C", 0, 100],
        ["Region 2", "Subregion D", 0, 50],
        ["Region 2", "Subregion E", 10, 90],
    ],
    columns=["REGION", "SUBREGION", "S", "T"],
)
dis.isolation(df, "S", "REGION", "SUBREGION")
