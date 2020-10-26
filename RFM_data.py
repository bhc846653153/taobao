import pandas as pd
import datetime

data = pd.read_csv("data/user_log.csv")

data["time"] = data.apply(lambda item: "2015-"+str(item["month"])+"-"+str(item["day"]),axis=1)
data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d")
data["r_value_single"] = data["time"].apply(lambda x:(datetime.datetime.strptime("2015-11-11", "%Y-%m-%d")-x).days)

r_value = data.groupby(["user_id"]).r_value_single.min()
f_value = data.groupby(["user_id"]).size()

rfm_df = pd.concat([r_value, f_value], join='outer', axis=1)
rfm_df.columns = ["r_value", "f_value"]

rfm_df["user_id"] = rfm_df.index
rfm_df["r_score"] = (rfm_df['r_value'] > rfm_df["r_value"].mean())*1
rfm_df["f_score"] = (rfm_df['f_value'] > rfm_df["f_value"].mean())*1

def put_label(item):
    return str(item["r_score"])+str(item["f_score"])

rfm_df["class_index"] = rfm_df.apply(put_label, axis=1)
def transform_user_class(x):
    if x == "11":
        user_label = "重要价值用户"
    elif x == "01":
        user_label = "消费潜力用户"
    return user_label


rfm_df["user_class"] = rfm_df["class_index"].apply(transform_user_class)
new_data = data.merge(rfm_df["user_class"], on='userid', how='inner')

print(new_data)