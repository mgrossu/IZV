#!/usr/bin/env python3.8
# coding=utf-8
#Autor: Marius Iustin Grossu xgross10
#Projekt 2 do IZV

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    orig_size = 0
    new_size = 0
    #control if file exists
    if not os.path.isfile(filename):
        print("ERROR: The file does not exists in working directory")
        exit(1)
    
    df_org = pd.read_pickle(filename, compression="gzip")
    
    orig_size = df_org.memory_usage(deep=True).sum()/1048576 

    df_new = df_org.rename({'p2a': 'date'}, axis=1) 

    #changing to type 
    for col in list(df_new.columns):
        if col != "date"  and col != "region":
            df_new[col] = df_new[col].astype("category")
        if col == "date" :
            df_new[col] = pd.to_datetime(df_new[col])
 
    new_size = df_new.memory_usage(deep=True).sum()/1048576
    
    #verbose parameter handling 
    if verbose:
        print("orig_size={:.1f} MB".format(orig_size)) 
        print("new_size={:.1f} MB".format(new_size))
    
    return df_new


# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    #creating a new df with the col needed to visualise data
    df = df[["p1", "p13a", "p13b", "p13c", "region"]]
    df = df.astype({"p13a" : int, "p13b" : int, "p13c" : int})
   
    #creating the df by region with each type of accidents and total number
    all_accidents = pd.DataFrame({"p13a" : df.groupby("region")["p13a"].sum(), 
                                  "p13b" : df.groupby("region")["p13b"].sum(), 
                                  "p13c" : df.groupby("region")["p13c"].sum(), 
                                  "total" : df.groupby("region")["p1"].count()})
    
    #multi-index fix
    all_accidents = all_accidents.reset_index()

    #sorting all the regions by total number of accidents in each region
    total_sort = all_accidents.sort_values(by=["total"], ascending=False)

    #creating the plot 
    sns.set_theme(style="darkgrid")
    fig = plt.figure(constrained_layout=True, figsize=(7,7))
    ax1, ax2, ax3, ax4 = (fig.add_gridspec(nrows=4, ncols=1).subplots())
    sns.barplot(x="region", y="p13a", data=all_accidents, color="red", ax=ax1, order=total_sort["region"])
    sns.barplot(x="region",y="p13b", data=all_accidents, color="orange", ax=ax2, order=total_sort["region"])
    sns.barplot(x="region",y="p13c", data=all_accidents, color="yellow", ax=ax3, order=total_sort["region"])
    sns.barplot(x="region", y="total", data=all_accidents, palette="Greys_r", ax=ax4, order=total_sort["region"])
    #graph with fatal
    ax1.title.set_text('Úmrti')
    ax1.set(xlabel="", ylabel="Počet")
    ax1.spines["top"].set_visible(False) 
    ax1.spines["right"].set_visible(False)
    ax1.axes.xaxis.set_visible(False)
    #graph with severe injuries
    ax2.title.set_text('Těžce ranění')
    ax2.set(xlabel="", ylabel="Počet")
    ax2.spines["top"].set_visible(False) 
    ax2.spines["right"].set_visible(False)
    ax2.axes.xaxis.set_visible(False)
    #graph with easy injuries
    ax3.title.set_text('Lehce ranění')
    ax3.set(xlabel="", ylabel="Počet")
    ax3.spines["top"].set_visible(False) 
    ax3.spines["right"].set_visible(False)
    ax3.axes.xaxis.set_visible(False)
    #graph with total injuries in each region
    ax4.title.set_text('Celkem nehod')
    ax4.set(xlabel="", ylabel="Počet")
    ax4.spines["top"].set_visible(False) 
    ax4.spines["right"].set_visible(False)
    #fig_location handling
    if fig_location is not None:
       fig.savefig(fig_location)
    #show_figure handling
    if show_figure:
       plt.show()

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    #taking the values from df that I will work with
    df = df[["region", "p12", "p53"]]
    df = df.astype({"p53" : float})
    df["p53"] = df["p53"].div(10) 
    #new df with categorizing the values
    df2 = pd.DataFrame({"region" : df.region, "p12" : pd.cut(df.p12, [0, 200, 209, 311, 414, 516, 615], 
                          labels=["nezaviněná řidičem", "nepřiměřená rychlost jízdy", 
                          "nesprávné předjíždění", "nedání přednosti v jízdě", 
                          "nesprávný způsob jízdy", "technická závada vozidla"]), 
                          "p53" : pd.cut(df.p53, [0,50, 200, 500, 1000, float("inf")], 
                         labels=["< 50","50-200", "200-500", "500-1000", "> 1000"], include_lowest=True)})
    print(df2)
    #df for each the region I selected
    df3 = df2[df2["region"].isin(["JHM", "PLK", "ZLK", "KVK"])]
    print(df3)

    #grouping
    df4 = pd.DataFrame({"total" : df3.groupby(["region","p53", "p12"])["region"].count()})


    #print(df4[df4.loc[0,"region"] == "JHM"])

    #creating the plot 
    sns.set_theme(style="darkgrid")
    fig = plt.figure(constrained_layout=True, figsize=(7,7))
    ax1, ax2, ax3, ax4 = sns.catplot(x="p53", hue="p12", col="region", col_wrap= 2 , data=df3, kind="count", legend=True)
    #ax.set(xlabel="Škoda [tisice Kč]", ylabel="Počet")
    #plt.title("{col_name}")
    #g.set_xlabels("Škoda [tisice Kč]")
    #g.set_ylabels("Počet")
    #g.set_axis_labels("Škoda [tisice Kč]", "Počet", labelpad=0.5)
    #g.legend.set_title("Přičina nehody")
    #plt.legend(title="Přičina nehody", bbox_to_anchor=(1.01, 1),borderaxespad=0,fontsize=10)
    
    #g.set(yscale="log")
    #g.fig.set_size_inches(10, 10)
    #g._legend.set_title("Přičina nehody")
    
    #ax.set_yscale("log")
    
    #fig_location handling
    if fig_location is not None:
       fig.savefig(fig_location)
    #show_figure handling
    if show_figure:
       plt.show()

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    pass
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz", verbose=True)
    #plot_conseq(df, fig_location="02_nasledky.png", show_figure=False)
    plot_damage(df, show_figure=True)
    #plot_damage(df, "02_priciny.png", True)
    #plot_surface(df, "03_stav.png", True)