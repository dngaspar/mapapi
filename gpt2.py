import time

import googlemaps
import pandas as pd

# カテゴリーを設定
categories = {
    "公共交通機関": ["train_station", "bus_station", "subway_station"],
    "主な施設": ["convenience_store", "bank", "post_office", "gas_station"],
    "教育機関": ["school", "university"],
    "病院": ["hospital", "pharmacy"],
}

# Google Maps APIを利用するためのクライアントを作成
gmaps = googlemaps.Client(key="AIzaSyCiQyTQ8iblBIaILbDuzS0oURGcn2nGb0c")

# エクセルファイルの読み込み
df = pd.read_excel("input.xlsx", sheet_name="駐車場")

# 各カテゴリー毎に検索して情報を取得
for cat_name, cat_types in categories.items():
    for cat_type in cat_types:
        df[cat_name + "_" + cat_type + "_num"] = 0
        df[cat_name + "_" + cat_type + "_name"] = ""
        df[cat_name + "_" + cat_type + "_lat"] = ""
        df[cat_name + "_" + cat_type + "_lng"] = ""
        for i, row in df.iterrows():
            if pd.isnull(row["住所"]):
                continue
            # ジオコーディングして緯度経度を取得
            geocode_result = gmaps.geocode(row["住所"])
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]
            else:
                lat, lng = "", ""
            # キーワード検索して結果を取得
            places_result = gmaps.places_nearby(
                location=location, radius=500, language="ja", type=cat_type
            )
            num_result = min(15, len(places_result["results"]))
            for j in range(num_result):
                df.at[i, cat_name + "_" + cat_type + "_num"] = j + 1
                df.at[i, cat_name + "_" + cat_type + "_name"] += (
                    places_result["results"][j]["name"] + ";"
                )
                df.at[i, cat_name + "_" + cat_type + "_lat"] += (
                    str(places_result["results"][j]["geometry"]["location"]["lat"])
                    + ";"
                )
                df.at[i, cat_name + "_" + cat_type + "_lng"] += (
                    str(places_result["results"][j]["geometry"]["location"]["lng"])
                    + ";"
                )
            time.sleep(3)

# データフレームをエクセルファイルに書き出し
writer = pd.ExcelWriter("output.xlsx")
df.to_excel(writer, sheet_name="駐車場", index=False)
writer.close()
