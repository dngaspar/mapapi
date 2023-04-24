import googlemaps
import pandas as pd

# あなたの実際のAPIキーで 'YOUR_API_KEY'を置き換えてください
gmaps = googlemaps.Client(key="AIzaSyCiQyTQ8iblBIaILbDuzS0oURGcn2nGb0c")


def get_walking_time(org_location):
    """
    指定された場所から徒歩15分以内の公共交通機関、主要施設、教育機関、病院などの場所を取得します。

    Parameters:
    org_location (str): 出発地の住所や地名などを表す文字列

    Returns:
    pandas.DataFrame: 取得した場所のカテゴリー、出発地、歩行時間が含まれるデータフレーム
    """
    # 出発地の住所や地名などから緯度・経度を取得します。
    location = gmaps.geocode(org_location)
    assert "Location not found", location
    region_location = location[0]["geometry"]["location"]
    org_latlng = f"{region_location['lat']}, {region_location['lng']}"
    # print(org_latlng)

    # Google Maps Directions APIを使用するためのmodeを設定します。
    mode = "walking"

    # 徒歩15分以内の場所を取得するための歩行時間の最大値を設定します。
    max_walking_time = 15 * 60  # 15分を秒に変換

    # 取得する場所のカテゴリーを設定します。
    queries = ["公共交通機関", "主な施設", "教育機関", "病院"]

    # 取得した場所の情報を格納するための辞書を初期化します。
    result = {
        "カテゴリー": [],
        "出発地": [],
        # "目的地": [],
        "歩行時間": [],
    }

    # カテゴリーごとに場所を取得して、歩行時間が15分以内の場所のみを格納します。
    for query in queries:
        # 一定の半径内のすべての近くの場所を取得します
        places_result = gmaps.places_nearby(
            location=org_latlng, radius=5000, type=query
        )
        for place in places_result["results"]:
            latlng = (
                place["geometry"]["location"]["lat"],
                place["geometry"]["location"]["lng"],
            )
            walking_time_result = gmaps.distance_matrix(
                origins=org_latlng, destinations=latlng, mode=mode
            )
            walking_time = walking_time_result["rows"][0]["elements"][0]["duration"][
                "value"
            ]
            if walking_time <= max_walking_time:
                result["カテゴリー"].append(query)
                result["出発地"].append(place["name"])
                # result["目的地"].append(org_location)
                result["歩行時間"].append(f"{walking_time // 60}分")
                # print(place['name'], walking_time // 60, '分')

    # 結果をデータフレームに変換して返す
    df = pd.DataFrame(result)
    return df


org = "静岡市葵区 西草深町 28-31"
resp_df = get_walking_time(org)
resp_df.to_csv(f"{org}.csv", index=False)
resp_df
