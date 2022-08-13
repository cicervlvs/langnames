import urllib.request as url
import shutil
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

# Download languoid data from glottolog and wals
glottolog_url = "https://cdstar.eva.mpg.de/bitstreams/EAEA0-7EA2-D308-CD6E-0/glottolog_languoid.csv.zip"
langs_zipped = url.urlretrieve(glottolog_url, "data/langs_glot.zip")
shutil.unpack_archive("data/langs_glot.zip", "data/")

wals_url = "https://raw.githubusercontent.com/cldf-datasets/wals/master/cldf/languages.csv"
langs_wals = url.urlretrieve(wals_url, "data/langs_wals.csv")

# Read languoid data into Python
languoid_glottolog = pd.read_csv("data/languoid.csv",
        usecols = ["id",
            "iso639P3code",
            "family_id",
            "level",
            "name"]) 

#get only languages (not dialects or families), and also get rid of langs only kept there for bookkeeping
langs_glottolog = languoid_glottolog.loc[(languoid_glottolog["level"] == "language") &
        (languoid_glottolog["family_id"] != "book1242")]

#get families and their names
fams_glottolog = languoid_glottolog[languoid_glottolog["level"] == "family"]
top_level_fams = fams_glottolog[fams_glottolog["family_id"].isnull()]

#glottolog subsitute family IDs for family names
fams_kv = dict(zip(top_level_fams.id, top_level_fams.name))
langs_glottolog["family"] = langs_glottolog["family_id"].replace(fams_kv).fillna("Isolate")

#wals data
languoid_wals = pd.read_csv("data/langs_wals.csv",
        usecols = [
            "ISO639P3code",
            "Name",
            "Family",
            "Genus"])

# Join with wals for names and codes
