# 1. 简单的函数，无参数无返回值
def say_hello():
    print("大家好！")

# 2. 带参数的函数
def greet(name):
    print(f"你好，{name}！")

# 3. 带默认参数的函数
def greet_with_time(name, time="早上"):
    print(f"{time}好，{name}！")

# 4. 带返回值的函数
def calculate_sum(a, b):
    return a + b

# 5. 带多个返回值的函数
def calculate_numbers(a, b):
    sum_result = a + b
    product = a * b
    average = (a + b) / 2
    return sum_result, product, average

# 测试这些函数
print("===== 测试各种函数 =====")

# 测试无参数函数
print("\n1. 调用无参数函数：")
say_hello()

# 测试带参数函数
print("\n2. 调用带参数函数：")
greet("张三")

# 测试带默认参数函数
print("\n3. 调用带默认参数函数：")
greet_with_time("李四")  # 使用默认参数
greet_with_time("王五", "下午")  # 覆盖默认参数

# 测试带返回值函数
print("\n4. 调用带返回值函数：")
result = calculate_sum(5, 3)
print(f"5 + 3 = {result}")

# 测试带多个返回值函数
print("\n5. 调用带多���返回值函数：")
sum_result, product, average = calculate_numbers(4, 6)
print(f"对于数字 4 和 6：")
print(f"和是：{sum_result}")
print(f"积是：{product}")
print(f"平均值是：{average}")

# 等待用户按回车键退出
input("\n按回车键退出程序...") 