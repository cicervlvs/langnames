import urllib.request as url
import shutil
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
from warnings import simplefilter

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
import re


def langnames():
    # Download languoid data from glottolog and wals
    glottolog_url = "https://cdstar.eva.mpg.de/bitstreams/EAEA0-7EA2-D308-CD6E-0/glottolog_languoid.csv.zip"
    langs_zipped = url.urlretrieve(glottolog_url, "data/langs_glot.zip")
    shutil.unpack_archive("data/langs_glot.zip", "data/")

    wals_url = (
        "https://raw.githubusercontent.com/cldf-datasets/wals/master/cldf/languages.csv"
    )
    langs_wals = url.urlretrieve(wals_url, "data/langs_wals.csv")

    ###Read languoid data into Python
    languoid_glottolog = pd.read_csv(
        "data/languoid.csv",
        usecols=["id", "iso639P3code", "family_id", "level", "name"],
    )

    # get only languages (not dialects or families), and also get rid of langs only kept there for bookkeeping
    langs_glottolog = languoid_glottolog.loc[
        (languoid_glottolog["level"] == "language")
        & (languoid_glottolog["family_id"] != "book1242")
    ].reset_index(drop=True)

    # get families and their names
    fams_glottolog = languoid_glottolog[languoid_glottolog["level"] == "family"]

    # only top level families
    top_level_fams = fams_glottolog[fams_glottolog["family_id"].isnull()]

    # glottolog subsitute family IDs for family names
    fams_kv = dict(zip(top_level_fams.id, top_level_fams.name))
    langs_glottolog["family"] = (
        langs_glottolog["family_id"].replace(fams_kv).fillna("Isolate")
    )

    ###wals data
    langs_wals = pd.read_csv(
        "data/langs_wals.csv", usecols=["ISO639P3code", "Name", "Family"]
    )

    langs_wals["Family"] = langs_wals["Family"].fillna("Isolate")

    # give consistent capitalization with glottolog, and resetting of indexes
    langs_wals = langs_wals.rename(
        columns={"Family": "family", "ISO639P3code": "iso639P3code", "Name": "name"}
    ).reset_index(drop=True)

    # Join with wals for names and codes
    langs = pd.merge(
        langs_wals,
        langs_glottolog,
        on="iso639P3code",
        how="outer",
        suffixes=("_glot", "_wals"),
    ).reset_index(drop=True)

    # filter and reorder
    langs = langs[
        ["iso639P3code", "name_glot", "name_wals", "family_glot", "family_wals"]
    ]

    # get duplicate iso codes
    code_n = langs["iso639P3code"].value_counts()
    duplicate_codes = code_n[code_n > 1].reset_index()

    # get duplicate codes the names of which have parentheses (dialect suspects)
    langs_with_pars = langs[langs.name_glot.str.contains(r" \(", na=False) == True]
    dupes_with_pars = pd.merge(
        langs_with_pars,
        duplicate_codes,
        on="iso639P3code",
        how="inner",
    )

    # get names (without parentheses), as well as number of them
    sus_names = {}
    suspect_pattern = re.compile(r"(.+) \(")

    for name, code in zip(
        dupes_with_pars["name_glot"], dupes_with_pars["iso639P3code"]
    ):
        main_name = suspect_pattern.match(name).group(1)
        if main_name != "":
            sus_names.update({main_name: code})

    # if all the occurrences of one name belong to the same code, I keep the shortest name
    langs = (
        langs.assign(name_len=(langs["name_glot"].str.len()))
        .sort_values("name_len")
        .drop_duplicates(subset=["name_wals", "iso639P3code"], keep="first")
        .sort_values("name_glot")
        .reset_index(drop=True)
        .drop_duplicates(subset=["name_glot", "iso639P3code"], keep="first")
        .reset_index(drop=True)
    )

    # remove entries without iso codes
    langs = langs.dropna(subset="iso639P3code").reset_index(drop=True)

    # fill na in glottolog names with wals names (and vice-versa)
    langs.name_glot = langs.name_glot.fillna("noname_glot")
    langs.name_wals = langs.name_wals.fillna("noname_wals")

    glotnames_fixed = []
    walsnnames_fixed = []
    for glotname, walsname in zip(langs.name_glot, langs.name_wals):
        if glotname == "noname_glot":
            glotname = walsname
        elif walsname == "noname_wals":
            walsname = glotname
        glotnames_fixed.append(glotname)
        walsnnames_fixed.append(walsname)

    langs.name_glot = glotnames_fixed
    langs.name_wals = walsnnames_fixed

    # Fill nan in glottolog families with wals families and viceversa
    glotfams_fixed = []
    walsfams_fixed = []
    for glotfam, walsfam in zip(langs.family_glot, langs.family_wals):
        if pd.isna(glotfam):
            glotfam = walsfam
        elif pd.isna(walsfam):
            walsfam = glotfam
        glotfams_fixed.append(glotfam)
        walsfams_fixed.append(walsfam)

    langs.family_glot = glotfams_fixed
    langs.family_wals = walsfams_fixed

    langs = langs.sort_values("iso639P3code")

    # make the keys for the latex package
    with open("langnames/ln_langs_glot.tex", "w") as lang_keys_glot:
        for name, code in zip(langs.name_glot, langs.iso639P3code):
            lang_keys_glot.write(f"\\def\\langnames@langs@glottolog@{code}{{{name}}}\n")

    with open("langnames/ln_langs_wals.tex", "w") as lang_keys_wals:
        for name, code in zip(langs.name_wals, langs.iso639P3code):
            lang_keys_wals.write(f"\\def\\langnames@langs@wals@{code}{{{name}}}\n")

    with open("langnames/ln_fams_glot.tex", "w") as fam_keys_glot:
        for fam, code in zip(langs.family_glot, langs.iso639P3code):
            fam_keys_glot.write(f"\\def\\langnames@fams@glottolog@{code}{{{fam}}}\n")

    with open("langnames/ln_fams_wals.tex", "w") as fam_keys_wals:
        for fam, code in zip(langs.family_wals, langs.iso639P3code):
            fam_keys_wals.write(f"\\def\\langnames@fams@wals@{code}{{{fam}}}\n")


if __name__ == "__main__":
    langnames()
