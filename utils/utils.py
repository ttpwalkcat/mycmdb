# -*- coding: utf-8 -*-
from datetime import datetime

# 判断日期类型数据是否合法,并将 string 类型的日期转换为 date 类型
def date_checker(date):
    if date == "":
        format_date = None
    elif date:
        try:
            format_date = datetime.strptime(date, '%Y-%m-%d')
        except Exception as e:
            msg = "日期格式错误，请重新输入('YYYY-MM-DD'): %s" % e
            return msg
    else:
        msg = "请输入日期('YYYY-MM-DD')"
        return msg
    return format_date
