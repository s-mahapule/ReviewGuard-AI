def generate_overview_insight(df):
    fake_ratio = df['model_label'].mean() * 100
    avg_rating = df['rating'].mean()

    return f"""
⚠️ **{fake_ratio:.1f}% of reviews are likely fake.**

This artificially inflates ratings to **{avg_rating:.2f}★**, 
creating a misleading perception of product quality.

👉 If unchecked, this can significantly distort buyer decisions and platform trust.
"""

def generate_category_insight(category_df, category_name):
    fake_ratio = category_df['model_label'].mean() * 100
    inflation = category_df['rating'].mean() - category_df[category_df['model_label']==0]['rating'].mean()

    return f"""
**{category_name}** shows **{fake_ratio:.1f}% fake reviews**, causing a rating inflation of **{inflation:.2f}★**.
This suggests strong manipulation of customer perception in this category.
"""