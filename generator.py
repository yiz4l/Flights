import random
from datetime import datetime, timedelta

def generate_id_number():
    # 地区码（北京市海淀区）
    region_code = "110108"

    # 随机生成一个18岁到60岁之间的生日
    start_date = datetime.now() - timedelta(days=60 * 365)
    end_date = datetime.now() - timedelta(days=18 * 365)
    birth_date = start_date + (end_date - start_date) * random.random()
    birth_date_str = birth_date.strftime("%Y%m%d")

    # 随机生成3位顺序码
    sequence_code = f"{random.randint(0, 999):03d}"

    # 拼接前17位
    id_number_17 = region_code + birth_date_str + sequence_code

    # 计算校验码
    check_code = calculate_check_digit(id_number_17)

    # 返回完整的身份证号
    return id_number_17 + check_code

def calculate_check_digit(id_number_17):
    # 身份证号码校验码的权重
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码对应的值
    check_digits = "10X98765432"

    # 计算校验码
    total = sum(int(id_number_17[i]) * weights[i] for i in range(17))
    check_digit = check_digits[total % 11]
    return check_digit

# 生成身份证号
print(generate_id_number())