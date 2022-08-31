'''
This is calculator in python language
'''

num1 = int(input("Enter 1st no: "))
operator = input('Enter any operator: ')
num2 = int(input('Enter 2nd no: '))

if operator == '+':
    print(num1 + num2)
elif operator == '-':
    print(num1 - num2)
elif operator == '*':
    print(num1 * num2)
else:
    print("Operator is invalid")
